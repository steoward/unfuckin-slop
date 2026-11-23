# Unfuckin-Slop

Find UI references locally, then use Apple Design and Impeccable guidance to build a screen that fits the product. The Rust CLI serves the craft cards and checks front-end source. A fine-tuned MiniLM encoder ranks catalog descriptions alongside lexical search. The coding agent designs and tests the interface.

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

## Use

```sh
unfslop design "field-recording archive with a track list and audio player"
unfslop design "card stack with swipe" --pool components --source skiper-ui.com
unfslop design --record skiper-skiper48 --pool components
unfslop context "audit a modal for focus and keyboard behavior"
unfslop lint src/
```

`design` returns up to three references with source links, the type of material stored, and an Apple Design and Impeccable card. Search by intent, or pass a catalog ID, title, or original URL to find a known reference. If several records share a title, use a source URL or ID. Open the selected original record with `--record` for the complete stored text. The evidence packet reports exact, hybrid, lexical, or filter-only retrieval when applicable.

The `context`, `get` and `lint` commands run without Python. Run `unfslop help` for flags. Lint flags source patterns. Check the rendered page, main actions, and keyboard behavior to evaluate the actual design.

## Catalog

| Provider | Records | Material available in the bundled snapshot |
| --- | ---: | --- |
| MotionSites | 328 | Design prompts. 185 records have video links. |
| Pixlpin | 622 | Descriptions and video links. |
| Skiper UI | 37 | Component source snapshots. Integration can require assets, helper files, or current registry code. |
| 21st.dev | 9,698 | Descriptions and registry instructions. Consult the linked component for its implementation and terms. |

The encoder ranks text and selects records. The original preview, installed assets, interaction behavior, and the agent’s implementation determine what a user sees. [Source comparison and evaluation](eval/README.md)

Project code is [MIT licensed](LICENSE). See [credits and third-party material](NOTICE.md).
