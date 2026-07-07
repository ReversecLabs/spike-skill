# Phase 1 — Workspace Setup

## 1.1 Install Spikee

Before installing anything, check the current environment:

**Step 1: Check if spikee is already available.**
```bash
spikee --help
```
If this works, spikee is already installed — skip to **1.2**.

**Step 2: Check for an existing virtual environment.**
Look in the current directory and parent directories for common venv folders:
```bash
ls -d env/ venv/ .venv/ 2>/dev/null
```
If found, activate it and re-check:
```bash
source env/bin/activate   # or venv/bin/activate, .venv/bin/activate
spikee --help
```
If spikee is now available, skip to **1.2**.

**Step 3: Check if the current directory looks like a spikee workspace.**
A spikee workspace has `datasets/`, `targets/`, `results/` directories and a `.env` file. If these exist, a previous user may have set up here — look for a venv before creating a new one.

**Step 4: Install spikee.**
The preferred approach is to create a virtual environment and install spikee into it:
```bash
python3 -m venv env
source env/bin/activate
pip install "spikee[all]"
```

> `spikee[all]` includes all LLM provider extras (Bedrock, Azure, Ollama, Groq, Google). If the user only needs specific providers, install selectively:
> ```bash
> pip install spikee                          # OpenAI-compatible only
> pip install "spikee[bedrock,ollama]"        # Specific providers
> ```

If the user prefers not to use a virtual environment or already has a Python environment they want to use, `pip install "spikee[all]"` works directly — but a venv is strongly recommended to avoid dependency conflicts.

## 1.2 Initialize a Workspace

Create and initialize a workspace directory. All spikee commands must run from here.

```bash
mkdir workspace && cd workspace
spikee init
```

This creates:
```
workspace/
├── datasets/          # Seed folders + generated datasets
├── targets/           # Custom target scripts (your code goes here)
├── attacks/           # Custom attack scripts
├── judges/            # Custom judge scripts (LLM judges)
├── plugins/           # Custom plugin scripts
├── results/           # Test output files
└── .env               # API keys and provider configuration
```

## 1.3 Configure LLM Providers

In a typical pentest engagement, the target under test is an **application** — not a raw LLM endpoint. LLM providers in spikee are used to power **supporting features**, not the target itself:

- **LLM judges** — evaluate whether an attack response indicates success (e.g., `llm_judge_harmful`, `llm_judge_objective`)
- **LLM-powered attacks** — generate adaptive payloads at runtime (e.g., `crescendo`, `llm_jailbreaker`)
- **LLM-powered plugins** — transform payloads using an LLM during dataset generation (e.g., `best_of_n`)

Ask the user: **Are you planning to use any LLM-based judges, attacks, or plugins?** If so, find out which LLM provider they want to use for these. This determines which extras are needed:

| Provider | Install extra | Env vars needed in `.env` |
|---|---|---|
| OpenAI (default, also covers DeepSeek, TogetherAI, OpenRouter) | None — included by default | `OPENAI_API_KEY=sk-...` |
| OpenAI-compatible with custom endpoint | None | `OPENAI_API_KEY=...` + `OPENAI_BASE_URL=https://...` |
| AWS Bedrock | `pip install "spikee[bedrock]"` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` |
| Azure OpenAI | `pip install "spikee[azure]"` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION` |
| Google Gemini | `pip install "spikee[google]"` | `GOOGLE_API_KEY` |
| Groq | `pip install "spikee[groq]"` | `GROQ_API_KEY=gsk_...` |
| Ollama (local, free) | `pip install "spikee[ollama]"` | `OLLAMA_HOST=http://localhost:11434` (optional, defaults to localhost) |

If the user doesn't plan to use LLM judges or attacks (e.g., only using `canary`/`regex` judges and no dynamic attacks), **no provider configuration is needed** — skip to 1.4.

Edit `.env` in the workspace root and add only the relevant keys:
```bash
# Example: using OpenAI for judges and Bedrock for attacks
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

> For full provider details including model identifier formats and supported parameters, read `spikee-src/docs/03_llm_providers.md`.

## 1.4 Verify Setup

```bash
# List available seeds
spikee list seeds

# List available targets, plugins, attacks, judges
spikee list targets
spikee list plugins
spikee list attacks
spikee list judges
spikee list providers
```

> Add `-d` for descriptions: `spikee list targets -d`

### Version Consistency Check

The skill bundles spikee source code and documentation in `spikee-src/`. Verify that the **installed** spikee version matches the **bundled** source version:

```bash
# Get installed version
python3 -c "import spikee; print(spikee.__version__)"

# Get source version from the submodule
grep '__version__' spikee-src/spikee/__init__.py
```

If these versions differ, **warn the user**: the documentation and source code in this skill may not match the installed runtime. The templates, APIs, and options described in the phase files reflect the version in `spikee-src/`. A version mismatch could mean:
- A base class signature has changed
- New options exist that aren't documented here (or vice versa)
- Built-in modules have been added or removed

To resolve: either update the installed package (`pip install --upgrade spikee`) or update the submodule (`cd spikee-src && git pull origin main`).

## 1.5 What's Next?

Spikee is primarily built to help pentesters test **LLM-powered applications** — chatbots, agents, RAG systems, copilots, and any product that wraps an LLM behind application logic. In most engagements, you'll need to write a **custom target** that tells spikee how to talk to the application's endpoints. This is where the skill helps most.

**Most likely: proceed to Phase 2** — work with the user to understand their application's API and write a custom target for it.

Less common scenarios:

| Scenario | What to do |
|---|---|
| Testing a raw LLM inference endpoint directly | Skip to **Phase 3** — use the built-in `llm_provider` target (no custom code needed) |
| Testing a guardrail or content filter in isolation | Proceed to **Phase 2** — write a guardrail target (returns boolean) |
