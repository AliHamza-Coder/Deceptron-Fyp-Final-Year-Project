# Phase 1: analysis-ui-output-enhancement - Research

**Researched:** 2026-03-24
**Domain:** Static multi-page HTML/CSS/JS UI enhancement for analysis outputs
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Bottom Output Layout
- **D-01:** Use a fixed 3-card bottom layout on all target pages.
- **D-02:** The cards are consistently ordered as: **Output Context** -> **Description** -> **Analysis %**.
- **D-03:** The bottom section must be visible as a unified analysis block, not split into tabs.

### Metric Visualization Style
- **D-04:** Use a hybrid visualization style.
- **D-05:** Show one primary metric as a prominent horizontal bar with large percentage.
- **D-06:** Show 2-3 secondary metrics as compact radial indicators.
- **D-07:** Preserve threshold color semantics (green/amber/red) for quick interpretation.

### Description Content Rules
- **D-08:** Description area includes a short paragraph summary.
- **D-09:** Include 3 key bullet findings under the summary.
- **D-10:** Include a final verdict badge line (for example: "Final Verdict: High Lying Risk").

### Reports Alignment
- **D-11:** Apply a hybrid alignment strategy for reports.
- **D-12:** Reuse the same metric card style and output language across report pages and analysis pages.
- **D-13:** Keep report-specific page layout structure intact (do not force full page layout parity with live/facial pages).

### Claude's Discretion
- Spacing scale and exact typography values for card internals.
- Exact icon set and micro-animation behavior.
- Responsive stacking behavior for narrow widths.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LIVE-01 | Dedicated bottom analysis block with output context, summary, percentages | Fixed 3-card bottom section pattern with strict card order and shared heading block |
| LIVE-02 | Risk/result percentages in high-contrast visual components | One primary horizontal bar + 2-3 compact radial indicators with threshold colors |
| LIVE-03 | Transcript/reasoning to final percentage in one viewport | Keep middle transcript/reasoning row, redesign only bottom section; no modal/tab split |
| FACE-01 | Clear bottom result section with context/findings/percentages | Mirror live-session bottom structure in facial page with same content hierarchy |
| FACE-02 | Comparable indicators + final percentages with consistent labels | Shared metric naming + same visual hierarchy (primary metric first, secondary metrics grouped) |
| FACE-03 | Styling consistency with live-session outputs | Reuse glass-card, theme token, and status color semantics already present |
| REPT-01 | Improved report summary blocks with clearer percentages/status labels | Apply same metric card visual language in report cards/detail summary sections |
| REPT-02 | At-a-glance verdict + description + percentages | Unified verdict badge line + short summary + bullet findings in report detail |
| REPT-03 | Consistent output language across report list/detail | Define shared wording schema (Output Context, Description, Analysis %) used in both pages |
| CONS-01 | Cross-page consistent structure: context, description, percentages | Enforce invariant card order and shared section labels across all 4 target pages |
| CONS-02 | Typography/spacing/color readable in dark & light themes | Reuse existing token-driven light-mode overrides and avoid hardcoded one-theme-only text colors |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

No `.cursor/rules/` directory exists in this repository (verified).  
Operational constraints come from existing codebase conventions and phase context documents.

## Summary

Phase 1 is a presentation-layer enhancement in an existing static HTML/CSS/JS architecture. The safest approach is to standardize a reusable UI pattern (same section structure and semantic labels) while leaving each page's existing layout flow intact. The phase should avoid introducing new frameworks, avoid backend changes, and focus on bottom-block structure, metric readability, and language consistency.

Current pages already contain most primitives needed: glass cards, dark/light token system, Chart.js donut/radar/line usage, and color-coded status text. The research indicates implementation should be additive and compositional: replace or refactor only the bottom result sections in `live-session.html` and `facial-expression.html`, and align report summary/detail blocks (`reports.html`, `report-detail.html`) to the same content contract.

Validation should prioritize visual/behavioral consistency checks over algorithmic tests. This repo currently lacks test infrastructure, so Wave 0 planning must include minimal validation scaffolding (or an explicit manual-only strategy for UI verification) before coding tasks claim completion.

