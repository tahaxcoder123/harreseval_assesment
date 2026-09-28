"""Computes differences between baseline and candidate harnesses."""
import difflib
from pathlib import Path
from typing import List, Optional, Union
from harness_eval.models import HarnessConfig, HarnessDiff


def compute_harness_diff(
    baseline: HarnessConfig,
    candidate: HarnessConfig,
    baseline_dir: Optional[Union[str, Path]] = None,
    candidate_dir: Optional[Union[str, Path]] = None,
) -> HarnessDiff:
    """Analyzes what changed between baseline and candidate configurations."""
    model_changed = baseline.model != candidate.model

    baseline_skills = set(baseline.skills)
    candidate_skills = set(candidate.skills)
    skills_added = sorted(list(candidate_skills - baseline_skills))
    skills_removed = sorted(list(baseline_skills - candidate_skills))

    baseline_tools = set(baseline.tools)
    candidate_tools = set(candidate.tools)
    tools_added = sorted(list(candidate_tools - baseline_tools))
    tools_removed = sorted(list(baseline_tools - candidate_tools))

    baseline_hooks = set(baseline.hooks)
    candidate_hooks = set(candidate.hooks)
    hooks_added = sorted(list(candidate_hooks - baseline_hooks))
    hooks_removed = sorted(list(baseline_hooks - candidate_hooks))

    # Check file contents if directories provided
    agents_changed = False
    prompt_changed = False
    agents_diff_text = ""
    prompt_diff_text = ""

    if baseline_dir and candidate_dir:
        b_dir = Path(baseline_dir)
        c_dir = Path(candidate_dir)

        b_agents = b_dir / baseline.agents_file
        c_agents = c_dir / candidate.agents_file
        if b_agents.exists() and c_agents.exists():
            b_txt = b_agents.read_text(encoding="utf-8")
            c_txt = c_agents.read_text(encoding="utf-8")
            if b_txt != c_txt:
                agents_changed = True

        if baseline.system_prompt and candidate.system_prompt:
            b_prompt = b_dir / baseline.system_prompt
            c_prompt = c_dir / candidate.system_prompt
            if b_prompt.exists() and c_prompt.exists():
                bp_txt = b_prompt.read_text(encoding="utf-8")
                cp_txt = c_prompt.read_text(encoding="utf-8")
                if bp_txt != cp_txt:
                    prompt_changed = True

    # Build human-readable summary
    lines: List[str] = [
        "HARNESS COMPARISON SUMMARY",
        f"Baseline : {baseline.name} (model: {baseline.model})",
        f"Candidate: {candidate.name} (model: {candidate.model})",
        "",
    ]

    if model_changed:
        lines.append(f"Model: {baseline.model} -> {candidate.model}")

    if skills_added or skills_removed:
        lines.append("Skills:")
        for s in skills_added:
            lines.append(f"  + Added:   {s}")
        for s in skills_removed:
            lines.append(f"  - Removed: {s}")

    if tools_added or tools_removed:
        lines.append("Tools:")
        for t in tools_added:
            lines.append(f"  + Added:   {t}")
        for t in tools_removed:
            lines.append(f"  - Removed: {t}")

    if hooks_added or hooks_removed:
        lines.append("Hooks:")
        for h in hooks_added:
            lines.append(f"  + Added:   {h}")
        for h in hooks_removed:
            lines.append(f"  - Removed: {h}")

    if agents_changed:
        lines.append("AGENTS.md: Modified between harnesses")
    if prompt_changed:
        lines.append("System Prompt: Modified between harnesses")

    summary_text = "\n".join(lines)

    return HarnessDiff(
        baseline_name=baseline.name,
        candidate_name=candidate.name,
        model_changed=model_changed,
        baseline_model=baseline.model,
        candidate_model=candidate.model,
        skills_added=skills_added,
        skills_removed=skills_removed,
        tools_added=tools_added,
        tools_removed=tools_removed,
        hooks_added=hooks_added,
        hooks_removed=hooks_removed,
        agents_file_changed=agents_changed,
        system_prompt_changed=prompt_changed,
        summary_text=summary_text,
    )
