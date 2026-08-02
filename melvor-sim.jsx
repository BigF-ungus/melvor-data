import React, { useState, useEffect, useMemo, useRef } from "react";

/* ============================================================
   TICK ENGINE
   Melvor resolves on a 50ms tick (20/sec) — confirmed against the
   reference simulator. All timers below are in ticks, never seconds.
   ============================================================ */
const TICK_MS = 50;
const TPS = 1000 / TICK_MS;

const CT_DMG = {
  melee:  { melee: 1.0,  ranged: 1.1,  magic: 0.85 },
  ranged: { melee: 0.85, ranged: 1.0,  magic: 1.1 },
  magic:  { melee: 1.1,  ranged: 0.85, magic: 1.0 },
};
const CT_DR = {
  melee:  { melee: 1.0,  ranged: 1.25, magic: 0.75 },
  ranged: { melee: 0.95, ranged: 1.0,  magic: 1.25 },
  magic:  { melee: 1.25, ranged: 0.85, magic: 1.0 },
};

const msToTicks = (ms) => Math.max(1, Math.round(ms / TICK_MS));

function hitChance(acc, eva) {
  if (acc <= 0) return 0;
  if (eva <= 0) return 1;
  return acc < eva ? acc / (2 * eva) : 1 - eva / (2 * acc);
}

function meleeRangedMaxHit(level, strengthBonus) {
  return Math.floor(10 * (2.2 + level / 10 + ((level + 17) * strengthBonus) / 640));
}

function evasionRating(level, bonus) {
  return Math.floor((level + 9) * (bonus + 64));
}

function accuracyRating(level, bonus) {
  return Math.floor((level + 9) * (bonus + 64));
}

/* Resolve one special attack's damage. Mirrors the structure verified
   against the game data: an inner attackCount on a damage component is a
   HIT INDEX, not a multiplier. */
function specialDamage(spec, ctx) {
  const comps = spec.damage || [];
  const perHitIndexed = comps.some((c) => "attackCount" in c);
  const outer = spec.attackCount || 1;
  let total = 0;
  let unmodelled = false;

  for (const c of comps) {
    if (c.damageType === "Normal") {
      if (c.amplitude == null) { unmodelled = true; continue; }
      total += ctx.avgNormal * (c.amplitude / 100);
    } else {
      const roll = c.maxRoll;
      const pct = c.maxPercent ?? 0;
      if (roll === "MaxHit") total += ctx.maxHit * (pct / 100);
      else if (roll === "Fixed") total += pct * 10;
      else if (roll === "MaxHP") total += ctx.targetMaxHP * (pct / 100);
      else if (roll === "CurrentHP") {
        const hi = ctx.selfHP * (pct / 100);
        const lo = ctx.selfHP * ((c.minPercent ?? pct) / 100);
        total += (hi + lo) / 2;
      } else unmodelled = true;
    }
  }
  if (!perHitIndexed) total *= outer;
  return { damage: total, unmodelled };
}

/* One combatant's per-tick state. */
function makeActor(cfg) {
  return {
    ...cfg,
    hp: cfg.maxHP,
    attackTimer: msToTicks(cfg.attackIntervalMs),
    stacks: 0,
  };
}

function rollDamage(actor, target, rng, log) {
  const style = actor.style;
  const dmgMult = CT_DMG[style][target.style];
  const drMult = CT_DR[target.style][style];
  const effDR = Math.min(95, Math.max(0, Math.floor(target.damageReduction * drMult)));

  const eva = target.evasion[style] ?? 0;
  const hc = hitChance(actor.accuracy, eva);
  const avgNormal = (actor.maxHit + actor.minHit) / 2;

  // choose special vs normal
  let chosen = null;
  let roll = rng() * 100;
  for (const s of actor.specials || []) {
    if (roll < s.defaultChance) { chosen = s; break; }
    roll -= s.defaultChance;
  }

  let raw = 0;
  let unmodelled = false;
  if (chosen) {
    const r = specialDamage(chosen, {
      avgNormal, maxHit: actor.maxHit,
      targetMaxHP: target.maxHP, selfHP: actor.hp,
    });
    unmodelled = r.unmodelled;
    const lands = chosen.cantMiss || rng() < hc;
    raw = lands ? r.damage : 0;
    if (chosen.canNormalAttack) {
      raw += (rng() < hc) ? (actor.minHit + rng() * (actor.maxHit - actor.minHit)) : 0;
    }
  } else {
    raw = (rng() < hc) ? (actor.minHit + rng() * (actor.maxHit - actor.minHit)) : 0;
  }

  const dealt = Math.floor(raw * dmgMult * (1 - effDR / 100));
  if (unmodelled) log.unmodelled = true;
  return dealt;
}

