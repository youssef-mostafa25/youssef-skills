# sha3bolly

Explanations you can follow. Claude answers as if explaining to a junior engineer:
plain words, always a real example, and a flowchart when steps chain together.

Created by [Habiba Abueldahab](https://github.com/abueldahabh). The original is at
[abueldahabh/sha3bolly](https://github.com/abueldahabh/sha3bolly), MIT licensed (see
[`LICENSE`](LICENSE)). It ships here because
[plan-build-board](../plan-build-board/README.md) and
[integration-assistant](../integration-assistant/README.md) explain things this way.

## How to use it

Ask for an explanation ("how does this request work?"), ask for a plan, or just say
"I don't understand", "I'm lost" or "explain again".

## What you get

- The point first, in plain words and short sentences.
- A concrete example every time: real code, a real request, or a real scenario.
- A flowchart for anything with chained steps:
  ```
  browser --(POST /login)--> API --(checks password)--> database
  ```
- Short numbered steps instead of walls of text. Ask for more detail whenever you want
  it.

When you say you don't understand, you won't just get the same answer reworded. You get
four labelled parts: **Context** (where this fits), **Backstory** (why it works this
way), **Example**, and **Flowchart**.
