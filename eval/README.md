# Evaluation

## What the catalog preserves

The encoder uses text to select an original record. To assess fidelity, compare the record with the provider’s current prompt, demo, or registry, then inspect your implementation on the target device.

| Reference | Live source and stored material |
| --- | --- |
| [3D Character Studio](https://motionsites.ai/lesson/cursor-tracking-website-with-motionsites) | The stored prompt includes the same cursor-controlled background video, its crop, and the seek behavior described in the lesson. The 550-character excerpt stops before the seek behavior. Use the full record and inspect the media. |
| [Card swipe carousel](https://skiper-ui.com/v1/skiper48) | The source page shows the card stack, drag and optional autoplay. The stored snapshot includes Swiper’s card effect and autoplay. Its demo wrapper references local images and a project helper. Matching the interaction in another app also depends on assets, configuration and integration. |
| [Aurora Ribbons](https://21st.dev/@ln-dev7/components/aurora-ribbons) | The record agrees with the original description and names the React Three Fiber dependencies. The source page shows a demo and points to the component implementation. The 298-character stored entry contains the description and registry instructions. |

## Retrieval audit

`python eval/source_fidelity.py` runs title, source URL, and paraphrase probes across four records per provider. This is a focused audit of catalog entry points. It measures whether the intended record appeared, including when several records share a title. It does not measure visual similarity or output quality.

| Probe | Previous first result | Current first result | Previous top three | Current top three |
| --- | ---: | ---: | ---: | ---: |
| Titles | 12/12 | 12/12 | 12/12 | 12/12 |
| Original URLs | 4/12 | 12/12 | 6/12 | 12/12 |
| Paraphrases | 11/12 | 11/12 | 11/12 | 11/12 |
| Paraphrases filtered by source | Unavailable | 11/12 | Unavailable | 12/12 |

The comparison used the shipped model and catalogs on both versions. To reproduce the baseline, save `search_design_showcases.py` from commit `6ff308a` as `previous_search.py` in the repository root and run `python eval/source_fidelity.py --baseline previous_search.py`.

## Other checks

- `cargo test` runs CLI and card tests.
- `python eval/smoke_test.py` checks ONNX inference and lexical fallback.
- GitHub Actions exercises exact and hybrid lookup from an installed bundle.
- [Design pilot](design-pilot.html) compares four runnable prototypes on two briefs. Download it and open it locally.
- [Showcase benchmark](benchmark.json) and [recorded results](deployed_results.json) track earlier model evaluation. `python eval/evaluate.py --help` lists the supported runs.
