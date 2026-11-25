# tabbed-explainer

Pages you can read at a glance. Ask Claude for an artifact, a page or a write-up, and you
get a tabbed HTML page that explains the subject in plain words (the
[sha3bolly](../sha3bolly/README.md) style), with a visual wherever a picture says it
faster.

## How to use it

Ask for a page: "make an artifact explaining how context search works", "put these
findings in a page for the team", "visualise this plan". You can also call it by name,
`/youssef-skills:tabbed-explainer`.

## What you get

```
header ─ the point, with the key numbers in the sentence
tabs ─── one per thing you'd come to look for, linkable by #hash
panels ─ point box ─► example ─► visual ─► detail
```

- **Tabs, not one long page.** Claude picks them from the content.
- **Visuals from a hand-picked kit.** 20 visuals, one per job, each listed for the
  situations it suits: what ships first, how the system is built, steps, before → after,
  who calls whom, comparing options, change over time, parts of a whole, timelines,
  hierarchy, status against a limit, decisions and code changes. No Mermaid and no stat
  tiles.
- **Diagrams you can explore.** Hover or click any item in a graph, pipeline, tree,
  sequence or data model: what it needs turns blue, what needs it turns red, and everything
  else fades. Flow buttons fade everything outside one flow, and any item named in the
  text links back to the diagram.
- **A recommendation when there's a choice**, with the options side by side.
- Light and dark themes, and it works on a phone.

## What's inside

| File | What it is |
|---|---|
| `SKILL.md` | The rules: page parts, which visual for which situation, build steps |
| `page-template.html` | The page shell: theme tokens, tabs, tooltips and the focus behaviour |
| `visuals/*.html` | One snippet per visual, with sample data to replace |
