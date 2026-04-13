# Defects4J ODC Pipeline

This repository now contains a runnable Python pipeline for your thesis direction:

1. Collect pre-fix bug evidence from Defects4J.
2. Build an ODC defect-type classification prompt using a scientific-debugging structure.
3. Call an OpenAI-compatible LLM endpoint.
4. Save machine-readable outputs for later evaluation and annotation.

## What the pipeline does

- Checks out a buggy Defects4J version with the official CLI.
- Compiles and tests the buggy version.
- Parses `failing_tests` and stack traces.
- Extracts source snippets around suspicious stack frames.
- Optionally runs `defects4j coverage` on suspicious classes only.
- Builds a structured ODC classification prompt.
- Writes `context.json`, `classification.json`, and a markdown report.

## Quick start

### 1. Collect bug context

```powershell
python -m d4j_odc_pipeline collect `
  --project Lang `
  --bug 1 `
  --work-dir .\work\Lang_1b `
  --output .\artifacts\Lang_1\context.json `
  --defects4j-cmd "perl C:\path\to\defects4j"
```

If `defects4j` is already on your `PATH`, omit `--defects4j-cmd`.

### 2. Classify with an LLM

Set your API key first:

```powershell
$env:OPENAI_API_KEY="your-key"
```

Then run:

```powershell
python -m d4j_odc_pipeline classify `
  --context .\artifacts\Lang_1\context.json `
  --output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --model gpt-4.1-mini
```

### 3. End-to-end run

```powershell
python -m d4j_odc_pipeline run `
  --project Lang `
  --bug 1 `
  --work-dir .\work\Lang_1b `
  --context-output .\artifacts\Lang_1\context.json `
  --classification-output .\artifacts\Lang_1\classification.json `
  --report .\artifacts\Lang_1\report.md `
  --model gpt-4.1-mini `
  --defects4j-cmd "perl C:\path\to\defects4j"
```

## Design choices aligned with your thesis

- The LLM sees pre-fix evidence only by default.
- `classes.modified` is stored as a hidden oracle for offline analysis, but it is excluded from the prompt.
- The default prompt style is `scientific`, which follows observation, hypothesis, prediction, experiment, and conclusion.
- The ODC target is the 7-class `Defect Type` attribute, which matches the narrower thesis scope in `thesis_review.md`.

## Notes

- This environment currently does not have Java or Defects4J installed, so local verification here is limited to the Python side.
- On Windows, the upstream Defects4J README notes that you may need to invoke it as `perl <fullpath>\defects4j` instead of plain `defects4j`.
