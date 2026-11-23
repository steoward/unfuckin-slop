# Unfuckin-Slop

Find UI references locally, then use Apple Design and Impeccable guidance to build a screen that fits the product. The Rust CLI serves the craft cards and checks front-end source. A fine-tuned MiniLM encoder ranks catalog descriptions alongside lexical search. The coding agent designs and tests the interface.

## Install

Download the archive for your platform from a successful [GitHub Actions run](https://github.com/steoward/unfuckin-slop/actions) and extract the enclosed `.tar.gz` into your agent’s skills directory. The bundle includes `SKILL.md`, the CLI, and `design-library/`. Install `design-library/requirements.txt` into the Python environment the agent uses. Call `bin/unfslop` by its path (`bin\unfslop.exe` on Windows).

To build and install from a checkout:

```sh
python -m pip install -r requirements.txt
cargo build --release --bin unfslop
./target/release/unfslop install --agent codex
```

On Windows, use `.\target\release\unfslop.exe`. Pass `--dir PATH` to install into a specific skills directory. Set `UNFSLOP_PYTHON` if the agent should use a specific interpreter. A binary moved outside the checkout or the bundle can use `UNFSLOP_DESIGN_LIBRARY` to locate the index.

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
