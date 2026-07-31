# melvor-data# melvor-data

Reference data for Melvor Idle progression planning.

## Contents

| File | What it is |
|---|---|
| `melvor-wiki.zip` | Full copy of wiki.melvoridle.com — 6,549 pages (5,805 articles, 409 templates, 184 categories, 151 modules). Unzips to `melvor-wiki.json`. |
| `game-data/melvorDemo.json` | Base game data (namespace `melvorD`) |
| `game-data/melvorFull.json` | Full version data (namespace `melvorF`) |
| `game-data/melvorTotH.json` | Throne of the Herald (namespace `melvorTotH`) |
| `game-data/melvorExpansion2.json` | Atlas of Discovery (namespace `melvorAoD`) |
| `game-data/en.json` | Internal IDs to display names |

## Wiki dump format

`melvor-wiki.json` is a single JSON object:

```json
{
  "source": "wiki.melvoridle.com",
  "dumped": "2026-07-31T19:59:08.277Z",
  "namespaces": [0, 828, 10, 14],
  "count": 6549,
  "pages": { "Page Title": "raw wikitext...", ... }
}
```

Wiki content belongs to its contributors. This copy is for personal reference.

## Refreshing

Game data — on melvoridle.com with a character loaded, open the browser console (F12) and download from `https://melvoridle.com/assets/data/`. The version suffix (`?528`) changes between updates; check the Network tab for current URLs.

Wiki — re-run the dump script from the browser console while on wiki.melvoridle.com.
