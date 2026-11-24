# Unfuckin-Slop

Build interfaces from a searchable local library of UI prompts, component source and registry entries. Give `unfslop` a product brief and its fine-tuned MiniLM model ranks a page blueprint and material for each section. The coding agent applies the selected material, connects product data and actions, and verifies the result.
## Install

Install from Git using Git, Python, and a Rust toolchain.

```sh
git clone --depth 1 https://github.com/steoward/unfuckin-slop.git
cd unfuckin-slop
python -m pip install -r requirements.txt
cargo run --locked --release --bin unfslop -- install --agent codex
```

Run the same commands on Windows, macOS and Linux. The last command installs the skill, local model and catalog. Codex's project skill directory is `.agents/skills/`. Add `--user` to install for your user account, `--dir PATH` for another location, or `--force` to update an existing installation. Set `UNFSLOP_PYTHON` if the agent uses a different interpreter.

Run commands below with `target/release/unfslop` from the checkout, or with the installed skill's `bin/unfslop` on PATH. On Windows the executable has an `.exe` suffix. The CLI is installed as `unfslop`.

## Build with the library

Ask your coding agent to **build your product site with unfuckin-slop**. For example, “Build a site for a portable field recorder. Let hikers compare microphones and reserve a unit. Use unfuckin-slop.”

```sh
unfslop plan "Portable field recorder for hikers; compare microphones and reserve a unit"
unfslop plan "Field recording archive" --section "player=audio waveform scrubber" --section "track-list=keyboard navigable list of recordings" --full
unfslop library
unfslop library "swipeable card stack" --pool components --limit 5
unfslop library --source motionsites.ai --category Footer --limit 10
unfslop library --record 3d-character-studio --record skiper-skiper48 --record 21st-aurora-ribbons
```

- **`plan`** returns a selected blueprint and ranked choices for each section in one JSON response. The default product-page sections are navigation, hero, features, primary action and footer. Repeated `--section NAME=QUERY` supplies the sections for a different page or screen. A section can pin a known reference by ID. `--full` includes complete selected records inline. `--local` restricts selection to the bundled prompts and source snapshots. A partial plan identifies slots that need another catalog query.
- **`library`** pages through all 10,685 records or searches by intent, ID, title or source URL. Filter by pool, provider or category. Continue with the returned `next_offset`. Repeated `--record` returns the full stored material for several selections in one call, with their source, dependencies where supplied, and a structured integration action.
- **`design`** remains the compact reference and Apple Design / Impeccable card command. **`context`**, **`get`** and **`lint`** run without Python.

A MotionSites record contains the stored build prompt. A Skiper UI record contains its source snapshot and may require project helpers or assets. A 21st.dev record includes registry instructions, with any supported install URL and required environment variable identified separately. Use a configured `API_KEY_21ST` where the registry requires it, or implement the documented pattern in the target stack. See each upstream source for terms and current availability.

## Catalog

| Provider | Records | Material available in the bundled snapshot |
| --- | ---: | --- |
| MotionSites | 328 | Design prompts. 185 records have video links. |
| Pixlpin | 622 | Descriptions and video links. |
| Skiper UI | 37 | Component source snapshots. Integration can require assets, helper files, or current registry code. |
| 21st.dev | 9,698 | Descriptions and registry instructions. Consult the linked component for its implementation and terms. |

The installed model library packages the ONNX encoder, both vector indexes and the full catalog payloads together. Inference ranks the stored records, so the agent can retrieve the actual material by ID. Hybrid search uses lexical ranking and MiniLM. If the semantic runtime is unavailable, search reports the lexical fallback in JSON. The three supplied prompt and component collections are represented in the catalog by source URL. The catalog covers source records, and the encoder checkpoint does not enumerate individual training examples. [Source comparison and evaluation](eval/README.md)

Project code is [MIT licensed](LICENSE). See [credits and third-party material](NOTICE.md).