/* Run N trials against a single target. Returns distribution stats. */
function simulate({ player, enemy, trials = 1000, tickLimit = 20000, seed = 12345 }) {
  let s = seed >>> 0;
  const rng = () => {
    s ^= s << 13; s >>>= 0;
    s ^= s >> 17;
    s ^= s << 5; s >>>= 0;
    return s / 4294967296;
  };

  let kills = 0, deaths = 0, totalTicks = 0, foodEaten = 0;
  let lowestHP = player.maxHP;
  let highestTaken = 0;
  const log = { unmodelled: false };
  const killTimes = [];

  const aeThreshold = player.autoEat.threshold / 100;
  const aeLimit = player.autoEat.limit / 100;
  const aeEfficiency = player.autoEat.efficiency / 100;

  let p = makeActor(player);

  while (kills + deaths < trials && totalTicks < tickLimit * trials) {
    let e = makeActor(enemy);
    let fightTicks = 0;
    let spawn = msToTicks(3000); // 3s respawn built into the cycle

    while (spawn > 0) { spawn--; totalTicks++; fightTicks++; }

    while (e.hp > 0 && p.hp > 0 && fightTicks < tickLimit) {
      totalTicks++; fightTicks++;
      p.attackTimer--; e.attackTimer--;

      if (p.attackTimer <= 0) {
        e.hp -= rollDamage(p, e, rng, log);
        p.attackTimer = msToTicks(p.attackIntervalMs);
        if (p.lifesteal) p.hp = Math.min(p.maxHP, p.hp + Math.floor(p.maxHit * p.lifesteal / 100));
      }
      if (e.hp <= 0) break;

      if (e.attackTimer <= 0) {
        const taken = rollDamage(e, p, rng, log);
        p.hp -= taken;
        if (taken > highestTaken) highestTaken = taken;
        e.attackTimer = msToTicks(e.attackIntervalMs);
      }

      if (p.hp < lowestHP) lowestHP = Math.max(0, p.hp);

      // Auto Eat: fires when below threshold, heals to limit
      if (p.hp > 0 && p.hp < p.maxHP * aeThreshold) {
        const target = p.maxHP * aeLimit;
        const healed = (target - p.hp) * aeEfficiency;
        p.hp = Math.min(p.maxHP, p.hp + healed);
        foodEaten++;
      }
    }

    if (p.hp <= 0) {
      deaths++;
      p = makeActor(player); // death resets
    } else if (e.hp <= 0) {
      kills++;
      killTimes.push(fightTicks);
    } else {
      break; // tick limit hit mid-fight
    }
  }

  const seconds = totalTicks / TPS;
  const trialsRun = kills + deaths;
  const avgKillTicks = killTimes.length
    ? killTimes.reduce((a, b) => a + b, 0) / killTimes.length : 0;

  return {
    kills, deaths, trialsRun,
    deathRate: trialsRun ? deaths / trialsRun : 0,
    killTimeS: avgKillTicks / TPS,
    killsPerHour: seconds > 0 ? (kills / seconds) * 3600 : 0,
    foodPerHour: seconds > 0 ? (foodEaten / seconds) * 3600 : 0,
    lowestHP, highestTaken,
    hasUnmodelled: log.unmodelled,
    seconds,
  };
}

