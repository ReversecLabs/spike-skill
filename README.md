# Spikee Skill for AI Coding Agents

An AI agent skill that guides security testers through LLM application security testing with [Spikee](https://github.com/ReversecLabs/spikee) — from workspace setup, through custom target creation, dataset generation, test execution with dynamic attacks, to results analysis.

## What This Skill Does

When loaded into your AI coding agent, this skill enables it to:

- **Set up a spikee workspace** — install, configure providers, verify environment
- **Write custom targets** — bridge spikee to the application under test (single-turn, multi-turn, guardrail)
- **Generate attack datasets** — from built-in seed folders with plugins, filters, and encoding transforms
- **Run tests with dynamic attacks** — crescendo, best-of-N, LLM jailbreaker, and more
- **Analyse results** — success rates, breakdowns, re-judging, cross-target comparison

The skill includes the full spikee source code and documentation as a local reference checkout, so the agent can read base class contracts, sample implementations, and reference docs on demand.

The workflow is collaborative by default: the agent inspects the current phase, clarifies unresolved decisions, completes agreed work, and checks in before moving to another phase or iteration. Passing a technical check does not authorize the rest of the assessment. Explicitly request autopilot to delegate phase progression and routine decisions within the agreed scope and limits.

## Installation

### Pi

```bash
# Clone into Pi's skills directory
git clone https://github.com/ReversecLabs/spike-skill.git spikee-skill
python3 spikee-skill/skill/update-references.py
cp -r spikee-skill/skill ~/.pi/agent/skills/spikee-skill

# Or symlink (stays in sync with repo updates)
ln -s "$(pwd)/spikee-skill/skill" ~/.pi/agent/skills/spikee-skill
```

### Claude Code

```bash
# Clone and symlink into your project
git clone https://github.com/ReversecLabs/spike-skill.git spikee-skill
python3 spikee-skill/skill/update-references.py
ln -s "$(pwd)/spikee-skill/skill" /path/to/your/project/.claude/skills/spikee-skill
```

### Cursor

```bash
# Clone and symlink into your project
git clone https://github.com/ReversecLabs/spike-skill.git spikee-skill
python3 spikee-skill/skill/update-references.py
ln -s "$(pwd)/spikee-skill/skill" /path/to/your/project/.cursor/rules/spikee-skill
```

### Generic / Other Agents

Point your agent to `skill/SKILL.md` as the skill entry point. The agent needs read access to the entire `skill/` directory including the generated `spikee-src/` reference folder.

## Updating

Fetch the current public Spikee source and documentation before using the skill:

```bash
python3 spikee-skill/skill/update-references.py
```

The references follow upstream `main`; the skill does not pin a Spikee release or
submodule commit. New installations use `pip install -U spikee` for the latest
published package. Reference source and the published package can differ: use the
installed runtime's help and interfaces when writing executable commands. Do not
downgrade an installed package to match reference metadata.

## Skill Structure

```
skill/
├── SKILL.md                    # Entry point — overview + workflow routing
├── 01-workspace-setup.md       # Install, init workspace, configure providers
├── 02-custom-targets.md        # Write targets for the application under test
├── 03-dataset-generation.md    # Seeds, plugins, dataset formats
├── 03b-judges.md               # Judge choice, arguments, version pitfalls, validation
├── 04-testing.md               # Run tests, attacks, judges, runtime options
├── 05-results-analysis.md      # Analyse, extract, re-judge, iterate
└── spikee-src/                 # Current upstream source + docs (generated)
    ├── docs/                   # Official documentation
    ├── spikee/                 # Source code (templates, attacks, plugins, etc.)
    └── workspace/              # Sample implementations
```

## License

This skill is licensed under Apache-2.0. Spikee itself is licensed under its own terms — see [LICENSE.txt](skill/spikee-src/LICENSE.txt).
