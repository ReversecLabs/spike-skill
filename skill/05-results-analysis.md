# Phase 5 — Results Analysis

After running `spikee test`, analyse the results to understand your target's vulnerability profile.

Base Spikee findings and metrics only on Spikee result artifacts. The assistant's own direct interactions are not test evidence. If the user explicitly requested a manual or out-of-band deviation, analyse and report it separately with its method and limits; do not combine it with Spikee results or success rates.

> **Workspace memory:** Read `spikee.log` first to locate the intended result files and prior decisions, then verify those paths and statuses before relying on them.

## Analysis Gate and Workflow Routing

Analyse the small static baseline before recommending a full or dynamic run. First verify that target responses are valid, judges executed as intended, errors are acceptably low, and the sample represents the relevant dataset categories. Do not treat an error-heavy or poorly covered run as evidence of safety or vulnerability.

When the gate fails, fix the cause and repeat the small baseline:

- **Phase 1:** wrong workspace, virtual environment, or Spikee installation.
- **Phase 2:** target integration, authentication, response shape, or single-/multi-turn behaviour.
- **Phase 3:** missing coverage, unsuitable entries, or incorrect/ambiguous judge definitions.
- **Phase 4:** provider access, timeouts, rate limits, concurrency, retries, or test parameters.

Only after the baseline is trustworthy should you compare vulnerability rates, scale the static run, or consider a compatible dynamic attack.

## 5.1 Analyse Results

```bash
# Analyse a single file (console output)
spikee results analyze --result-file results/results_my_target_cybersec-2026-01_*.jsonl

# Analyse all results in a folder
spikee results analyze --result-folder results/

# Output as HTML report
spikee results analyze --result-file results/results_*.jsonl --output-format html

# Only show overview statistics
spikee results analyze --result-file results/results_*.jsonl --overview

# Combine multiple result files
spikee results analyze --result-file results/run1.jsonl --result-file results/run2.jsonl --combine
```

## 5.2 Understanding the Output

### General Statistics

| Metric | Meaning |
|---|---|
| **Total Unique Entries** | Number of distinct test cases |
| **Successful Attacks (Total)** | Entries where at least one attempt succeeded |
| **Failed Attacks** | Entries where all attempts failed |
| **Errors** | Entries where all attempts errored |
| **Guardrail Triggered** | Entries where all attempts were blocked by guardrail |
| **Attack Success Rate** | `Successful / Total` — the headline vulnerability metric |

### Dynamic Attack Metrics (if `--attack` was used)

| Metric | Meaning |
|---|---|
| **Initially Successful** | Succeeded with the static payload (before dynamic attack) |
| **Only Successful with Dynamic Attack** | Succeeded only because the attack found a bypass |
| **Attack Success Rate (Improvement)** | Additional vulnerability uncovered by the attack strategy |

### Breakdown Tables

Results are broken down by **Jailbreak Type**, **Instruction Type**, **Plugin**, and **Language**. Sort by success rate to identify effective attack vectors.

## 5.3 Extract Specific Results

```bash
# Extract all successful attacks to a new file
spikee results extract --result-file results/results_*.jsonl --category success

# Extract failures
spikee results extract --result-file results/results_*.jsonl --category failure

# Extract guardrail triggers
spikee results extract --result-file results/results_*.jsonl --category guardrail

# Custom search — find specific error patterns
spikee results extract --result-file results/results_*.jsonl \
                       --category custom \
                       --custom-search "error:timeout"

# Custom search on specific field
spikee results extract --result-file results/results_*.jsonl \
                       --category custom \
                       --custom-search "instruction_type:xss"

# Inverse search (entries that DON'T match)
spikee results extract --result-file results/results_*.jsonl \
                       --category custom \
                       --custom-search "!jailbreak_type:no-jailbreak"
```

## 5.4 Re-Judge Results — Explicit User Choice Only

Re-evaluate existing results with a different judge or LLM model without re-running the test:

Do not re-judge automatically. Run this only after the user explicitly chooses re-judging and the judge provider/model. State why it is proposed and label the resulting analysis with the chosen evaluation configuration. If LLM access is missing or unclear, stop and offer supported hosted-provider or local-endpoint setup options; do not substitute `regex`, `canary`, or a custom judge, and do not rewrite the dataset to make re-judging run.