/* ============================================================
   DATA LOADING
   ============================================================ */
const REPO = "https://raw.githubusercontent.com/BigF-ungus/melvor-data/main/";
const DATA_FILES = ["melvorDemo.json", "melvorFull.json", "melvorTotH.json", "melvorExpansion2.json"];

const CONSOLE_SNIPPET = `(() => {
  const p = game.combat.player, s = p.stats;
  const m = (k) => { try { return game.modifiers[k] ?? 0 } catch(e){ return 0 } };
  const out = {
    name: game.characterName,
    levels: Object.fromEntries(game.skills.allObjects.map(k => [k.id.split(':').pop(), k.level])),
    maxHP: p.stats.maxHitpoints ?? p.maxHitpoints,
    style: p.attackType,
    maxHit: s.maxHit, minHit: s.minHit,
    accuracy: s.accuracy,
    evasion: { melee: s.evasion?.melee, ranged: s.evasion?.ranged, magic: s.evasion?.magic },
    attackIntervalMs: s.attackInterval,
    damageReduction: p.stats.damageReduction ?? m('damageReduction'),
    lifesteal: m('lifesteal'),
    autoEat: {
      threshold: m('autoEatThreshold'),
      efficiency: m('autoEatEfficiency'),
      limit: m('autoEatHPLimit'),
    },
    equipped: p.equipment.equippedArray.filter(x=>x.providesStats).map(x=>x.item.id),
  };
  copy(JSON.stringify(out));
  console.log('Copied to clipboard. Paste into the simulator.', out);
})()`;

/* ============================================================
   UI
   ============================================================ */
