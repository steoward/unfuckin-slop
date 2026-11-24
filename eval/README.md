# Retrieval evaluation

Run against the configured private catalog. `tests/verify_dataset.py` checks
record IDs, media paths and vector shapes. `eval/smoke_test.py` exercises the
official model and optionally accepts `--reference SCREENSHOT`.

`eval/evaluate.py` compares keyword ranking, EmbeddingGemma 2 text similarity
and hybrid search on `benchmark.json`. Benchmark labels are canonical catalog
IDs. Use the private archive when building the catalog so these IDs resolve.

Run the benchmark with the pinned base model, then set `UNFSLOP_ADAPTER`,
rebuild the indexes, and rerun to measure the fine-tune. Review video matches
against their returned timestamps and verify visual transfer in the rendered
page. The text benchmark does not measure visual fidelity.

The installed CLI test runs with a small fixture catalog and checks browsing,
source retrieval and section plans. It requires no Hugging Face download.