**Primary recommendation:** Implement a shared "3-card analysis output contract" across target pages using existing theme tokens and Chart.js, with no backend/API changes.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| HTML5 + vanilla JS | Browser-native | Page structure and behavior | Matches current architecture (`web/pages/*.html` with inline scripts) |
| Tailwind-style utility CSS via `output.css` | Project-local build output | Fast visual composition and spacing/typography consistency | Already dominant styling pattern across target files |
| CSS custom properties (theme tokens) | Browser-native | Dark/light theme consistency | Existing pages already rely on tokenized colors/backgrounds |
| Chart.js | Bundled local `../scripts/chart.min.js` | Radial/line/bar metric visualizations | Already loaded and used in all relevant analysis/report pages |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Font Awesome | Bundled local `../vendor/font-awesome` | Status/icons in cards and headers | For semantic icon cues in output context/summary cards |
| Eel JS bridge (`/eel.js`) | Runtime-provided | Session/user checks and host integration | Keep existing session/auth flow unchanged while updating UI only |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Inline page-specific card markup | Shared JS component renderer | Better consistency, but adds refactor risk in this phase |
| Chart.js donuts + bars | SVG-only custom charts | More control but unnecessary hand-rolled complexity now |
| Existing token classes | Hardcoded per-page colors | Faster short-term but breaks cross-page and theme consistency |

**Installation:**
```bash
# No new dependencies required for this phase.
```

**Version verification:**  
Package-registry version checks are not applicable in this phase because dependencies are vendored/local and phase scope is UI structure enhancement only (no dependency changes planned).

## Architecture Patterns

### Recommended Project Structure
```text
web/pages/
├── live-session.html        # Replace bottom result row with 3-card contract
├── facial-expression.html   # Mirror same contract and metric hierarchy
├── reports.html             # Align report card summary language and metric visual emphasis
└── report-detail.html       # Align detail summary block to same output contract
```

### Pattern 1: Unified Bottom Analysis Contract
**What:** One bottom section with 3 ordered cards: Output Context -> Description -> Analysis %.  
**When to use:** On all target analysis/report surfaces where final output is presented.  
**Example:**
```html
<!-- Source: project page patterns in web/pages/live-session.html -->
<section class="px-4 pb-8 space-y-6">
  <h2 class="text-[11px] font-bold uppercase tracking-[0.3em]">
    AI Analysis Results
  </h2>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <article class="glass p-6">Output Context</article>
    <article class="glass p-6">Description</article>
    <article class="glass p-6">Analysis %</article>
  </div>
</section>
```

### Pattern 2: Hybrid Metric Emphasis
**What:** One dominant linear percentage bar + 2-3 compact radial indicators.  
**When to use:** Any result area where a primary risk/finality metric exists with supporting signals.  
**Example:**
```html
<!-- Source: existing chart + progress-bar usage in target pages -->
<div class="space-y-3">
  <p class="text-xs font-bold">Primary Risk Score</p>
  <div class="h-2 bg-white/5 rounded-full overflow-hidden">
    <div class="h-full bg-rose-500" style="width: 82%"></div>
  </div>
  <canvas id="secondaryMetricRadialA"></canvas>
  <canvas id="secondaryMetricRadialB"></canvas>
</div>
```

### Pattern 3: Theme-Token-First Styling
**What:** Use CSS variables and existing light-mode override classes, not isolated hardcoded values.  
**When to use:** All new cards, text, borders, and status colors in this phase.  
**Example:**
```css
/* Source: existing token usage in all target pages */
.analysis-card {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  color: var(--text-main);
}
```

### Anti-Patterns to Avoid
- **Tab/modals for bottom output:** Violates D-03 and breaks "one viewport interpretation."
- **Page-specific wording drift:** Causes CONS-01/REPT-03 failure even if visuals look improved.
- **One-theme tuning only:** Hardcoded dark values will regress light-mode readability.
- **Backend coupling for UI-only phase:** Adds regression risk beyond scope.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Radial metric rendering | Custom canvas arc drawing engine | Existing Chart.js doughnut charts | Already integrated; avoids custom math/resize/legend edge cases |
| Theme management | New theme state system | Existing `localStorage` + `body.light-mode` pattern | Current pages already rely on it; avoid split theme logic |
| Cross-page UI framework | New component framework for one phase | Existing static page pattern + shared class contracts | Faster delivery and lower integration risk |