export default function MelvorSim() {
  const [data, setData] = useState(null);
  const [loadState, setLoadState] = useState("loading");
  const [loadErr, setLoadErr] = useState("");
  const [charJSON, setCharJSON] = useState("");
  const [char, setChar] = useState(null);
  const [charErr, setCharErr] = useState("");
  const [targetId, setTargetId] = useState("");
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [filter, setFilter] = useState("");
  const [showSnippet, setShowSnippet] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const parts = await Promise.all(
          DATA_FILES.map((f) => fetch(REPO + f).then((r) => {
            if (!r.ok) throw new Error(`${f}: ${r.status}`);
            return r.json();
          }))
        );
        const monsters = {}, attacks = {}, dungeons = {};
        for (const part of parts) {
          const ns = part.namespace;
          for (const m of part.data.monsters || []) monsters[`${ns}:${m.id}`] = { ...m, _ns: ns };
          for (const a of part.data.attacks || []) attacks[`${ns}:${a.id}`] = a;
          for (const d of part.data.dungeons || []) dungeons[`${ns}:${d.id}`] = { ...d, _ns: ns };
        }
        setData({ monsters, attacks, dungeons });
        setLoadState("ready");
      } catch (e) {
        setLoadErr(String(e.message || e));
        setLoadState("error");
      }
    })();
  }, []);

  function importChar() {
    setCharErr("");
    try {
      const c = JSON.parse(charJSON);
      if (!c.maxHit && c.maxHit !== 0) throw new Error("No maxHit found — is this the full snippet output?");
      setChar(c);
    } catch (e) {
      setCharErr(String(e.message || e));
      setChar(null);
    }
  }

  const monsterList = useMemo(() => {
    if (!data) return [];
    return Object.entries(data.monsters)
      .map(([id, m]) => ({
        id,
        name: m.name,
        hp: (m.levels?.Hitpoints ?? 0) * 10,
        style: m.attackType,
        levels: m.levels,
        stats: Object.fromEntries((m.equipmentStats || []).map((e) => [e.key, e.value])),
        specials: (m.specialAttacks || []).map((s) => data.attacks[s]).filter(Boolean),
      }))
      .filter((m) => m.hp > 0)
      .sort((a, b) => a.hp - b.hp);
  }, [data]);

  const filtered = useMemo(() => {
    const f = filter.trim().toLowerCase();
    return f ? monsterList.filter((m) => m.name.toLowerCase().includes(f)) : monsterList;
  }, [monsterList, filter]);

  function buildEnemy(m) {
    const lv = m.levels || {};
    const st = m.stats || {};
    const style = m.style || "melee";
    let acc, maxHit;
    if (style === "melee") {
      acc = accuracyRating(lv.Attack ?? 1, st.meleeAttackBonus ?? 0);
      maxHit = meleeRangedMaxHit(lv.Strength ?? 1, st.meleeStrengthBonus ?? 0);
    } else if (style === "ranged") {
      acc = accuracyRating(lv.Ranged ?? 1, st.rangedAttackBonus ?? 0);
      maxHit = meleeRangedMaxHit(lv.Ranged ?? 1, st.rangedStrengthBonus ?? 0);
    } else {
      const effDef = Math.floor(0.3 * (lv.Defence ?? 1) + 0.7 * (lv.Magic ?? 1));
      acc = accuracyRating(lv.Magic ?? 1, st.magicAttackBonus ?? 0);
      maxHit = meleeRangedMaxHit(lv.Magic ?? 1, st.magicDamageBonus ?? 0);
      m._effDef = effDef;
    }
    const effDef = Math.floor(0.3 * (lv.Defence ?? 1) + 0.7 * (lv.Magic ?? 1));
    return {
      name: m.name, style, maxHP: m.hp, minHit: 1, maxHit, accuracy: acc,
      attackIntervalMs: st.attackSpeed ?? 3000,
      damageReduction: st.damageReduction ?? 0,
      evasion: {
        melee: evasionRating(lv.Defence ?? 1, st.meleeDefenceBonus ?? 0),
        ranged: evasionRating(lv.Defence ?? 1, st.rangedDefenceBonus ?? 0),
        magic: evasionRating(effDef, st.magicDefenceBonus ?? 0),
      },
      specials: m.specials || [],
      lifesteal: 0,
    };
  }

  function run() {
    if (!char || !targetId) return;
    setRunning(true);
    setTimeout(() => {
      const m = monsterList.find((x) => x.id === targetId);
      const enemy = buildEnemy(m);
      const player = {
        style: char.style || "melee",
        maxHP: char.maxHP,
        minHit: char.minHit ?? 1,
        maxHit: char.maxHit,
        accuracy: char.accuracy,
        attackIntervalMs: char.attackIntervalMs ?? 3000,
        damageReduction: char.damageReduction ?? 0,
        lifesteal: char.lifesteal ?? 0,
        evasion: char.evasion || { melee: 0, ranged: 0, magic: 0 },
        specials: [],
        autoEat: {
          threshold: char.autoEat?.threshold ?? 0,
          efficiency: char.autoEat?.efficiency ?? 100,
          limit: char.autoEat?.limit ?? 0,
        },
      };
      setResult({ ...simulate({ player, enemy, trials: 1000 }), enemy, player });
      setRunning(false);
    }, 10);
  }

  const S = styles;

  return (
    <div style={S.page}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        .tickrule { background-image: repeating-linear-gradient(90deg, #C9D2DC 0 1px, transparent 1px 8px); }
        button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
          outline: 2px solid #3A5FCD; outline-offset: 2px;
        }
        .row:hover { background: #E4E9EF; }
      `}</style>

      <header style={S.header}>
        <div>
          <div style={S.eyebrow}>50ms tick engine · Melvor Realm · Standard</div>
          <h1 style={S.h1}>Combat Simulator</h1>
        </div>
        <div style={S.loadPill(loadState)}>
          {loadState === "loading" && "loading game data…"}
          {loadState === "ready" && `${Object.keys(data.monsters).length} monsters loaded`}
          {loadState === "error" && "data load failed"}
        </div>
      </header>
      <div className="tickrule" style={S.rule} />

      {loadState === "error" && (
        <div style={S.error}>
          Couldn't reach the data repo: {loadErr}
          <div style={S.errorSub}>
            Check that <code>melvor-data</code> is public and the four game data files are in the repo root.
          </div>
        </div>
      )}

      <div style={S.grid}>
        {/* ---- LEFT: character ---- */}
        <section style={S.panel}>
          <h2 style={S.h2}>1 · Your character</h2>
          <p style={S.p}>
            Reading your live stats is more accurate than parsing a save file — the game
            has already folded in Astrology, pets, Agility, prayers, and potions.
          </p>
          <button style={S.linkBtn} onClick={() => setShowSnippet((v) => !v)}>
            {showSnippet ? "Hide" : "Show"} the console snippet
          </button>
          {showSnippet && (
            <>
              <ol style={S.ol}>
                <li>Open melvoridle.com with your character loaded</li>
                <li>Press F12, click Console</li>
                <li>Paste this, press Enter — it copies to your clipboard</li>
              </ol>
              <textarea readOnly style={S.code} value={CONSOLE_SNIPPET} rows={8} />
            </>
          )}
          <textarea
            style={S.textarea}
            placeholder="Paste the copied character JSON here"
            value={charJSON}
            onChange={(e) => setCharJSON(e.target.value)}
            rows={4}
          />
          <button style={S.btn} onClick={importChar}>Import character</button>
          {charErr && <div style={S.inlineErr}>{charErr}</div>}
          {char && (
            <dl style={S.statGrid}>
              <Stat label="name" v={char.name} />
              <Stat label="style" v={char.style} />
              <Stat label="max HP" v={char.maxHP} />
              <Stat label="max hit" v={char.maxHit} />
              <Stat label="accuracy" v={char.accuracy?.toLocaleString()} />
              <Stat label="interval" v={`${(char.attackIntervalMs / 1000).toFixed(2)}s`} />
              <Stat label="DR" v={`${char.damageReduction}%`} />
              <Stat label="auto eat" v={`${char.autoEat?.threshold ?? 0}% → ${char.autoEat?.limit ?? 0}%`} />
            </dl>
          )}
        </section>

        {/* ---- MIDDLE: target ---- */}
        <section style={S.panel}>
          <h2 style={S.h2}>2 · Target</h2>
          <input
            style={S.input}
            placeholder="Filter monsters…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <div style={S.list}>
            {filtered.map((m) => (
              <button
                key={m.id}
                className="row"
                onClick={() => setTargetId(m.id)}
                style={S.listRow(targetId === m.id)}
              >
                <span style={S.rowName}>{m.name}</span>
                <span style={S.rowMeta}>
                  <em style={S.style(m.style)}>{m.style?.[0]?.toUpperCase()}</em>
                  <span style={S.hp}>{m.hp.toLocaleString()} hp</span>
                </span>
              </button>
            ))}
          </div>
          <button
            style={{ ...S.btn, opacity: char && targetId ? 1 : 0.4 }}
            onClick={run}
            disabled={!char || !targetId || running}
          >
            {running ? "Simulating…" : "Run 1,000 trials"}
          </button>
        </section>

        {/* ---- RIGHT: results ---- */}
        <section style={S.panel}>
          <h2 style={S.h2}>3 · Result</h2>
          {!result && <div style={S.empty}>Import a character and pick a target to run a simulation.</div>}
          {result && (
            <>
              <div style={S.verdict(result.deathRate)}>
                {result.deathRate === 0 ? "Safe to idle" :
                 result.deathRate < 0.01 ? "Marginal — under 1% deaths" :
                 "Not safe to idle"}
                <span style={S.verdictNum}>
                  {(result.deathRate * 100).toFixed(2)}% death rate
                </span>
              </div>
              <dl style={S.statGrid}>
                <Stat label="kills / hour" v={result.killsPerHour.toFixed(1)} big />
                <Stat label="kill time" v={`${result.killTimeS.toFixed(1)}s`} big />
                <Stat label="lowest HP reached" v={Math.round(result.lowestHP)} />
                <Stat label="hardest hit taken" v={Math.round(result.highestTaken)} />
                <Stat label="food / hour" v={result.foodPerHour.toFixed(0)} />
                <Stat label="trials" v={`${result.kills}k / ${result.deaths}d`} />
              </dl>
              <div style={S.margin}>
                <div style={S.marginLabel}>
                  Safety margin — lowest HP as a share of max
                </div>
                <div style={S.bar}>
                  <div style={S.barFill(result.lowestHP / result.player.maxHP)} />
                </div>
                <div style={S.marginNum}>
                  {Math.round((result.lowestHP / result.player.maxHP) * 100)}% of {result.player.maxHP} HP
                </div>
              </div>
              {result.hasUnmodelled && (
                <div style={S.warn}>
                  This fight uses conditional damage the engine doesn't model
                  (HP thresholds, reflection, debuff scaling). Treat the numbers
                  as a lower bound on incoming damage.
                </div>
              )}
            </>
          )}
        </section>
      </div>

      <footer style={S.footer}>
        Formulas verified against live game values. Mechanics cross-checked against
        mythridium/combat-simulator (GPL-3.0), implemented independently.
        Excludes Into the Abyss and Barrier combat.
      </footer>
    </div>
  );
}

function Stat({ label, v, big }) {
  return (
    <div style={styles.stat}>
      <dt style={styles.dt}>{label}</dt>
      <dd style={{ ...styles.dd, fontSize: big ? 26 : 18 }}>{v ?? "—"}</dd>
    </div>
  );
}

const INK = "#16202B", PAPER = "#EDEFF2", LINE = "#C9D2DC";
const BLUE = "#3A5FCD", TEAL = "#0F7B6C", RED = "#B3261E", AMBER = "#B06E12";

const styles = {
  page: {
    background: PAPER, color: INK, minHeight: "100%", padding: "28px 24px 40px",
    fontFamily: "'IBM Plex Sans', system-ui, sans-serif",
  },
  header: { display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 16, flexWrap: "wrap" },
  eyebrow: {
    fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, letterSpacing: ".14em",
    textTransform: "uppercase", color: "#5C6B7A",
  },
  h1: {
    fontFamily: "'Barlow Condensed', sans-serif", fontWeight: 700, fontSize: 46,
    letterSpacing: "-.01em", margin: "2px 0 0", lineHeight: 1,
  },
  loadPill: (s) => ({
    fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, padding: "5px 10px",
    border: `1px solid ${s === "error" ? RED : LINE}`,
    color: s === "error" ? RED : "#5C6B7A", background: "#fff",
  }),
  rule: { height: 10, margin: "14px 0 22px", opacity: .8 },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 18, alignItems: "start" },
  panel: { background: "#fff", border: `1px solid ${LINE}`, padding: 18 },
  h2: {
    fontFamily: "'Barlow Condensed', sans-serif", fontSize: 20, fontWeight: 600,
    textTransform: "uppercase", letterSpacing: ".06em", margin: "0 0 10px",
    paddingBottom: 8, borderBottom: `1px solid ${LINE}`,
  },
  p: { fontSize: 13, lineHeight: 1.5, color: "#41505F", margin: "0 0 10px" },
  ol: { fontSize: 12.5, lineHeight: 1.7, color: "#41505F", paddingLeft: 18, margin: "10px 0" },
  code: {
    width: "100%", fontFamily: "'IBM Plex Mono', monospace", fontSize: 10.5,
    border: `1px solid ${LINE}`, padding: 10, background: "#F7F9FB", color: "#2C3A48",
    resize: "vertical", lineHeight: 1.45,
  },
  textarea: {
    width: "100%", fontFamily: "'IBM Plex Mono', monospace", fontSize: 11.5,
    border: `1px solid ${LINE}`, padding: 10, marginTop: 10, resize: "vertical",
  },
  input: {
    width: "100%", fontFamily: "'IBM Plex Sans', sans-serif", fontSize: 13,
    border: `1px solid ${LINE}`, padding: "8px 10px", marginBottom: 10,
  },
  btn: {
    width: "100%", marginTop: 10, padding: "10px 14px", background: INK, color: "#fff",
    border: "none", fontFamily: "'Barlow Condensed', sans-serif", fontSize: 16,
    letterSpacing: ".06em", textTransform: "uppercase", cursor: "pointer", fontWeight: 600,
  },
  linkBtn: {
    background: "none", border: "none", padding: 0, color: BLUE, cursor: "pointer",
    fontSize: 12.5, textDecoration: "underline", fontFamily: "inherit",
  },
  list: { maxHeight: 320, overflowY: "auto", border: `1px solid ${LINE}`, background: "#FAFBFC" },
  listRow: (sel) => ({
    display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%",
    padding: "7px 10px", border: "none", borderBottom: `1px solid #E4E9EF`,
    background: sel ? "#DDE5F5" : "transparent", cursor: "pointer", textAlign: "left",
    fontFamily: "inherit", fontSize: 13,
  }),
  rowName: { color: INK },
  rowMeta: { display: "flex", gap: 10, alignItems: "center" },
  style: (s) => ({
    fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, fontStyle: "normal",
    width: 16, height: 16, lineHeight: "16px", textAlign: "center", color: "#fff",
    background: s === "melee" ? "#7A4A2B" : s === "ranged" ? TEAL : "#4B3A80",
  }),
  hp: { fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, color: "#5C6B7A", minWidth: 62, textAlign: "right" },
  statGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px 14px", margin: "14px 0 0" },
  stat: { margin: 0 },
  dt: {
    fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, letterSpacing: ".1em",
    textTransform: "uppercase", color: "#6B7A89",
  },
  dd: { margin: "2px 0 0", fontFamily: "'IBM Plex Mono', monospace", fontWeight: 500 },
  verdict: (dr) => ({
    padding: "12px 14px", background: dr === 0 ? "#E6F3F0" : dr < 0.01 ? "#FBF3E2" : "#FBE9E7",
    border: `1px solid ${dr === 0 ? TEAL : dr < 0.01 ? AMBER : RED}`,
    color: dr === 0 ? TEAL : dr < 0.01 ? AMBER : RED,
    fontFamily: "'Barlow Condensed', sans-serif", fontSize: 22, fontWeight: 700,
    textTransform: "uppercase", letterSpacing: ".04em",
    display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: 8,
  }),
  verdictNum: { fontFamily: "'IBM Plex Mono', monospace", fontSize: 13, fontWeight: 500, letterSpacing: 0 },
  margin: { marginTop: 18 },
  marginLabel: {
    fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, letterSpacing: ".1em",
    textTransform: "uppercase", color: "#6B7A89", marginBottom: 6,
  },
  bar: { height: 10, background: "#E4E9EF", border: `1px solid ${LINE}` },
  barFill: (f) => ({
    height: "100%", width: `${Math.max(2, Math.min(100, f * 100))}%`,
    background: f > 0.5 ? TEAL : f > 0.25 ? AMBER : RED,
  }),
  marginNum: { fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, color: "#5C6B7A", marginTop: 5 },
  empty: { fontSize: 13, color: "#6B7A89", lineHeight: 1.5, padding: "18px 0" },
  warn: {
    marginTop: 14, padding: "10px 12px", background: "#FBF3E2", border: `1px solid ${AMBER}`,
    fontSize: 12, lineHeight: 1.5, color: "#6B4A0C",
  },
  error: { padding: "12px 14px", background: "#FBE9E7", border: `1px solid ${RED}`, color: RED, fontSize: 13, marginBottom: 18 },
  errorSub: { color: "#7A2B22", fontSize: 12, marginTop: 4 },
  inlineErr: { color: RED, fontSize: 12, marginTop: 8, fontFamily: "'IBM Plex Mono', monospace" },
  footer: {
    marginTop: 28, paddingTop: 14, borderTop: `1px solid ${LINE}`,
    fontSize: 11.5, color: "#6B7A89", lineHeight: 1.6,
  },
};
