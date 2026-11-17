# Review and evidence

Before implementation: reuse the Scientific Method Lab editor, worker, relative-path deployment and quiet reading layout. Keep one primary Run action; optional notes, tools and worked output remain collapsed. Use distinct course storage keys. No external service receives learner code.

Sources: Hernán and Robins, Causal Inference: What If; Pearl, Causal Diagrams for Empirical Research; Angrist and Imbens on instrumental variables; World Bank Impact Evaluation in Practice. Source links are reading references, not a claim of full-text verification in this session.

Learning effectiveness has not been evaluated with novice learners.

## Implementation review — 14 November 2026

The essential route has 18 investigations in six modules, each with one main outcome, explicit data provenance, a prediction, an executable example, a deliberate change and a separate application question. Concept comparisons distinguish estimands and assumptions. Five plots are generated from actual example executions; worked output is never fabricated. The scientific-method relationship is explained in the course notes.

Scientific review checked counterfactual arithmetic, zero-effect confounding, collider selection, total versus direct pathways, target-population standardisation, known-propensity weighting, empty comparison cells, ATT versus ATE, parallel-trend violations, cutoff locality, instrumental-variable exclusion violations, biased confidence intervals, sensitivity scenarios, selective observation and transport. Numerical contract tests include changed assumptions that deliberately break identification. The final example states that aggregate cell means supply no sampling interval.

Verification: seven native test groups pass; all 18 exact published examples execute. Build produces 20 static pages and five executed plots; 693 local links and fragments pass. Real Chromium/Pyodide executes all 18 examples with native/browser numerical agreement and no page errors. Browser tests cover error recovery, Stop/restart, exact-source run and report exports, stale-output notices, local drafts, progress export/import, every lesson quiz, all 18 phone layouts, contents keyboard Escape, themes and JavaScript-free worked output. Third-party browser requests are blocked during these tests; the runtime and fonts are served locally. Screenshots are saved in test-results and uploaded by CI.

Visual review: overview and mobile lesson use the retained readable typography and quiet layout. Code may scroll horizontally within its editor; the document does not overflow at 390 px. Optional tools, hints, notes and worked output leave the main reading route uncluttered. The causal hero uses explicit arrow directions.

Limitations: no novice usability study, full formal causal-identification review or assistive-technology user study has been conducted. Source references were selected for methodological reading; source titles are not evidence that their entire texts were reviewed in this session. Real causal studies need domain-specific assumptions and analysis beyond these small invented examples.

## Learner-flow review — 17 November 2026

The UX and learning-design pass names the values learners edit and the output
fields they compare in all 18 investigations. The two hints in each lesson
now point to the evidence for its fresh question. The prepared example and
comparison instructions are visible with optional panels closed.

Tab moves from the editor to Run Python. The existing run shortcut is visible,
and Stop can receive keyboard focus when a run starts. Restore example saves the
draft it replaces and offers Recover draft in Tools. The recovery copy is part
of progress exports. An execution error shows its message separately from
successful output. Run JSON and the final report use the last successful
execution, including when a later attempt fails.

The full check passed native calculations, all 18 browser examples, links,
feedback, keyboard Stop and restart, draft recovery after reload, progress
export and import, and JavaScript-free reading. Browser tests confirmed that a
later Python exception leaves both the successful output and its exported
record intact. These checks establish behaviour and example arithmetic.
Learner understanding remains unmeasured.