```bash
# Re-judge with a different LLM
spikee results rejudge --result-file results/results_*.jsonl \
                       --judge-options "openai/gpt-4o"

# Resume an interrupted re-judge
spikee results rejudge --result-file results/results_*.jsonl \
                       --judge-options "openai/gpt-4o" \
                       --resume
```

## 5.5 Compare Across Targets

Compare how the same dataset performs against different targets:

```bash
spikee results dataset-comparison \
    --dataset datasets/cybersec-2026-01-*.jsonl \
    --result-file results/results_target-A_*.jsonl \
    --result-file results/results_target-B_*.jsonl \
    --result-file results/results_target-C_*.jsonl \
    --success-threshold 0.8 \
    --success-definition gt
```

This identifies entries that succeed against most targets (threshold > 80%) — these are the most dangerous attacks in your dataset.

To find entries that are hardest to exploit (succeed < 20% of the time):
```bash
spikee results dataset-comparison \
    --dataset datasets/cybersec-2026-01-*.jsonl \
    --result-file results/results_target-A_*.jsonl \
    --result-file results/results_target-B_*.jsonl \
    --success-threshold 0.2 \
    --success-definition lt \
    --number 10
```

## 5.6 Web UI

Launch an interactive web interface for exploring results:

```bash
spikee webui                              # Default: 127.0.0.1:8080
spikee webui --host 0.0.0.0 -p 8081      # Bind to all interfaces
spikee webui --database jobs.db           # Persist job history
```

The web UI covers: Generate, Test, Jobs monitoring, and Results exploration.

## 5.7 Guardrail Testing — False Positive Analysis

For guardrail targets, run two test sets and combine:

```bash
# 1. Run attack dataset against guardrail
spikee test --dataset datasets/attack-dataset.jsonl \
            --target my_guardrail \
            --tag attack_results

# 2. Run benign dataset against guardrail
spikee test --dataset datasets/benign-dataset.jsonl \
            --target my_guardrail \
            --tag benign_results

# 3. Analyse with false positive checks
spikee results analyze \
    --result-file results/results_my_guardrail_*attack_results*.jsonl \
    --false-positive-checks results/results_my_guardrail_*benign_results*.jsonl
```

This produces a **Confusion Matrix** and metrics:
- **Precision** — of blocked prompts, how many were actual attacks?
- **Recall** — of actual attacks, how many were blocked?
- **F1 Score** — harmonic mean of precision and recall
- **Accuracy** — overall correct classification rate

> For the full guardrail testing workflow, read `spikee-src/docs/10_guardrail_testing.md`.

## 5.8 Excel Export

```bash
spikee results convert-to-excel --result-file results/results_*.jsonl
```

## 5.9 Iteration Guide

Based on results, decide next steps:

| Observation | Action |
|---|---|
| Low success rate across all categories | First validate judge behaviour and coverage. If the baseline is sound and adaptive testing fits the user's goal, return to Phase 4 and propose a compatible dynamic attack with explicit limits |
| High success for specific jailbreak types | The target is vulnerable to that bypass technique — report it |
| High success for specific instruction types | The target doesn't defend against those goals — prioritise remediation |
| Encoding plugins increase success | The target doesn't handle encoded inputs — return to Phase 3, add agreed encoding plugins, regenerate the dataset, and rerun it through `spikee test` |
| Dynamic attacks significantly improve success | Static defences are present but can be bypassed with persistence |
| Missing or unrepresentative categories | Return to Phase 3 and correct dataset coverage, then repeat the small baseline |
| Judge access or judge meaning is unresolved | Stop. Confirm the intended judge in Phase 3 and configure the user-chosen provider/endpoint in Phase 4; never substitute a simpler judge to continue |
| Malformed, empty, or unexpected target responses, or target-application authentication failures | Return to Phase 2 and fix the target contract or target authentication |
| Judge/attack-provider authentication failures | Return to Phase 4 to configure the chosen provider; return to Phase 3 as well if the provider or judge choice itself is unresolved |
| Many timeouts, rate-limit responses, or request errors | Identify whether they came from the target, judge/attack provider, or test runner; route to Phase 2 or 4 accordingly before drawing conclusions |
| Many guardrail triggers | Run the false-positive workflow and verify benign coverage before concluding that the guardrail is effective |

After analysis, update the `spikee.log` summary and add a concise analysis/decision entry containing only durable conclusions, material errors or coverage gaps, the result/report path, the user's decision, and the next phase/gate. Do not duplicate detailed evidence already stored in results.

> For complete results documentation, read `spikee-src/docs/11_results.md`.