**Key insight:** The codebase already has rendering and theming primitives; custom infrastructure here adds complexity without requirement value.

## Common Pitfalls

### Pitfall 1: Inconsistent Card Order Across Pages
**What goes wrong:** One page shows percentages first while another follows context-first order.  
**Why it happens:** Manual page edits without a shared output contract checklist.  
**How to avoid:** Enforce D-02 card order in every target page task acceptance criteria.  
**Warning signs:** QA screenshots show same labels but different visual order.

### Pitfall 2: Theme Readability Regression
**What goes wrong:** Text/badge contrast degrades in light mode.  
**Why it happens:** Added utility classes are dark-biased and not covered by light overrides.  
**How to avoid:** For every new class/color, confirm light-mode override or token-based style path.  
**Warning signs:** Gray text on light card backgrounds or faded status badges.

### Pitfall 3: Metric Semantics Drift
**What goes wrong:** Red/amber/green meanings change between pages, confusing interpretation.  
**Why it happens:** Independent per-page color choices during quick UI iteration.  
**How to avoid:** Define one semantic map (critical/warning/safe) and reuse everywhere.  
**Warning signs:** "High risk" appears in non-alert color or status badges conflict with chart colors.

### Pitfall 4: Over-refactor Beyond Scope
**What goes wrong:** Session/auth/recording logic is touched for a UI-only phase, creating regressions.  
**Why it happens:** Editing large inline-script pages without isolating visual sections.  
**How to avoid:** Restrict code changes to output-rendering blocks and style fragments only.  
**Warning signs:** Diffs include `eel.*` calls, upload logic, or device selection behavior.

## Code Examples

Verified in-repo patterns to reuse directly:

### Existing Theme Toggle Pattern
```javascript
const themeToggle = document.getElementById("theme-toggle");
function toggleTheme() {
  const isLight = body.classList.toggle("light-mode");
  localStorage.setItem("theme", isLight ? "light" : "dark");
}
```

