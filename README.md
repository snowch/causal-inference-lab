# Causal Inference Lab

Eighteen short investigations into inferring causal effects from observational data. A companion to [Scientific Method Lab](https://snowch.github.io/scientific-method-lab/).

**Course:** https://snowch.github.io/causal-inference-lab/

Learners define counterfactual questions, draw causal stories, standardise and weight comparisons, inspect overlap, explore matching, difference-in-differences, regression discontinuity and instrumental variables, then challenge uncertainty, confounding, missingness and generalisation. Each lesson includes editable real Python, build-executed worked output, a prediction, one change and a fresh question with feedback. The final report exports the exact completed execution.

All inputs are invented or simulated and labelled. These examples teach reasoning; they do not establish real treatment effects. Basic Python reading helps. Allow approximately 2½ hours plus exploration; this is an author estimate.

## Develop

Node 24 and Python 3.12 recommended:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm ci
python -m playwright install chromium
npm run dev
```

Open http://localhost:5173/causal-inference-lab/. The prefix exercises GitHub Pages paths. `npm run check` executes every example, builds the static course and hash-verified self-hosted Python runtime, checks links, and runs browser checks. Set `CHROMIUM_PATH=/usr/bin/chromium` to use system Chromium. Browser evidence is saved in ignored `test-results/`.

## Author and publish

- `src/course.json`: lesson route, prose, tasks and references.
- `python/`: complete standalone learner examples.
- `scripts/`: build, actual example execution, illustrations and pinned runtime preparation.
- `src/app.js`, `src/worker.js`: local drafts, feedback, exports and Python execution.
- `docs/`: learning design and review evidence.

The GitHub Actions workflow checks pull requests and pushes; a successful push to `main` publishes `dist/` through GitHub Pages Actions. No account, API key or paid learner service is required. Worked examples remain readable without JavaScript. First execution needs a substantial runtime download; full offline support is not provided.

The learning interface and runtime are adapted from Christopher Snow’s Scientific Method Lab. Code: Apache-2.0. Original content: CC BY-NC 4.0. Third-party packages retain their licences. See LICENSE and LICENSE-CODE.
