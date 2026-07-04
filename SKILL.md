---
compatibility: Claude Code, Claude.ai (code execution enabled)
metadata:
  "Built and maintained": "Darrin Southern from CadenceUX"
  version: "1.1"
name: fmp-dev-full-script
description: |
  Generates a single paste-ready FileMaker script exercising every resolvable script step and
  calculation function against a target file — for regression-testing FileMaker reference
  catalogs, or a working demo of the full step/function surface. Trigger on "build a script that
  tests every function", "exercise all script steps", "generate a reference/regression script",
  or similar full-surface requests. Guides the developer through setup first: MBS Plugin
  recommended for delivery (or the developer defines their own method), a blank companion script
  exists, and the target table has the schema objects a full-coverage script needs (Summary
  field, repeating field, relationship, value list, container field, layout). Delivers via a
  single combined paste, then walks the developer through a save-and-copy-back verification step
  to confirm the script actually landed correctly in FileMaker. Code-execution-dependent (368
  functions + 215 steps) — not reliably doable by hand in chat reasoning alone.
---

# FMP Dev Full Script — Comprehensive Reference Script Generator (v1.1)

Generates one paste-ready `fmxmlsnippet` script that exercises every resolvable FileMaker Pro
script step and calculation function — built for regression-testing FileMaker script/function
reference catalogs, or for handing a developer a single working demonstration of the full
step/function surface.

This is not a general scripting skill — for day-to-day script authoring, use a general FileMaker
scripting skill. This skill is specifically for the "exercise everything" full-surface script task.

---

## Setup — walk the developer through this before generating anything

Building a script this size only works if a handful of things already exist in the target file.
Go through each of these with the developer, one at a time, offering ready-to-paste XML wherever
one is needed rather than just asking yes/no and leaving them to build it themselves.

### 1. MBS Plugin is the recommended way to receive the paste into Script Workspace

The recommended delivery method (see *Delivery*, below) writes the generated XML directly to the
system clipboard from outside FileMaker. FileMaker's Script Workspace only recognises pasted
content as real steps — rather than literal text — when MBS Plugin is installed in that FileMaker
instance. No MBS scripting call is needed, and no field or variable stores the XML — the plugin
merely needs to be present for the paste to be interpreted correctly.

Ask: *"Is MBS Plugin installed in the FileMaker Pro application you'll be pasting into?"*

- **If yes**, use the delivery method described below.
- **If no**, the developer needs to define their own method for getting the generated XML into
  Script Workspace as real steps — this skill does not require MBS and does not manage that
  process itself. See `fmp-dev-gate`'s "Delivering Code to FileMaker" section for the range of
  alternative delivery methods and their tradeoffs. Once the developer has a working delivery method, everything else
  in this skill (setup, generation, verification) applies the same way regardless of which
  method delivers the XML.

### 2. A blank companion script named `script` must exist in the target file

Several steps in the full-surface script (`Perform Script`, `Perform Script on Server`,
`Install OnTimer Script`, `Perform Script on Server with Callback`) need a real script to
reference. Never point these at the reference script itself — if the pasted script is ever
actually run, a self-referencing `Perform Script` call would call the whole script again,
recursing forever. A separate, blank, always-safe companion avoids this entirely.

Offer this ready-to-paste XML, to be pasted directly into the file's Scripts list:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<fmxmlsnippet type="FMObjectList">
  <Script enable="True" name="script">
    <Step enable="True" id="85" name="Allow User Abort">
      <Set state="False"/>
    </Step>
    <Step enable="True" id="86" name="Set Error Capture">
      <Set state="True"/>
    </Step>
    <Step enable="True" id="103" name="Exit Script">
      <Calculation><![CDATA[""]]></Calculation>
    </Step>
  </Script>