### Existing Hybrid Metric Building Blocks
```html
<!-- Bar metric -->
<div class="h-1 bg-white/5 rounded-full overflow-hidden">
  <div class="h-full bg-cyan-500" style="width: 45%"></div>
</div>

<!-- Radial metric -->
<canvas id="deceptionPieChart"></canvas>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-page custom output blocks with varied language | Unified output contract with fixed section order | Phase 1 target | Improves scanability and cross-page learnability |
| Equal visual weight for all metrics | Primary + secondary metric hierarchy | Phase 1 target | Faster interpretation of final verdict |
| Isolated report styling language | Shared analysis/report language model | Phase 1 target | Better consistency from live analysis to archived reports |

**Deprecated/outdated:**
- Ad-hoc output wording per page: replaced by contract-driven labels and verdict phrasing.

## Open Questions

1. **Exact responsive breakpoint behavior for 3 cards**
   - What we know: Responsive stacking is discretionary and required for narrow widths.
   - What's unclear: Specific breakpoints for 3->2->1 card transitions per page.
   - Recommendation: Decide one breakpoint matrix during planning and apply consistently.

2. **Primary metric naming standard**
   - What we know: Must emphasize final percentage with threshold semantics.
   - What's unclear: Whether label should be "Lying Risk", "Truth Score", or context-dependent alias.
   - Recommendation: Use one canonical label plus optional subtitle mapping per page type.

## Environment Availability

Step 2.6: SKIPPED (no external dependencies identified).  
This phase is code/config-only within existing static HTML/CSS/JS pages and bundled local assets.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected |
| Config file | none — see Wave 0 |
| Quick run command | `python -m pytest -q` (if pytest is installed in Wave 0) |
| Full suite command | `python -m pytest` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LIVE-01 | Bottom 3-card output block appears in live session | integration/UI smoke | `python -m pytest tests/ui/test_live_session_output.py -k bottom_block -q` | ❌ Wave 0 |
| LIVE-02 | Percentages rendered in high-contrast visuals | integration/UI smoke | `python -m pytest tests/ui/test_live_session_output.py -k percentages -q` | ❌ Wave 0 |
| LIVE-03 | Transcript/reasoning + final output visible in one viewport | integration/UI smoke | `python -m pytest tests/ui/test_live_session_output.py -k one_viewport -q` | ❌ Wave 0 |
| FACE-01 | Bottom result section with required structure | integration/UI smoke | `python -m pytest tests/ui/test_facial_output.py -k structure -q` | ❌ Wave 0 |
| FACE-02 | Indicator hierarchy consistent with labels | integration/UI smoke | `python -m pytest tests/ui/test_facial_output.py -k hierarchy -q` | ❌ Wave 0 |
| FACE-03 | Styling consistency with live session outputs | visual regression/manual-assisted | `python -m pytest tests/ui/test_facial_output.py -k consistency -q` | ❌ Wave 0 |
| REPT-01 | Report summary blocks emphasize percentages/status | integration/UI smoke | `python -m pytest tests/ui/test_reports_output.py -k summary -q` | ❌ Wave 0 |
| REPT-02 | Verdict + description + percentages visible at a glance | integration/UI smoke | `python -m pytest tests/ui/test_report_detail_output.py -k verdict -q` | ❌ Wave 0 |
| REPT-03 | Report list/detail language consistency | integration/UI smoke | `python -m pytest tests/ui/test_reports_output.py -k language -q` | ❌ Wave 0 |
| CONS-01 | Cross-page content structure consistency | integration/UI smoke | `python -m pytest tests/ui/test_cross_page_consistency.py -k structure -q` | ❌ Wave 0 |
| CONS-02 | Readability maintained in dark/light modes | visual regression/manual-assisted | `python -m pytest tests/ui/test_cross_page_consistency.py -k theme -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ui -k "live or face or report or consistency" -q`
- **Per wave merge:** `python -m pytest tests/ui`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/ui/test_live_session_output.py` — covers LIVE-01..03
- [ ] `tests/ui/test_facial_output.py` — covers FACE-01..03
- [ ] `tests/ui/test_reports_output.py` — covers REPT-01..03
- [ ] `tests/ui/test_report_detail_output.py` — covers REPT-02
- [ ] `tests/ui/test_cross_page_consistency.py` — covers CONS-01..02
- [ ] `tests/conftest.py` — shared DOM fixture loader for static HTML assertions
- [ ] Framework install: `pip install pytest beautifulsoup4`

## Sources

### Primary (HIGH confidence)
- `.planning/phases/01-analysis-ui-output-enhancement/01-CONTEXT.md` - locked decisions and scope constraints
- `.planning/REQUIREMENTS.md` - requirement definitions (LIVE/FACE/REPT/CONS)
- `.planning/ROADMAP.md` - phase goal, mapped requirements, success criteria
- `.planning/codebase/ARCHITECTURE.md` - architecture and integration boundaries
- `.planning/codebase/STRUCTURE.md` - file ownership and current test-infra absence
- `.planning/codebase/CONVENTIONS.md` - naming/style/error-handling conventions
- `web/pages/live-session.html` - current bottom output + chart/theme implementation patterns
- `web/pages/facial-expression.html` - current facial metrics + live output structure
- `web/pages/reports.html` - report list language/status/mini-chart patterns
- `web/pages/report-detail.html` - detailed verdict/metric/transcript presentation patterns
- `.planning/config.json` - nyquist validation enabled (`workflow.nyquist_validation: true`)

### Secondary (MEDIUM confidence)
- None (no external-doc-dependent claims needed for this phase research)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - derived directly from current repository implementation and phase scope
- Architecture: HIGH - backed by architecture/structure docs + target page source
- Pitfalls: MEDIUM-HIGH - based on observed code duplication and theme variance patterns

**Research date:** 2026-03-24
**Valid until:** 2026-04-23
