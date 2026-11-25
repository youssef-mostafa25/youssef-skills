---
name: tabbed-explainer
description: Use when the user asks for an HTML artifact, page, explainer, report, write-up, overview or visual summary to read or share, such as "make an artifact explaining X", "put this in a page for the team", "tabbed explainer", "design artifact", "visualise this", or when findings, a plan, numbers or an architecture would be clearer as a page than as terminal text. Not for the merge review page of integration-assistant or the status board of plan-build-board, which have their own templates.
---

# tabbed-explainer

Build a **tabbed** HTML artifact that explains one subject the sha3bolly way, with the
right visual wherever a picture says it faster than words. Every visual comes from this
skill's `visuals/` folder: the user hand-picked each one for the situations listed below.

**Invoke the `sha3bolly` skill (via the Skill tool) before anything else.** Its rules
govern every word on the page: the point first, plain words, a concrete example for
every explanation, and a flow for anything with chained steps.

## The page, part by part

Build the page from `page-template.html` (next to this file). It is made of these parts,
in this order:

1. **Header.** An eyebrow (topic · date), the page's question or point as the `h1`, and a
   two-line lede that gives the answer first, with the key numbers in the sentence
   ("Round 4 finds 98.9 of every 100 items the agent needs, up from 38.2, at 4–6× the
   search time."). There are no stat tiles anywhere on the page.
2. **Tab bar.** Tabs, never one long scrolling page. Choose the tabs from the content:
   one tab per thing a reader would come to look for (for example *How it works*,
   *Numbers*, *The choice*, *Shipping it*). Usually 3 to 6 tabs, named in plain words,
   each with a 2–4 word sub-label. The first tab is what most readers need first. Each
   tab's `data-tab` slug is also its `#hash`, so a tab can be linked.
3. **Panels.** One per tab. Each section inside a panel has, in order:
   - a heading;
   - a `.point` box: the conclusion to remember, as one sentence;
   - for a section that explains **how something works**, a concrete example (a real
     question, request, query or row from the material, in a `pre.code` or a short
     sentence). If the material has none, write one and label it "Illustration";
   - its visual (see *Choosing the visual*). The visual's title says what to look at in it
     ("All rerankers sit 2 s left of the LLM ranker, and 6–14 points lower"), not the
     point box again;
   - long detail as tables or lists under the visual, not above it.
4. **A choice, when the page has one.** When the reader has to decide something, that
   gets its own tab: the options side by side (an options table or the `outcome-grid`
   visual), **your recommendation stated plainly with the reason**, and what happens
   after each choice. Laying the options out "neutrally" with no recommendation is not
   enough.

## Choosing the visual

Name the situation each section is in, then use a visual listed for it. Open only the
snippet files you use (`visuals/<slug>.html`); each starts with a comment saying when to
use it and what to fill.

| Situation | Visual (slug) and what it answers |
|---|---|
| **What must happen first** (prerequisites, ship order) | `dependency-graph`: the first choice whenever items depend on each other |
| **How the system is built** (services, layers) | `blueprint`: layers and the links between them, drawn dark in both themes |
| **How parts connect**, other shapes | `many-to-one` (many callers → one seam → many providers), `data-model` (records and typed links), `swimlane-grid` (who hands what to whom, per milestone) |
| **Steps of a process** | `pipeline` (one or two labelled rows of steps), `count-funnel` (how many survive each step) |
| **Before → after** | `today-after` (a flow, today vs after), `progress-list` (a number per item, before → after) |
| **Who calls whom, in order** | `sequence-phased` (any number of steps; use one phase band when there are few), `case-timelines` (what happens to one request in two cases) |
| **Compare options** | `scatter-ref` (options on two measures), `bars-limit` (one measure, with a limit), `progress-list` (many measures, before → after) |
| **Change along a scale or over time** | `multi-line` (one or more series, optional dashed ceiling) |
| **Parts of a whole** | `stacked-rows` (one row per total; one row for a single total; one row per step for "found vs missed after each step") |
| **How long each thing takes** | `step-durations` |
| **Schedule / who does what when** | `swimlane-grid`, `case-timelines` |
| **Hierarchy / tree** | `tree`, `data-model` |
| **Status / risk** against a limit | `bars-limit`, `progress-list` |
| **Decision** between two crossed settings | `outcome-grid` (for a plain either/or, use an options table) |
| **Explain an idea** (page opener) | `hero-diagram` |
| **Code change** | `code-panel` |
| **Key numbers** | the lede sentence, plus `progress-list` or `bars-limit` when the numbers have a limit or a comparison |

Rules for the visuals:

- **Only these visuals.** No Mermaid, no stat tiles, no charting library, no visual drawn
  from scratch when a slug above fits. If no slug fits a real need, use a plain table and
  say so in your reply.
- **Every node-and-link visual is interactive.** Graphs, pipelines, mappings, trees, data
  models, sequences and swimlanes keep the snippet's `data-focus` wiring: hovering or
  clicking an item keeps its chain (what it needs in blue, what needs it in red) and fades
  everything else; flow buttons fade what is outside a flow. Keep `data-node` /
  `data-edge` on every item and link you add. Wherever the text names a diagram item by
  its id or short name (`R5`, `Runner`), write it as `<span data-goto-node="R5">R5</span>`
  so clicking it opens the diagram's tab and pins that item. Leave longer phrases as plain
  text.
- **Dense points get hover values, not fewer points.** When labels would collide (a
  scatter of close options), label only the few that matter and put `data-tip` on every
  mark. Don't swap the listed visual for a different one to dodge the collision.
- **One idea per visual.** The visual's title is its point as a sentence ("Every reranker
  is 2 s faster and 6–14 points less accurate"), and its note says how to read it in one
  line.
- **Fill, don't restyle.** Replace the whole `DATA` object with values from your material
  and replace the `{{…}}` text. The sample data is made up and looks plausible, so no
  sample value may survive. Keep the snippet's markup, classes and script. A second copy of
  a snippet on one page gets a new id prefix everywhere (`dep-1` → `dep-2`, including ids
  inside the script).

## Build and publish

1. Make one `Artifact` call with `action: "quickstart"` and `intent: "other"`. The template
   already meets its page-design guidance, so `artifact-design` doesn't need loading.
2. Copy `page-template.html` to the scratchpad as `<topic>.html`. Keep its `<style>` and
   `<script>` blocks exactly as they are. Fill the header, one tab button and one panel
   per tab, and paste each chosen snippet (its `<figure>` and its `<script>`) into its
   section. Delete the template's HTML comments.
3. Check that no `{{` is left, every `id` is unique, every name in a `data-goto-node`
   exists as a `data-node`, and every `DATA` object holds only values from your material.
4. Publish with the `Artifact` tool: a 2–4 word `<title>` that names the subject, a
   one-sentence `description`, and an `icon`. To change it later, edit the same file and
   publish again (no `icon`).
5. In the terminal: the point in one or two lines, the tabs in one line, the link. The
   detail lives on the page.

## Red flags: stop and fix

| You're about to… | Instead |
|---|---|
| Write one scrolling page "so it reads in order" or "can be printed" | Tabs. Order the tabs instead. |
| Put headline numbers in tiles | Put them in the lede sentence; add bars if they have a limit. |
| Draw a static dependency or architecture diagram | Use `dependency-graph` or another focus-wired slug. |
| Swap a listed visual because labels collide | Keep it; label a few points, `data-tip` the rest. |
| Present a decision without saying which option you'd take | State the recommendation and the reason. |
| Use Mermaid for a flow | `pipeline` or `sequence-phased`. |
| Explain how something works without an example | Add the real request, query, row or scenario; label an invented one "Illustration". |