</fmxmlsnippet>
```
Confirm it lands as a real script (not just steps) before moving on.

### 3. Confirm the target table, then offer the full field set

Ask which table the demonstration fields should live in. Once confirmed, offer the complete
ready-to-paste field set for that table name — covering every data type (Text, Number, Date,
Time, Timestamp, Container), both non-Normal `fieldType`s (Calculation, Summary), and enough
validation/storage variants (Global, Repeating, Serial, Value List, Range, external Container
storage, stored+indexed Calculation) that the full-surface script has real objects to reference
rather than placeholders. Don't just ask "do you have a Summary field?" one at a time — confirm
the table name once, then hand over the whole set.

### 4. Confirm these specific objects exist, or offer to help create them

| Object | Needed for | If absent |
|---|---|---|
| A Summary field | `GetSummary()` | Exclude `GetSummary` from the generated script |
| A repeating field | `NPV()`, `Extend()`, `GetRepetition()`, `Last()` | Exclude `NPV`, or use a plain (non-repeating) demo for the others |
| A relationship + a real field on the related table occurrence | Lookup auto-enter demo, `RelationInfo()` | Field pastes but the Lookup stays unresolved until a relationship exists |
| A value list | Value-list field validation, `ValueListItems()` | Field pastes with the validation attribute set but no attached list |
| A container field | Container functions | Reference a real container field if one exists; otherwise these return empty at runtime, which is fine for a syntax demo |
| A configured AI Account | AI/embedding functions and steps | Fine to include regardless — they'll just return nothing without a configured account |
| A layout matching the target table's name | `Go to Layout` | Use a real layout name the developer provides instead |

Only exclude something after confirming the target genuinely lacks what it needs — many of these
may already exist, and assuming otherwise produces an unnecessarily incomplete script.

---

## Generating the script

### Source the catalogs — never generate step or function syntax from memory

Use a dedicated FileMaker function/script-step reference skill for the full roster of script
steps (name, category, purpose) and all 368 calculation functions (`name`, `format`,
`parameters`, `category`). Use a dedicated FileMaker script-XML skill for the paste-ready XML
skeleton of each step — every step ID and element structure should come from a verified reference,
not be guessed.

### The placeholder-ID pattern

For schema references (`<Field>`, `<Table>`, `<Layout>`, `<Script>`) where the target file's real
internal IDs aren't known, use `id="1"` (or any non-zero placeholder) with the real `name`
attribute. FileMaker resolves these by name on paste and populates the real ID on save.

### Building function calls mechanically

At 368 functions, build each one programmatically rather than by hand:
1. Tokenize each function's parameter names (split camelCase/snake_case into words).
2. Classify each token against word lists — numeric, text, date/time/timestamp, JSON, field
   reference — and build the literal argument from the classification.
3. Hand-special-case functions with non-obvious syntax: `Let` (needs `var = expression`
   assignment, not positional args), `While` (needs a real init/condition/logic/result shape),
   `Evaluate` (first argument must itself be a valid calc string like `"1+1"`), `Case`/`Choose`/
   `ExecuteSQL` (need real conditional/query shapes), all `Get()` functions (the parameter name is
   the constant already embedded in the function's own syntax, not a substitutable argument),
   Aggregate functions (want numeric literals, not text).
4. When tokenizing, match whole words only — never substring-match a short hint word (`x`, `n`,
   `y`, `z`) against arbitrary parameter names, since that misclassifies unrelated words that
   happen to contain that letter (`"text"` contains `x`; `"fileNameWithExtension"` contains `n`).

See `scripts/build_function_calls.py` for the reference implementation.

### Functions excluded from the general-case script

`Self`, `GetSummary`, and `NPV` cannot be faked with a literal in the general case (see
`references/limitations.md` for why). Confirm with the developer whether the target file has what
each needs (per the *Setup* checklist above) before excluding any of them for a specific target.

### Steps that need a configured form, not the bare/minimal one

A handful of steps have a bare/unconfigured form that is not valid to actually generate and
paste — the developer's target file will reject it on save. Use the configured forms in
`references/step-configurations.md` for: `Add Account`, `Open File`,
`Perform Script on Server with Callback`, `Save a Copy as XML`, `Fine-Tune Model`, and
`Go to Related Record`.

### Transaction steps must be flat and unconditional

`Commit Transaction` and `Revert Transaction` must be flat, top-level steps in the generated
script — never nested inside an `If`/`Else` block, even when only one of the two is nested. Any
`Open Transaction` needs a `Commit Transaction` and/or `Revert Transaction` following it as a
plain sequential step, not wrapped in a condition:
```
Open Transaction
# ... transaction body ...
Commit Transaction
Revert Transaction
```
This demonstrates both steps' syntax; it isn't a template for real conditional commit/revert
logic, since branching between the two doesn't work reliably when pasted this way.

### Steps that cannot be generated at all

A small number of script steps have no verified paste-ready structure available and should be
excluded from the generated script rather than guessed at — see `references/limitations.md` for
the current list.

---

## Delivery

**Recommended method, when MBS Plugin is available:** wrap the blank `script` companion and the
main reference script in their own `<Script enable="True" name="...">` elements, as siblings
inside one `fmxmlsnippet`, and paste directly into the target file's Scripts list to create both
scripts at once:
```xml
<fmxmlsnippet type="FMObjectList">
  <Script enable="True" name="script">...the blank companion...</Script>
  <Script enable="True" name="Reference Script">...all steps and function calls...</Script>
