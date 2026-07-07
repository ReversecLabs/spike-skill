# Phase 5 — Results Analysis

After running `spikee test`, analyse the results to understand your target's vulnerability profile.

## 5.1 Analyse Results

```bash
# Analyse a single results file
spikee results analyze --result-file results/results_my_target_cybersec-2026-01_*.jsonl

# Analyse all results in a folder
spikee results analyze --result-folder results/

# Only show overview statistics (skip breakdowns)
spikee results analyze --result-file results/results_*.jsonl --overview

# Combine multiple result files into one analysis
spikee results analyze --result-file results/results_run1_*.jsonl \
                       --result-file results/results_run2_*.jsonl \
                       --combine
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

Results are broken down by:
- **Jailbreak Type** — which jailbreak templates are most effective?
- **Instruction Type** — which attack goals succeed most often?
- **Plugin** — do encoding transforms help bypass defences?
- **Language** — is the target more vulnerable in certain languages?

Sort by success rate to quickly identify the most effective attack vectors.

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

## 5.4 Re-Judge Results

Re-evaluate existing results with a different judge or LLM model without re-running the test:

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
| Low success rate across all categories | Try dynamic attacks (`--attack crescendo`), different plugins, or more diverse seeds |
| High success for specific jailbreak types | The target is vulnerable to that bypass technique — report it |
| High success for specific instruction types | The target doesn't defend against those goals — prioritise remediation |
| Encoding plugins increase success | The target doesn't handle encoded inputs — test more encoding variants |
| Dynamic attacks significantly improve success | Static defences are present but can be bypassed with persistence |
| Many errors | Check target implementation, rate limits, or connectivity |
| Many guardrail triggers | The guardrail is working — test with more advanced attacks or check false positive rate |

> For complete results documentation, read `spikee-src/docs/11_results.md`.
