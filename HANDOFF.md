# Phenoscale PAM — Handoff (short)

If you're taking over: this repo is the documentation hub. The code and heavy lifting live in three linked repos: [phenoscale-pilot](https://github.com/nilomr/phenoscale-pilot) (processing), [perch-cpu-inference](https://github.com/nilomr/perch-cpu-inference) (embeddings & inference), and [AudioMoth-Wytham-Woods](https://github.com/nilomr/AudioMoth-Wytham-Woods) (device firmware).

### What to do first (quick):
- Confirm you have access to the three linked repos (or just fork or clone them) and read access to the data store.
- Find the dataset path in `docs/0-data-access.md` and ensure you can mount or request access.
- If the data is accessible, run a small end-to-end check: extract embeddings from one site using `perch-cpu-inference` on a few audio files and inspect outputs. These will have been extrated already for the full dataset, so this step is optional.

### Essential checks for takeover:
1. Verify data access and that the example/sample dataset used in docs can be read locally.
2. Run a sample embedding extraction (a handful of clips) using `perch-cpu-inference` and confirm files are produced.
3. Inspect the device inventory in `metadata/phenoscale_acoustic_loggers.csv`, open `metadata/logger_map.html` to check locations, familiarise yourself with the deploment, and make sure you readily understand the data collection setup as described in `docs/1-data-sources.md`.
4. Update this file (or the docs) with any missing information you had to look up or figure out, so the next person has it documented.

### Contacts & ownership
- Reach out to the project lead for questions. Project lead: Ben Sheldon, University of Oxford.
- Previous maintainer: nilomr (GitHub: @nilomr)

### Notes & known gaps
- This repo is a documentation index. The detailed scripts, tests, and operational runbooks live in the other repos listed above.
- No CI or automated tests are set up.

### Where to look next
- `docs/index.md` — a map to more detailed docs (data access, samples, validation, processing, downstream ideas).

