# Harnesses Directory & Configuration Reference

The `harnesses/` directory contains agent harness configurations. A **harness** defines the operational perimeter, system constraints, instructions, capabilities, and underlying model that govern an LLM coding agent.

---

## 1. Directory Structure

```text
harnesses/
├── baseline/                     # Production reference harness
│   ├── config.yaml               # Harness configuration schema
│   ├── AGENTS.md                 # Agent guidelines and behavioral constraints
│   ├── prompts/
│   │   └── system_prompt.txt     # System prompt template
│   └── skills/
│       └── basic-python.md       # Basic Python skill guide
└── candidate/                    # Candidate harness under evaluation
    ├── config.yaml               # Enhanced configuration schema
    ├── AGENTS.md                 # Updated guidelines with holdout and typing rules
    ├── hooks/
    │   └── pre_commit_lint.sh    # Pre-commit lint validation hook
    ├── prompts/
    │   └── system_prompt.txt     # Strict system prompt template
    └── skills/
        ├── python-testing.md     # Pytest & holdout test verification skill
        └── strict-typing.md      # Type hinting & mypy compliance skill
```

---

## 2. Core Concepts: Baseline vs. Candidate

- **Baseline Harness**: Represents your current production or reference agent setup (e.g., lightweight model `claude-3-5-haiku`, basic prompt instructions, default toolset).
- **Candidate Harness**: Represents an experimental modification (e.g., upgrading to `claude-3-5-sonnet`, adding `strict-typing.md` skill, introducing pre-commit verification hooks, or adjusting prompt guidance).

The objective of `harness-eval` is to verify whether changes in the candidate harness yield statistically reliable improvements without causing unexpected task regressions or unacceptable cost inflation.

---

## 3. Harness Configuration Schema (`config.yaml`)

Every harness directory must contain a valid `config.yaml` file:

```yaml
name: candidate
version: "2.0.0"
description: "Advanced agent harness with rigorous type checking, test-driven validation, and pre-commit verification"
model: "claude-3-5-sonnet-20241022"
temperature: 0.0
max_iterations: 8
system_prompt: "prompts/system_prompt.txt"
agents_file: "AGENTS.md"
skills:
  - "skills/python-testing.md"
  - "skills/strict-typing.md"
tools:
  - "filesystem"
  - "git"
  - "code_search"
  - "database_inspect"
hooks:
  - "hooks/pre_commit_lint.sh"
cost_per_1k_input: 0.003
cost_per_1k_output: 0.015
```

### Parameter Reference

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | *(Required)* | Unique name identifier of the harness configuration. |
| `version` | `string` | `"1.0.0"` | Semantic version string of the harness. |
| `description`| `string` | `""` | Human-readable explanation of harness capabilities and intent. |
| `model` | `string` | *(Required)* | Foundation model identifier (e.g., `claude-3-5-haiku-20241022`, `claude-3-5-sonnet-20241022`, `gpt-4o`). |
| `temperature` | `float` | `0.0` | Sampling temperature for the model. |
| `max_iterations` | `int` | `5` | Maximum agent tool loop iterations allowed per task. |
| `system_prompt` | `string` | `""` | Relative path to system prompt file inside the harness directory. |
| `agents_file` | `string` | `"AGENTS.md"`| Relative path to behavioral guidelines file. |
| `skills` | `list[string]` | `[]` | List of markdown skill files injected into agent context. |
| `tools` | `list[string]` | `[]` | Tool capabilities granted to the agent (`filesystem`, `git`, etc.). |
| `hooks` | `list[string]` | `[]` | Execution scripts invoked at specific lifecycle stages (e.g., pre-commit linters). |
| `cost_per_1k_input` | `float` | `0.0` | Dollar cost per 1,000 input/prompt tokens for the selected model. |
| `cost_per_1k_output` | `float` | `0.0` | Dollar cost per 1,000 output/completion tokens for the selected model. |

---

## 4. Comparing Harnesses via CLI (`diff`)

Before running a benchmark evaluation, inspect the structural differences between baseline and candidate harnesses using `harness-eval diff`:

```bash
harness-eval diff --baseline harnesses/baseline --candidate harnesses/candidate
```

### Sample Diff Output

```text
HARNESS COMPARISON SUMMARY
Baseline : baseline (model: claude-3-5-haiku-20241022)
Candidate: candidate (model: claude-3-5-sonnet-20241022)

Model: claude-3-5-haiku-20241022 -> claude-3-5-sonnet-20241022
Skills:
  + Added:   skills/python-testing.md
  + Added:   skills/strict-typing.md
  - Removed: skills/basic-python.md
Tools:
  + Added:   code_search
  + Added:   database_inspect
Hooks:
  + Added:   hooks/pre_commit_lint.sh
AGENTS.md: Modified between harnesses
```

---

## 5. Creating a New Harness

To create an experimental harness configuration:

1. Create a directory under `harnesses/` (e.g., `harnesses/experimental_v1`).
2. Add a `config.yaml` specifying model, prompt paths, tools, and token pricing.
3. Add custom `AGENTS.md`, system prompt templates, or skill files.
4. Run a side-by-side evaluation against the baseline:

```bash
harness-eval evaluate \
  --baseline harnesses/baseline \
  --candidate harnesses/experimental_v1 \
  --tasks benchmarks/sample/tasks.yaml \
  --output reports/exp_v1
```

For detailed architectural considerations, see [Technical Documentation](file:///d:/Task/chat/docs/Project_Documentation.md).
