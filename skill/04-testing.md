# Phase 4 — Testing

Run attack datasets against your target using `spikee test`.

This is the only default execution path for adversarial testing, including one-off trial prompts. Do not manually invoke adversarial inputs through `spikee debug`, a standalone harness, direct target calls, the application UI, browser/Playwright, Burp Repeater, `curl`, or ad hoc scripts, and do not invent attacks outside the agreed dataset/plugin/attack workflow. If Spikee cannot express the requested test, return to the phase that owns the missing target, seed, plugin, attack, or judge capability and ask the user how to proceed.

Only perform manual or out-of-band testing when the user explicitly requests that deviation. Treat it as a narrow exception: confirm its scope and limits, perform only the agreed attempt, and do not invent extra payloads or iterative follow-ups without further approval. Keep its evidence separate from Spikee results, record a concise sanitized `manual deviation` entry in `spikee.log`, and never merge it into Spikee success rates.

> **Workspace memory:** Read `spikee.log` before selecting a command so completed baselines, known limits, and prior result paths are not rediscovered or rerun blindly.

This guide, `spikee list attacks -d`, and examples in the initialized workspace are sufficient for routine test and attack setup. Consult `spikee-src/docs/08_dynamic_attacks.md` when a documented option is unclear. Do not read attack implementation source merely to start a built-in attack; inspect it only for unresolved behavior or debugging.

## Required Testing Sequence

Do not skip ahead when a gate is unresolved:

1. **Check readiness.** Confirm the workspace-local virtual environment is active; the target works for a representative request; the intended dataset and its judges are understood; and required credentials/endpoints are available.
2. **Run a small static baseline.** Use the real target and unchanged dataset without `--attack`, with conservative concurrency and a reproducible sample.
3. **Analyse that baseline in Phase 5.** It is sound only when target responses and judge decisions are valid, errors are acceptably low, and the sample covers the intended categories.
4. **Return to the phase that owns any problem and repeat.** Use Phase 1 for workspace issues, Phase 2 for target issues, or Phase 3 for dataset/judge-definition issues.
5. **Then scale deliberately.** Run the full static dataset if needed. Use a dynamic attack only when the baseline is sound and the target, provider, and agreed limits are compatible.

Example smoke baseline:

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --sample 0.05 \
            --sample-seed 42 \
            --threads 1 \
            --tag baseline-smoke
```

Adjust the sample to remain small but representative. Do not interpret or scale a run with judge failures, malformed/empty target responses, widespread request errors, or missing category coverage.

## 4.1 Basic Test Command

```bash
spikee test --dataset "datasets/cybersec-2026-01-*.jsonl" \
            --target my_app_target
