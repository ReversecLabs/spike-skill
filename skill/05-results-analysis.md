# Phase 5 — Results Analysis

After running `spikee test`, analyse the results to understand your target's vulnerability profile.

Base Spikee findings and metrics only on Spikee result artifacts. The assistant's own direct interactions are not test evidence. If the user explicitly requested a manual or out-of-band deviation, analyse and report it separately with its method and limits; do not combine it with Spikee results or success rates.

> **Workspace memory:** Read `spikee.log` first to locate the intended result files and prior decisions, then verify those paths and statuses before relying on them.

Any new or repeated `spikee test` proposed during analysis is Phase 4 work and must follow Phase 4's preview, confirmation, baseline, and attachable-session gates.

## Built-In Analysis First; JSONL When Useful

For a normal summary of a completed run, do not begin by rebuilding Spikee's aggregate calculations manually. First run `spikee results analyze` normally, without tmux, against the exact intended result file and present the resulting overview and relevant breakdowns to the user. Do not merely say that analysis completed: capture its console output, explain the important figures, and retain the exact result path.

The CLI subcommand is `analyze` (American spelling): `spikee results analyze`. There is no `spikee results --analyse` form in this bundled version.

Direct inspection of the result JSONL is also allowed and often necessary. Use ordinary read-only tools such as `jq`, `rg`, or a small parsing script for specific questions, individual prompt/response review, error diagnosis, severity assessment, validation of judge decisions, or calculations not provided by Spikee. Prefer `spikee results extract` when its standard categories already express the requested filter. State which files and filters a manual answer used, distinguish custom calculations from Spikee's metrics, and never edit the original result artifact in place.

Preserve result artifacts by default. If the user explicitly asks to edit, replace, move, archive, or delete a result—including stale results—treat it as an audited mutation. After any required authorization and immediately before the change, add a `starting` record under `Executions` in `spikee.log` with the timestamp, actor, operation, exact source/destination paths, reason, and full command or action. If the log write fails, do not mutate the result. Afterward, update the same record with finish time and `completed` or `failed`; state whether the original remains recoverable. Never infer permission to clean up results.

If `spikee results analyze` fails or cannot parse an artifact, report that failure and investigate the JSONL directly instead of abandoning the analysis. Keep the fallback clearly labelled; do not present manually reconstructed numbers as command output.

## Analysis Gate and Workflow Routing

Analyse the small static baseline before recommending a full or dynamic run. First verify that target responses are valid, judges executed as intended, errors are acceptably low, and the sample represents the relevant dataset categories. Do not treat an error-heavy or poorly covered run as evidence of safety or vulnerability.

