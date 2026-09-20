# Mining Deck Template

A basic Anki deck template for use with Yomitan. Forked from https://github.com/friedrich-de/Basic-Mining-Deck.

## Yomitan Fields

| Anki Field    | Yomitan Template         |
|---------------|--------------------------|
| Word          | {expression}             |
| Reading       | {reading}                |
| Glossary      | {glossary-no-dictionary} |
| Sentence      | {clipboard-text}         |
| Picture       |                          |
| Audio         | {audio}                  |
| SentenceAudio |                          |
| Graph         | {pitch-accent-graphs}    |
| Hint          |                          |

## Last tested dictionary versions

- **Jitendex.org \[2024-08-11\]** rev.2024.08.11.0: https://github.com/stephenmk/stephenmk.github.io/releases/tag/v4.8-4
- **JMnedict \[2026-01-11\]** rev.JMnedict.2026-01-11: https://github.com/yomidevs/jmdict-yomitan/releases/tag/2026-01-11
- **KANJIDIC \[2026-011\]** rev.kanjidic2.2026-011: https://github.com/yomidevs/jmdict-yomitan/releases/tag/2026-01-11
- **大辞泉** rev.pitch_1.0.0.1

## Layout

```
src/
  templates/      Card templates and testing harness
  inputs/         Low-level fragments shared between templates
testcases/        Example Yomitan glossary dumps for testing
output/           Generated card/note sources for use in Anki
build.py          Script to build output/ files
```

## Building

```bash
python3 build.py
```

## How to update a card in Anki

1. Edit files under `src/`.
2. Run `python3 build.py`.
3. Open a card with the corresponding template in Anki, then `Edit` > `Cards...`.
4. Copy from `output/` into the Anki editor:

   | Note type      | Anki slot | File                        |
   |----------------|-----------|-----------------------------|
   | Written        | Front     | `output/front-written.html` |
   | Written        | Back      | `output/back.html`          |
   | Audio          | Front     | `output/front-audio.html`   |
   | Audio          | Back      | `output/back.html`          |
   | Reverse        | Front     | `output/front-reverse.html` |
   | Reverse        | Back      | `output/back-reverse.html`  |
   | *(all)*        | Styling   | `output/styling.css`        |

## Testing

`output/testing.html` is a browser test harness for the card templates.

### Adding test cases

If the dictionaries/Yomitan produce a glossary structure that breaks card formatting:

1. Copy the card's **Glossary** field out of Anki. It should start with
   `<div class="yomitan-glossary">`.
2. Save it as `testcases/NN-short-name.html`
3. Run `python3 build.py` and pick it from the "Test case" dropdown.

`testcases/sample-fields.json` holds stand-in values for the other Anki fields
(`Word`, `Reading`, `Graph`, `Audio`) so the test harness renders a complete card.

## Templating

`build.py` relies on simple placeholders:

| Placeholder | Meaning |
|---|---|
| `<!-- @include inputs/foo.html -->` | Insert file contents with relative indentation |
| `<!-- @testcases -->` | Insert one `<template>` per `testcases/*.html` file |
| `<!-- @note-types -->` | Insert one `<template>` per note type × front/back |