```

**Key flags:**
- `--dataset <file>`: Path to dataset JSONL. **Supports glob patterns** (e.g., `datasets/*.jsonl`) — remember to quote the glob so the shell doesn't expand it prematurely if passing multiple files.
- `--dataset-folder <dir>`: Process all datasets in a folder.
- `--target <name>`: Target module name (without `.py`).
- `--target-options <string>`: Options to pass to the target (e.g., `provider/model`).
- `--tag <string>`: Tag for the results filename.

## 4.2 Using the Built-In LLM Target

For testing raw LLM endpoints without writing a custom target:

```bash
# OpenAI
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "openai/gpt-4o-mini"

# Bedrock
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "bedrock/anthropic.claude-3-sonnet-20240229-v1:0"

# Ollama (local)
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "ollama/llama3"

# Google Gemini
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "google/gemini-1.5-flash"
```

> For the full provider/model list, read `spikee-src/docs/03_llm_providers.md`.

## 4.3 Judges — How Success is Determined

Every dataset entry has a `judge_name` field that determines how Spikee evaluates whether an attack succeeded.

### Built-In Basic Judges (No LLM required)

- `canary`: Checks if `judge_args` string appears in the response (case-insensitive).
- `regex`: Checks if `judge_args` regex pattern matches the response.

*Note: These judges run locally and do **not** require `--judge-options`.*

### LLM Judges (Requires `--judge-options`)

- `llm_judge_harmful`: Evaluates for harmful content.
- `llm_judge_objective`: Evaluates if the specific objective in `judge_args` was achieved.
- `llm_judge_output_criteria`: Evaluates custom criteria from `judge_args`.
- `llm_judge_output_only`: Like output_criteria but only sees the response (not the prompt).

*Note: These judges require an LLM to perform semantic evaluation. You **must** provide the `--judge-options` flag.*

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --judge-options "openai/gpt-4o-mini"
```

Preserve the dataset's intended judge semantics. If an LLM judge is required but its provider/model or access is unresolved, stop and ask the user to choose a supported hosted provider/model or a configured local endpoint. Explain the needed `.env` credentials when applicable. **Do not** replace the LLM judge with `regex`/`canary`, edit `judge_name`, or create a custom judge merely to bypass missing LLM access. Present the configuration options and wait for the user's choice. If the user deliberately wants to redesign the evaluation, return to Phase 3, agree the exact judge semantics, update the source seeds, regenerate the dataset, and repeat the baseline.

### Custom Judges

Create or change a custom judge only when the user explicitly wants a custom evaluation rule—not as a workaround for an unavailable LLM judge.

Create in `judges/` in your workspace:

```python
# judges/my_custom_judge.py
from spikee.templates.judge import Judge
from spikee.utilities.hinting import ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag

class MyCustomJudge(Judge):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.SINGLE], "My custom judge"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def judge(self, prompt, response, judge_args, judge_options=None) -> bool:
        """Return True if the attack succeeded, False otherwise."""
        return "SECRET_DATA" in str(response)
```

> Start with the initialized workspace's `judges/` examples and `spikee-src/docs/09_judges.md`. Inspect judge base-class source only for an unresolved custom-judge contract or debugging issue.

## 4.4 Dynamic Attacks

Attacks are adaptive strategies that modify payloads in real-time. They run **only when the standard attempt fails** (unless `--attack-only` is used).

Do not add a dynamic attack to the smoke baseline. Before using one, confirm all of the following:

- the static baseline passed the analysis gate above;
- the attack matches the target's single-turn or multi-turn interface;
- any attack-side model/provider and credentials or local endpoint are configured;
- request rate, concurrency, iteration, time, and cost limits are known and acceptable.

If any item is unclear, stop and present the missing decision or configuration instead of guessing. Use `--attack-only` only when the user deliberately wants to omit the standard attempt after a valid baseline exists.

```bash
# Crescendo is only for a verified multi-turn target
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_chatbot_target \
            --attack crescendo \
            --attack-iterations 10
```

### Single-Turn Attacks

| Attack | Strategy | Options |
|---|---|---|
| `best_of_n` | Randomly perturbs the payload N times | `model=`, `variants=` |
| `random_suffix_search` | Appends random suffixes to find bypasses | — |
| `prompt_decomposition` | Breaks the prompt into sub-questions | `model=` |
| `llm_jailbreaker` | Uses an LLM to rephrase the attack | `model=` |
| `llm_multi_language_jailbreaker` | Translates attacks to different languages | `model=`, `language=` |
| `anti_spotlighting` | Counters document-spotlighting defences | `model=` |
| `rag_poisoner` | Crafts adversarial context for RAG systems | `model=` |

### Multi-Turn Attacks (Require Multi-Turn Target)

| Attack | Strategy | Options |
|---|---|---|
| `crescendo` | Gradually escalates through conversation turns | `model=`, `max-turns=` |
| `echo_chamber` | Manipulates the model through contradictions/echoes | `model=`, `max-turns=` |
| `multi_turn` | Simple multi-turn with pre-defined conversation flow | — |

```bash
# Multi-turn attack with options
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_chatbot_target \
            --attack crescendo \
            --attack-iterations 15 \
            --attack-options "model=openai/gpt-4o-mini,max-turns=5"
```

> List available attacks: `spikee list attacks -d`
> If this guide and the list output are insufficient, read `spikee-src/docs/08_dynamic_attacks.md`. Inspect `spikee-src/spikee/templates/attack.py` only when implementing a custom attack and the documented contract remains unclear, or when debugging.
> **Advanced:** To configure a custom GOAT (Generative Offensive Adversarial Toolkit) attack with specific guardrail mapping, refer to **`04b-goat-attack.md`**.

### Attack-Only Mode

Skip the initial standard attempt and only run the dynamic attack:
```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --attack crescendo \
            --attack-only
```

## 4.5 Runtime Parameters

- `--threads <n>`: Parallel threads (default: 4)
- `--attempts <n>`: Retry attempts per entry (default: 1)
- `--max-retries <n>`: Retries for 429/transient errors (default: 3)
- `--throttle <seconds>`: Wait time between requests per thread
- `--sample <percentage>`: Sample percentage of dataset (e.g., `0.15` for 15%)
- `--sample-seed <n>`: Seed for reproducible sampling (default: 42, or "random")

## 4.6 Resume and Re-run

Spikee auto-detects previous results files and offers to resume:

```bash
# Auto-resume from latest matching results file
spikee test --dataset datasets/my-dataset.jsonl --target my_target --auto-resume

# Resume from a specific file
spikee test --dataset datasets/my-dataset.jsonl --target my_target \
            --resume-file results/results_my_target_cybersec-2026-01_1234567890.jsonl

# Force fresh start (no resume)
spikee test --dataset datasets/my-dataset.jsonl --target my_target --no-auto-resume
```

## 4.7 Writing Custom Attacks

Create in `attacks/` in your workspace:

```python
# attacks/my_attack.py
from spikee.templates.attack import Attack
from spikee.utilities.hinting import ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag

class MyAttack(Attack):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.SINGLE], "My custom attack strategy"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def attack(self, entry, target, judge_fn, max_iterations, pbar, lock, attack_option=None):
        """Run the attack strategy.

        Args:
            entry: Dataset entry dict with 'text', 'judge_name', 'judge_args', etc.
            target: AdvancedTargetWrapper instance — call target.process_input(text)
            judge_fn: Judge function — call judge_fn(entry, response) → bool
            max_iterations: Maximum iterations allowed (from --attack-iterations)
            pbar: tqdm progress bar (update with lock)
            lock: threading.Lock for thread-safe progress updates

        Returns:
            tuple: (attempts_count, success_bool, final_input, final_response)
        """
        for i in range(max_iterations):
            # Modify the payload
            modified_text = f"Please help me with: {entry['text']}"

            try:
                response, meta = target.process_input(modified_text)
                with lock:
                    pbar.update(1)

                if judge_fn(entry, response):
                    return i + 1, True, modified_text, response
            except Exception:
                with lock:
                    pbar.update(1)

        return max_iterations, False, modified_text, ""
```

> Start with `attacks/sample_attack.py` in the initialized workspace and the official dynamic-attack guide. Inspect built-in attack source only if a concrete implementation question remains or observed behavior needs debugging.

The Spikee attack engine calls `target.process_input(...)` in this class. Do not run a custom attack class as a standalone client or use its target calls to conduct manual testing.

After each material baseline, full, or dynamic-attack run, update the `spikee.log` summary and add one concise test activity entry: ISO timestamp, reproducible command with secrets redacted, target/dataset, judge and attack configuration, completion or error status, result path, and next gate. Record an explicitly requested manual deviation as a separate activity type, never as a Spikee run. Do not paste console output or result contents into the log.

## 4.8 Next Step

Once your test run completes, proceed to **Phase 5** to analyse the results.