When the gate fails, explain the evidence and propose work in the owning phase below. Apply the [phase handoff gate](SKILL.md#collaboration-and-phase-gates) before making changes or repeating the baseline; do not automatically turn analysis into another run:

- **Phase 1:** wrong workspace, virtual environment, or Spikee installation.
- **Phase 2:** target integration, authentication, response shape, or single-/multi-turn behaviour.
- **Phase 3:** missing coverage, unsuitable entries, or incorrect/ambiguous judge definitions.
- **Phase 4:** provider access, timeouts, rate limits, concurrency, retries, or test parameters.

Only after the baseline is trustworthy should you compare vulnerability rates, scale the static run, or consider a compatible dynamic attack.

## 5.1 Obtain the Standard Spikee Summary

Use an exact path. Each `--result-file` accepts one file; repeat the flag for multiple files. Do not rely on a shell wildcard that may expand to several unlabelled positional arguments. Before using `--result-folder`, inspect its contents and make sure every included result belongs in the requested analysis.

```bash
# Full console summary and breakdowns for one run
spikee results analyze --result-file results/results_my_target_cybersec-2026-01_1234567890.jsonl

# Headline statistics only
spikee results analyze --result-file results/results_my_target_cybersec-2026-01_1234567890.jsonl --overview

# Analyse all applicable result artifacts in a deliberately scoped folder
spikee results analyze --result-folder results/

# Create an HTML report next to the input result file
spikee results analyze --result-file results/results_my_target_cybersec-2026-01_1234567890.jsonl --output-format html

# Combine compatible runs into one aggregate analysis
spikee results analyze \
    --result-file results/run1.jsonl \
    --result-file results/run2.jsonl \
    --combine
```

Without `--overview`, console analysis prints the general statistics plus applicable dynamic-attack, category, plugin, language, and other breakdown tables. With multiple inputs and no `--combine`, Spikee analyses each file separately. Combine only when a pooled statistic is meaningful; do not hide differences between incompatible datasets, targets, judges, or application versions.

## 5.2 Understanding the Output

### General Statistics

| Metric | Meaning |
|---|---|
| **Total Unique Entries** | Number of distinct test cases |
| **Successful Attacks (Total)** | Entries where at least one attempt succeeded |
| **Failed Attacks** | Entries where all attempts failed |
| **Errors** | Entries where all attempts errored |
| **Guardrail Triggered** | Entries where all attempts were blocked by guardrail |
| **Total Attempts** | All target requests, including retries and dynamic-attack iterations |
| **Attack Success Rate** | `Successful / Total` — the headline vulnerability metric |

### Dynamic Attack Metrics (if `--attack` was used)

| Metric | Meaning |
|---|---|
| **Initially Successful** | Succeeded with the static payload (before dynamic attack) |
| **Only Successful with Dynamic Attack** | Succeeded only because the attack found a bypass |
| **Attack Success Rate (Improvement)** | Additional vulnerability uncovered by the attack strategy |

Interpret these against the dataset's stated question:

- An **initially successful** instructions-only entry shows direct compliance with a harmful request; it is not a jailbreak bypass, because no jailbreak was required.
- An entry that succeeds **only with the dynamic attack** shows meaningful attack uplift when its matching original attempt was refused.
- For an `--attack-only` run, link it to the prior matching baseline before claiming uplift or a bypass. Without that comparison, report only that the attack-generated attempt succeeded.
- Keep known-prompt resistance, transformed-prompt resistance, and objective-driven adaptive attacks as separate findings rather than combining their rates into one conclusion.

### Breakdown Tables

Results are broken down by **Jailbreak Type**, **Instruction Type**, **Plugin**, and **Language**. Sort by success rate to identify effective attack vectors.

## 5.3 Extract Specific Results

```bash
# Extract all successful attacks to a new file
spikee results extract --result-file results/results_my_target_1234567890.jsonl --category success

# Extract failures
spikee results extract --result-file results/results_my_target_1234567890.jsonl --category failure

# Extract guardrail triggers
spikee results extract --result-file results/results_my_target_1234567890.jsonl --category guardrail

# Custom search — find specific error patterns
spikee results extract --result-file results/results_my_target_1234567890.jsonl \
                       --category custom \
                       --custom-search "error:timeout"

# Custom search on specific field
spikee results extract --result-file results/results_my_target_1234567890.jsonl \
                       --category custom \
                       --custom-search "instruction_type:xss"

# Inverse search (entries that DON'T match)
spikee results extract --result-file results/results_my_target_1234567890.jsonl \
                       --category custom \
                       --custom-search "!jailbreak_type:no-jailbreak"
```

## 5.4 Direct JSONL Inspection

Result files are ordinary JSON Lines: one JSON object per line. Read them directly whenever that is the clearest way to answer the user's actual question. Suitable tasks include locating particular errors, checking the prompts and responses behind a success, grouping by a field the built-in output does not cover, comparing metadata, and manually reviewing impact or judge quality.

Use the smallest reliable query and report its basis—for example, the exact result path, fields inspected, filters applied, and denominator used. Cross-check surprising aggregate findings against `spikee results analyze`. Keep temporary extracts separate and leave the original JSONL unchanged.

## 5.5 Re-Judge Results — Explicit User Choice Only

Re-evaluate existing results with a different judge or LLM model without re-running the test:

Do not re-judge automatically. Run this only after the user explicitly chooses re-judging and the judge provider/model. State why it is proposed and label the resulting analysis with the chosen evaluation configuration. If LLM access is missing or unclear, stop and offer supported hosted-provider or local-endpoint setup options; do not substitute `regex`, `canary`, or a custom judge, and do not rewrite the dataset to make re-judging run.

```bash
# Re-judge with a different LLM
spikee results rejudge --result-file results/results_my_target_1234567890.jsonl \
                       --judge-options "openai/gpt-4o"

# Resume an interrupted re-judge
spikee results rejudge --result-file results/results_my_target_1234567890.jsonl \
                       --judge-options "openai/gpt-4o" \
                       --resume
```

## 5.6 Compare Across Targets

Compare how the same dataset performs against different targets:

```bash
spikee results dataset-comparison \
    --dataset datasets/cybersec-2026-01-1234567800.jsonl \
    --result-file results/results_target-A_1234567890.jsonl \
    --result-file results/results_target-B_1234567891.jsonl \
    --result-file results/results_target-C_1234567892.jsonl \
    --success-threshold 0.8 \
    --success-definition gt
```

This identifies entries that succeed against most targets (threshold > 80%) — these are the most dangerous attacks in your dataset.

To find entries that are hardest to exploit (succeed < 20% of the time):
```bash
spikee results dataset-comparison \
    --dataset datasets/cybersec-2026-01-1234567800.jsonl \
    --result-file results/results_target-A_1234567890.jsonl \
    --result-file results/results_target-B_1234567891.jsonl \
    --success-threshold 0.2 \
    --success-definition lt \
    --number 10
```

## 5.7 HTML and Web UI

Offer the HTML report for a static artifact or the web UI for interactive exploration. `spikee webui` covers result browsing and filtering as well as Generate, Test, and Jobs. It is optional; do not ignore the console summary in favour of launching a service the user did not request.

```bash
spikee webui                              # Default: 127.0.0.1:8080
spikee webui --host 0.0.0.0 -p 8081      # Bind to all interfaces
spikee webui --database jobs.db           # Persist job history
```

Prefer the default loopback binding and tell the user to open `http://127.0.0.1:8080`. Binding to `0.0.0.0` can expose the service to other hosts; explain that and require the user's explicit choice before using it. When the agent launches the UI, the ordinary Spikee command-preview rule applies, but do not create a tmux session for it.

## 5.8 Guardrail Testing — False Positive Analysis

For guardrail targets, run two test sets and combine:

```bash
# 1. Run attack dataset against guardrail
spikee test --dataset datasets/attack-dataset.jsonl \
            --target my_guardrail \
            --threads <agreed-n> \
            --tag attack_results

# 2. Run benign dataset against guardrail
spikee test --dataset datasets/benign-dataset.jsonl \
            --target my_guardrail \
            --threads <agreed-n> \
            --tag benign_results

# 3. Analyse with false positive checks
spikee results analyze \
    --result-file results/results_my_guardrail_attack_results_1234567890.jsonl \
    --false-positive-checks results/results_my_guardrail_benign_results_1234567891.jsonl
```

This produces a **Confusion Matrix** and metrics:
- **Precision** — of blocked prompts, how many were actual attacks?
- **Recall** — of actual attacks, how many were blocked?
- **F1 Score** — harmonic mean of precision and recall
- **Accuracy** — overall correct classification rate

> For the full guardrail testing workflow, read `spikee-src/docs/10_guardrail_testing.md`.

## 5.9 Excel Export

```bash
spikee results convert-to-excel --result-file results/results_my_target_1234567890.jsonl
```

## 5.10 Iteration Guide

Based on results, recommend next steps using the table below. These are proposals, not instructions to execute automatically. Present the findings, ask which follow-up the user wants, and wait unless explicit autopilot covers it. If no follow-up is requested, finish with the findings and leave the workspace ready to resume.

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

After analysis, update the `spikee.log` summary and add a concise analysis/decision entry containing the built-in analysis command and result/report path, only durable conclusions, any material errors or coverage gaps, the user's decision, and the next phase/gate. If a manual JSONL query materially informed the conclusion, record its purpose and sanitized filter briefly rather than its raw output. Do not duplicate detailed evidence already stored in results.

> For complete results documentation, read `spikee-src/docs/11_results.md`.
