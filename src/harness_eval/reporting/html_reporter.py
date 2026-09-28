"""Self-contained, responsive HTML report generator for harness evaluations."""
from pathlib import Path
from typing import Union
from jinja2 import Template
from harness_eval.models import ComparisonReport


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Coding Agent Harness Evaluation Report</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --accent: #818cf8;
      --code-bg: #0b1120;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2rem 1.5rem;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    header { margin-bottom: 2rem; border-bottom: 1px solid var(--card-border); padding-bottom: 1.5rem; }
    h1 { font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem; }
    .meta-bar { display: flex; flex-wrap: wrap; gap: 1.5rem; color: var(--text-muted); font-size: 0.9rem; }
    .badge {
      display: inline-block; padding: 0.25rem 0.6rem; border-radius: 9999px;
      font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    }
    .badge-positive { background: rgba(16, 185, 129, 0.2); color: var(--success); border: 1px solid var(--success); }
    .badge-negative { background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger); }
    .badge-inconclusive { background: rgba(245, 158, 11, 0.2); color: var(--warning); border: 1px solid var(--warning); }
    
    /* Decision Banner */
    .decision-banner {
      background: var(--card-bg);
      border-radius: 12px;
      padding: 1.5rem 2rem;
      margin-bottom: 2rem;
      border-left: 6px solid var(--warning);
    }
    .decision-banner.POSITIVE { border-left-color: var(--success); }
    .decision-banner.NEGATIVE { border-left-color: var(--danger); }
    .decision-banner.INCONCLUSIVE { border-left-color: var(--warning); }
    .decision-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem; }
    .decision-reason { color: #e2e8f0; font-size: 1.05rem; margin-bottom: 1rem; }
    .tradeoffs-list { margin-left: 1.5rem; color: #cbd5e1; font-size: 0.95rem; }
    .tradeoffs-list li { margin-bottom: 0.25rem; }

    /* Section Cards */
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }
    .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; color: var(--primary); }

    /* Metric Grid */
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    .metric-box {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 1rem;
    }
    .metric-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.35rem; }
    .metric-value { font-size: 1.5rem; font-weight: 700; }
    .metric-delta { font-size: 0.85rem; font-weight: 600; margin-top: 0.25rem; }
    .delta-pos { color: var(--success); }
    .delta-neg { color: var(--danger); }
    .delta-neutral { color: var(--text-muted); }

    /* Tables */
    table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.95rem; }
    th { text-align: left; padding: 0.75rem 1rem; background: rgba(15, 23, 42, 0.8); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; }
    td { padding: 0.75rem 1rem; border-top: 1px solid var(--card-border); }
    tr:hover td { background: rgba(51, 65, 85, 0.3); }

    /* Tasks Accordion */
    details {
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      margin-bottom: 1rem;
      overflow: hidden;
    }
    summary {
      padding: 1rem 1.25rem;
      cursor: pointer;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
      user-select: none;
      background: rgba(30, 41, 59, 0.4);
    }
    summary:hover { background: rgba(51, 65, 85, 0.4); }
    .task-details { padding: 1.25rem; border-top: 1px solid var(--card-border); }
    .diff-box {
      background: var(--code-bg);
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 1rem;
      font-family: monospace;
      font-size: 0.85rem;
      overflow-x: auto;
      white-space: pre;
      margin-top: 0.5rem;
      color: #e2e8f0;
    }
    .diff-add { color: #86efac; }
    .diff-rem { color: #fca5a5; }
    .evidence-tag { display: inline-block; background: #334155; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin: 0.2rem; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Coding Agent Harness Evaluation</h1>
      <div class="meta-bar">
        <span><strong>Generated:</strong> {{ report.timestamp }}</span>
        <span><strong>Benchmark:</strong> {{ report.benchmark.benchmark_name }} (v{{ report.benchmark.version }})</span>
        <span><strong>Repetitions:</strong> {{ report.repetitions }}</span>
        <span><strong>Runner:</strong> {{ report.runner_type }}</span>
        <span><strong>Tool Version:</strong> v{{ report.tool_version }}</span>
      </div>
    </header>

    <!-- Decision Banner -->
    <div class="decision-banner {{ report.decision.outcome.value }}">
      <div class="decision-title">
        <span class="badge badge-{{ report.decision.outcome.value | lower }}">{{ report.decision.outcome.value }}</span>
        <span>{{ report.decision.summary_verdict }}</span>
      </div>
      <p class="decision-reason">{{ report.decision.justification }}</p>
      {% if report.decision.trade_offs %}
      <div style="font-weight: 600; margin-bottom: 0.5rem; color: #f1f5f9;">Identified Trade-offs & Limitations:</div>
      <ul class="tradeoffs-list">
        {% for to in report.decision.trade_offs %}
        <li>{{ to }}</li>
        {% endfor %}
      </ul>
      {% endif %}
      {% if report.statistics.significance_note %}
      <p style="margin-top: 0.75rem; font-size: 0.85rem; color: #94a3b8;">
        <strong>Statistical Reliability:</strong> {{ report.statistics.significance_note }}
      </p>
      {% endif %}
    </div>

    <!-- Harness Diff Card -->
    <div class="card">
      <div class="card-title">Harness Configuration Delta</div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
        <div style="padding: 1rem; background: rgba(15,23,42,0.4); border-radius: 8px;">
          <h4 style="color: #cbd5e1; margin-bottom: 0.5rem;">Baseline: {{ report.harness_diff.baseline_name }}</h4>
          <p style="font-size: 0.9rem; color: #94a3b8;"><strong>Model:</strong> {{ report.harness_diff.baseline_model }}</p>
        </div>
        <div style="padding: 1rem; background: rgba(15,23,42,0.4); border-radius: 8px;">
          <h4 style="color: #cbd5e1; margin-bottom: 0.5rem;">Candidate: {{ report.harness_diff.candidate_name }}</h4>
          <p style="font-size: 0.9rem; color: #94a3b8;"><strong>Model:</strong> {{ report.harness_diff.candidate_model }}</p>
          {% if report.harness_diff.skills_added %}
          <p style="font-size: 0.9rem; color: var(--success); margin-top: 0.25rem;"><strong>Skills Added:</strong> {{ report.harness_diff.skills_added | join(', ') }}</p>
          {% endif %}
          {% if report.harness_diff.hooks_added %}
          <p style="font-size: 0.9rem; color: var(--success); margin-top: 0.25rem;"><strong>Hooks Added:</strong> {{ report.harness_diff.hooks_added | join(', ') }}</p>
          {% endif %}
        </div>
      </div>
    </div>

    <!-- Metrics Overview -->
    <div class="card">
      <div class="card-title">Multi-Dimensional Comparison</div>
      <div class="metric-grid">
        {% for delta in report.metric_deltas %}
        <div class="metric-box">
          <div class="metric-label">{{ delta.metric }}</div>
          <div class="metric-value">
            {% if "Rate" in delta.metric or "Compliance" in delta.metric or "Satisfaction" in delta.metric %}
              {{ (delta.candidate * 100) | round(1) }}%
            {% elif "$" in delta.metric %}
              ${{ delta.candidate | round(4) }}
            {% elif "(s)" in delta.metric %}
              {{ delta.candidate | round(1) }}s
            {% else %}
              {{ delta.candidate | round(0) | int }}
            {% endif %}
          </div>
          <div class="metric-delta {% if delta.is_favorable == true %}delta-pos{% elif delta.is_favorable == false %}delta-neg{% else %}delta-neutral{% endif %}">
            {% if "Rate" in delta.metric or "Compliance" in delta.metric or "Satisfaction" in delta.metric %}
              {{ (delta.absolute_delta * 100) | round(1) }}pp (from {{ (delta.baseline * 100) | round(1) }}%)
            {% elif "$" in delta.metric %}
              +${{ delta.absolute_delta | round(4) }} ({{ delta.relative_delta_pct }}%)
            {% elif "(s)" in delta.metric %}
              {{ delta.absolute_delta | round(1) }}s ({{ delta.relative_delta_pct }}%)
            {% else %}
              {{ delta.absolute_delta | round(0) | int }}
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>

      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Baseline</th>
            <th>Candidate</th>
            <th>Absolute Delta</th>
            <th>Relative Delta</th>
          </tr>
        </thead>
        <tbody>
          {% for d in report.metric_deltas %}
          <tr>
            <td><strong>{{ d.metric }}</strong></td>
            <td>
              {% if "Rate" in d.metric or "Compliance" in d.metric or "Satisfaction" in d.metric %}
                {{ (d.baseline * 100) | round(1) }}%
              {% elif "$" in d.metric %}
                ${{ d.baseline | round(4) }}
              {% elif "(s)" in d.metric %}
                {{ d.baseline | round(1) }}s
              {% else %}
                {{ d.baseline | round(0) | int }}
              {% endif %}
            </td>
            <td>
              {% if "Rate" in d.metric or "Compliance" in d.metric or "Satisfaction" in d.metric %}
                {{ (d.candidate * 100) | round(1) }}%
              {% elif "$" in d.metric %}
                ${{ d.candidate | round(4) }}
              {% elif "(s)" in d.metric %}
                {{ d.candidate | round(1) }}s
              {% else %}
                {{ d.candidate | round(0) | int }}
              {% endif %}
            </td>
            <td style="font-weight: 600; color: {% if d.is_favorable == true %}var(--success){% elif d.is_favorable == false %}var(--danger){% else %}inherit{% endif %}">
              {% if "Rate" in d.metric or "Compliance" in d.metric or "Satisfaction" in d.metric %}
                {{ (d.absolute_delta * 100) | round(1) }}pp
              {% elif "$" in d.metric %}
                ${{ d.absolute_delta | round(4) }}
              {% elif "(s)" in d.metric %}
                {{ d.absolute_delta | round(1) }}s
              {% else %}
                {{ d.absolute_delta | round(0) | int }}
              {% endif %}
            </td>
            <td>{{ d.relative_delta_pct }}%</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    <!-- Per-Task Evidence -->
    <div class="card">
      <div class="card-title">Per-Task Evidence & Artifacts</div>
      {% for t in report.task_comparisons %}
      <details>
        <summary>
          <span><strong>{{ t.task_id }}</strong>: {{ t.title }}</span>
          <span>
            <span class="badge {% if t.outcome.value == 'IMPROVED' %}badge-positive{% elif t.outcome.value == 'REGRESSED' %}badge-negative{% else %}badge-inconclusive{% endif %}">
              {{ t.outcome.value }}
            </span>
          </span>
        </summary>
        <div class="task-details">
          <p style="margin-bottom: 0.75rem;"><strong>Analysis:</strong> {{ t.explanation }}</p>
          
          <div style="margin-bottom: 1rem;">
            <strong>Evidence Points:</strong>
            <ul style="margin-left: 1.5rem; margin-top: 0.25rem;">
              {% for ep in t.evidence_points %}
              <li>{{ ep }}</li>
              {% endfor %}
            </ul>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
              <h5 style="color: var(--warning); margin-bottom: 0.25rem;">Baseline Run ({{ t.baseline_run.status.value }})</h5>
              <div style="font-size: 0.85rem; color: #cbd5e1;">
                Tests: {{ t.baseline_run.unit_test_result.passed }}/{{ t.baseline_run.unit_test_result.total }} unit,
                {{ t.baseline_run.holdout_test_result.passed }}/{{ t.baseline_run.holdout_test_result.total }} holdout |
                Cost: ${{ t.baseline_run.estimated_cost }} |
                Time: {{ t.baseline_run.runtime_seconds }}s
              </div>
              <div class="diff-box">{{ t.baseline_run.generated_changes }}</div>
            </div>
            <div>
              <h5 style="color: var(--success); margin-bottom: 0.25rem;">Candidate Run ({{ t.candidate_run.status.value }})</h5>
              <div style="font-size: 0.85rem; color: #cbd5e1;">
                Tests: {{ t.candidate_run.unit_test_result.passed }}/{{ t.candidate_run.unit_test_result.total }} unit,
                {{ t.candidate_run.holdout_test_result.passed }}/{{ t.candidate_run.holdout_test_result.total }} holdout |
                Cost: ${{ t.candidate_run.estimated_cost }} |
                Time: {{ t.candidate_run.runtime_seconds }}s
              </div>
              <div class="diff-box">{{ t.candidate_run.generated_changes }}</div>
            </div>
          </div>
        </div>
      </details>
      {% endfor %}
    </div>

  </div>
</body>
</html>
"""


def export_html_report(
    report: ComparisonReport,
    output_dir: Union[str, Path],
) -> Path:
    """Renders and saves a standalone HTML evaluation report."""
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    template = Template(HTML_TEMPLATE)
    rendered = template.render(report=report)

    html_file = out / "report.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(rendered)

    return html_file
