# Phase 1 — Workspace Setup

## 1.1 Install Spikee

1. **Check if spikee is installed:** `spikee --help`
2. **Check for existing venv:** `ls -d env/ venv/ .venv/ 2>/dev/null`. If found, activate it and re-check `spikee --help`.
3. **Workspace check:** Look for `datasets/`, `targets/`, `results/`, and `.env`.
4. **Install spikee (preferred via venv):**
```bash
python3 -m venv env
source env/bin/activate
pip install "spikee[all]"
```

*Note: `spikee[all]` installs all provider extras. For specific providers: `pip install "spikee[bedrock,ollama]"`*

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

LLM providers are used for supporting features (LLM judges, dynamic attacks, LLM plugins), not the target itself. Determine if the user plans to use these features. If yes, install the necessary extra and update `.env`.

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

Ensure the **installed** spikee version matches the **bundled** source version in `spikee-src/`:

```bash
python3 -c "import spikee; print(spikee.__version__)"
grep '__version__' spikee-src/spikee/__init__.py
```

If versions differ, **warn the user**. The documentation/source in `spikee-src/` dictates the APIs and options for this skill. Fix by updating the package (`pip install --upgrade spikee`) or the submodule (`cd spikee-src && git pull origin main`).

## 1.5 What's Next?

Spikee is primarily built to help pentesters test **LLM-powered applications** — chatbots, agents, RAG systems, copilots, and any product that wraps an LLM behind application logic. In most engagements, you'll need to write a **custom target** that tells spikee how to talk to the application's endpoints. This is where the skill helps most.

**Most likely: proceed to Phase 2** — work with the user to understand their application's API and write a custom target for it.

Less common scenarios:

| Scenario | What to do |
|---|---|
| Testing a raw LLM inference endpoint directly | Skip to **Phase 3** — use the built-in `llm_provider` target (no custom code needed) |
| Testing a guardrail or content filter in isolation | Proceed to **Phase 2** — write a guardrail target (returns boolean) |