</fmxmlsnippet>
```

**If MBS Plugin isn't available**, this skill's job is still just to produce that same XML
content — the developer defines their own way of getting it into Script Workspace as real steps
(see `fmp-dev-gate`'s "Delivering Code to FileMaker" section for the range of delivery methods
and how to choose between them).
This skill doesn't require MBS and isn't responsible for running whichever delivery method the
developer settles on; everything else in this workflow (setup, generation, verification) applies
the same regardless of how the XML actually gets pasted.

**If delivering an updated version after a fix**, tell the developer to delete both existing
scripts first. FileMaker scripts are identified by internal ID, not name — pasting the same
bundle again after both scripts already exist creates duplicates rather than replacing them.

---

## Verification — confirm the script actually landed correctly

Don't consider the script "delivered" once it pastes without an error. Paste succeeding is not
the same as the script being structurally correct inside FileMaker — walk the developer through
this confirmation step every time:

1. **Ask the developer to save the script** in Script Workspace after pasting.
2. **Ask them to copy the script's steps back out** of Script Workspace (select all, Cmd+C).
3. **Ask them to paste that copied content back to you.**
4. **Compare it against the XML you originally generated.** FileMaker's own re-export reflects
   exactly what it stored — any step whose content differs from what was generated (a reference
   that didn't resolve, a value that got dropped, an element FileMaker normalised differently)
   will show up in this comparison. This is a more reliable check than watching for a save error,
   since some defects don't produce an error message at all.
5. If anything differs unexpectedly, fix the specific step and repeat the round trip — don't
   assume a clean paste and a successful save mean everything is correct.

---

## Execution context

Building this at full scale (368 functions, 215 steps) is a code-execution task — tokenizing
parameter names, classifying against word lists, and mechanically assembling and validating
several hundred XML elements isn't realistically hand-authorable in chat reasoning alone.

- **Claude Code / SDK**: run the bundled `scripts/` generator directly via Bash, inspect and
  validate output, iterate.
- **Claude.ai with code execution enabled**: the same Python script runs in that sandbox — the
  source function catalog needs to be available in that session, not assumed present on disk.
- **Claude.ai chat with no code execution**: this workflow is not reliably achievable by hand.

---

## Required reference skills

This skill doesn't duplicate FileMaker's function/script-step catalogs or paste-XML format
rules — it depends on:
- A FileMaker function and script-step reference skill, for the full function/step roster.
- A FileMaker script-XML skill, for verified paste-ready XML skeletons and paste-format rules
  (the placeholder-ID pattern, element ordering, CDATA wrapping, and similar structural rules).

Read those skills' own documentation before generating anything — this skill assumes their
content is available, not bundled here.

---

## Bundled reference

- **`references/step-configurations.md`** — verified configured XML for the six steps whose
  default form isn't save-valid.
- **`references/limitations.md`** — functions and steps excluded from the general-case script,
  and why.
- **`scripts/build_function_calls.py`** — the function-call generator. Run yourself
  (Claude Code/Bash, or a code-execution-enabled chat session) — this skill does not execute it
  automatically:
  ```
  python3 scripts/build_function_calls.py path/to/function-catalog.json > function_calls.json
  ```

---

## Version History

See [`CHANGELOG.md`](./CHANGELOG.md) for the full version history.

---

## Licence

This skill is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
