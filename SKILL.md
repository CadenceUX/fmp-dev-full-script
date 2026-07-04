---
compatibility: Claude Code, Claude.ai (code execution enabled)
metadata:
  "Built and maintained": "Darrin Southern from CadenceUX"
  version: "1.0"
name: fmp-dev-full-script
description: |
  Generates a single paste-ready FileMaker script exercising every resolvable script step and
  calculation function against a target file — for regression-testing the claris-filemaker-pro
  and filemaker-xml skills' catalogs, or a working demo of the full step/function surface.
  Trigger on "build a script that tests every function", "exercise all script steps", "generate
  a reference/regression script", or similar full-surface requests. Mandatory first step: ask
  which optional schema objects (summary field, repeating field, relationship, value list,
  container field, AI Account) already exist in the target file before excluding anything that
  needs one — don't assume absence. Excludes the zero-argument function Self, confirmed to cause
  an "invalid script step" save failure when used in a script Set Variable (it's only valid in a
  Conditional Formatting or object calc). Code-execution-dependent (368 functions + 225 steps) —
  not reliably doable by hand in chat reasoning alone.
---

# FMP Dev Full Script — Comprehensive Reference Script Generator (v1.0)

Generates one paste-ready `fmxmlsnippet` script that exercises as many FileMaker Pro script
steps and calculation functions as can be resolved with a verified XML skeleton — built for
regression-testing the `claris-filemaker-pro` / `filemaker-xml` skills' own catalogs against a
real file, or for handing a developer a single working demonstration of the full step/function
surface.

This is not a general scripting skill — for day-to-day script authoring use `fmp-dev-gate`. This
skill is specifically for the "exercise everything" full-surface script task.

---

## Mandatory first step: ask about optional schema objects before excluding anything

**Do not exclude a function or step from the generated script just because it typically needs a
schema object that doesn't exist in a generic/blank file.** Ask the developer first whether the
*actual target file* already has one. This was gotten wrong once already: `GetSummary` was
excluded from a generated script on the assumption that no real Summary field existed to
reference — but the target table already had one (`ExampleSummary`, created earlier in the same
session). The exclusion was avoidable; the right move was to ask, not assume.

Before generating, ask the developer to confirm which of the following exist in the target file,
and use the real names if so:

| Object | Needed for | If absent |
|---|---|---|
| A Summary field | `GetSummary()` — needs a real summary field + sorted break field, no literal substitute exists | Exclude `GetSummary`, note why |
| A repeating field | `NPV()` (payment parameter — plain numbers are rejected at the field-type level), `Extend()`, `GetRepetition()`, `Last()`, a repeating-field Set Field demo | Exclude/flag as needing real infra |
| A relationship / table occurrence | `Go to Related Record`, `Fine-Tune Model`, Lookup auto-enter, `RelationInfo()` | Confirmed: `Go to Related Record` and `Fine-Tune Model` both need a real Table (self-reference to the target table is fine if no other relationship exists — see `references/known-issues.md`). Lookup fields need more specifically: a real related table occurrence *name* and a real field name on it — the field's own `<Table>` reference resolves regardless of relationships, only the inner `<Field table="RelatedTOName">` needs the relationship to exist |
| A value list | Value-list field validation, `ValueListItems()` | Pastes with `valuelist="True"` but the `<ValueList>` child silently drops on paste (documented FileMaker behaviour, not a bug) |
| A container field | Container functions (`GetContainerAttribute`, `GetThumbnail`, `CryptDecrypt`, etc.) | Reference a real container field name if one exists, otherwise these return empty/error at runtime — still syntactically fine |
| A configured AI Account | AI/embedding functions and steps to return real (not just syntactically valid) results | Fine to include regardless — they'll just no-op without a configured account |
| **A blank script literally named `script`** | `Perform Script`, `Perform Script on Server`, `Install OnTimer Script`, `Perform Script on Server with Callback` all need a real script to reference | Offer to paste one — see the ready-made XML in `references/known-issues.md`'s "blank `script` companion" design decision. Never self-reference the reference script itself as the target — that risks infinite recursion if the pasted script is ever actually run |
| **A layout matching the target table's name** | `Go to Layout` | Confirmed to matter in practice — tables don't automatically get a same-named layout. If absent, use a real layout name the developer provides instead of assuming the table name works |

Ask this as a single up-front question, e.g.:

> Before I generate this, does the target file already have: a Summary field, a repeating field,
> a relationship/table occurrence, a value list, a container field, a configured AI Account, a
> blank script literally named `script`, and a layout matching the target table's name? If any of
> these exist, tell me the real names so I can wire the relevant functions/steps to them for real
> instead of excluding or hand-waving them.

Only exclude a function/step after confirming the target genuinely lacks what it needs — and say
so explicitly in the report, rather than defaulting to exclusion from general knowledge of what
*most* files lack.

**For the fields specifically, don't just ask yes/no — confirm the table name, then offer the
full paste.** Once the developer confirms which target table to use, offer the complete
ready-to-paste field set (all data types, both `fieldType`s beyond Normal, and every validation/
storage variant — see the "example table" field XML built during this skill's originating
session) parameterized to that table name, so any missing prerequisite field can be created on
the spot rather than requiring a separate manual setup step.

---

## Resolved issues: eight separate "invalid script step" causes found and fixed

**The generated script previously did not save in Script Workspace**, with an "invalid script
step" error after a clean paste. Eight distinct causes were found and fixed on 2026-07-03 — full
account of all eight in `references/known-issues.md`. Clearing one did not mean the script was
clean; each subsequent cause was found only after the previous fix was deployed and re-tested
(and in the last two cases, after the developer confirmed the fixes cleared and independently
identified further issues themselves). Treat this pattern as the norm for a full-surface script,
not the exception — **budget for multiple rounds of "invalid script step" whenever a script this
size is generated against a real file for the first time.**

1. A `Set Variable` step calling the zero-argument function `Self`.
2. `Commit Transaction`/`Revert Transaction` nested inside an `If`/`Else` block — confirmed
   invalid regardless of context, found only after an initial "looks correct on paper" fix
   (branching to Commit or Revert, matching a documented general FileMaker idiom) was deployed,
   tested, and found to still fail.
3. `Add Account` (id 134) — bare unconfigured skeleton missing `AccountName`/`Password`/
   `PrivilegeSet`. Fixed using FileMaker's own real exported XML for a manually-configured step
   (Privilege Set: the built-in `[Data Entry Only]`).
4. `Open File` (id 33) — bare unconfigured skeleton missing `<FileReference>` entirely. Fixed by
   pointing at the target file itself (`Blank.fmp12`) — always resolvable, no external dependency.
5. `Perform Script on Server with Callback` (id 210) — two separate missing script references
   (the main script to perform, and the callback script) — the documented skeleton's
   `<CallbackScript/>` was an empty tag with nothing inside it.
6. `Save a Copy as XML` (id 3) — no destination file path in either documented form (pre-FM26
   minimal or FM26-expanded). Fixed by adding a direct `<UniversalPathList>` child.
7. `Fine-Tune Model` (id 213) — bare "no table set" skeleton. Fixed by self-referencing the
   target table occurrence.
8. `Go to Related Record` (id 74) — **this one was a generator error, not a documentation gap**:
   `filemaker-xml` already documents a working "Basic form" for this step; the generator used the
   wrong (unconfigured) variant instead. Fixed by switching to the documented form — four
   attribute values differ together (`Restore`, `LayoutDestination`, `NewWndStyles`'s `Styles`,
   plus the `Table`/`Layout` elements), not just adding references on top of the unconfigured set.

Fixes 3–6 were obtained by asking the developer to manually configure the real step and copy it
out. For 7–8, the developer proactively diagnosed and either supplied the real captured state (7)
or named the exact fix needed (8) without being asked — the same technique generalizing further
each round. `Go to Layout` was suspected as a likely ninth cause but confirmed fine in this
specific target file (a layout matching the table name happened to already exist) — noted as
target-file-specific, not a general guarantee.

**Also resolved, not a script step**: the `LookupField` field's `Lookup` auto-enter, left
deliberately unresolved at field-creation time (no relationship existed yet), now resolves
correctly after the developer created a real relationship. See `references/known-issues.md` for
the structural confirmation of which part of a Lookup reference actually depends on the
relationship existing (only the inner `<Field table="RelatedTOName">`, not the outer `<Table>`).

The combined two-script bundle with all eight script-step fixes applied has been delivered and
the delivery mechanism confirmed pasting correctly; the developer's workflow of testing individual
fixes in isolation before folding them into the full bundle means each fix is independently
verified, but a single full end-to-end save of the very latest combined bundle (all eight fixes
present at once) has not been separately re-confirmed as one pass.

**Root cause**: a `Set Variable` step calling the zero-argument function `Self`
(`Set Variable [ $var ; Value: Self ]`). `Self` is only valid inside a Conditional Formatting
calculation or an object's own calc — meaningless in a script context. FileMaker's paste handler
accepted the step structurally, then silently dropped the entire `<Value>` element on save,
leaving a `Set Variable` with a name and no calculation — which save-time validation then
rejected.

**Fix**: `Self` added to `scripts/build_function_calls.py`'s `FORCE_EXCLUDE` table. Any future
full-surface script must exclude it; there is no valid script-level substitute.

**How the `Self` bug was found — prefer this over bisection when possible:** the developer
copied the pasted script's current steps back out of Script Workspace (Cmd+C), and diffing that
native re-exported XML against the originally-generated XML immediately showed which single
step's content FileMaker itself considered different — a direct, one-pass comparison, no repeated
save attempts needed.

**But the diff technique doesn't catch everything** — the transaction bug (#2) produced *no*
content diff at all (the XML round-tripped byte-for-byte identical structurally); the defect was
behavioral/semantic, not a dropped element. That one needed actual bisection: isolated, minimal
test snippets (flat pair / nested-in-If / flat-with-both-closers), each tested by pasting into a
fresh empty script one at a time, narrowed to the real rule in 3 rounds after both the diff
technique and the developer's own direct diagnosis proved insufficient alone. Use the diff
technique first since it's cheaper when it applies, but don't assume it will always find the
defect — fall back to isolated bisection when a save still fails despite a clean diff.

**A third technique for the `Add Account` bug — ask for real native XML before guessing at all,
not after a failed guess.** `filemaker-xml` only had a bare, unconfigured `Add Account` skeleton
to offer, with no configured variant to adapt. Rather than fabricate `AccountName`/`Password`/
`PrivilegeSet` XML from speculation — risky for anything account/security-related — the developer
was asked upfront to manually configure a real `Add Account` step in Script Workspace and copy it
out. Full structure and the "why this technique here" reasoning in `references/known-issues.md`.
Prefer this proactive approach whenever a step's configured form isn't documented anywhere,
rather than deploying a guess and waiting to see if it fails.

**The same technique found three more fixes (`Open File`, `Perform Script on Server with
Callback`, `Save a Copy as XML`) in one batch** — once the pattern was established, the developer
proactively captured and supplied real configured XML for all three without needing to be asked
for each individually, plus flagged and disproved a fourth suspect (`Go to Layout`) the same way.
This confirms the technique generalizes: whenever a step's configured form isn't documented,
asking for one real captured example resolves it faster and more reliably than iterating on
guesses.

**Still worth treating with caution for future attempts:** paste succeeding is not the same
guarantee as save succeeding — verify an actual save in Script Workspace before calling a
generation attempt done, not just clean XML validation or a paste with no paste-handler error.
And it's not established that `Self` is the *only* function with this property, or that the
transaction-nesting rule is the *only* structural constraint of its kind (see
`references/known-issues.md`'s "Residual open question") — re-diff and re-bisect if a future
full-surface script fails to save again, even against the same target file.

**`GetSummary`/`NPV` re-added (2026-07-03), not yet re-confirmed to save:** both required objects
were confirmed to already exist in the target table (`example`, in `blank.fmp12`) —
`ExampleSummary` (a real Summary field) and `ExampleRepeating` (a real repeating field) — so both
functions were moved from `FORCE_EXCLUDE` into `SPECIAL` with real field references:
`GetSummary ( example::ExampleSummary ; example::ExampleNumber )` and
`NPV ( example::ExampleRepeating ; .05 )`. This produces a 367/368-function, 618-step script
(only `Self` still excluded). **This specific version has not yet been paste-and-save tested** —
the 616-step version without these two was the one confirmed saving; treat 367/368 coverage as
generated-but-unverified until an actual save is confirmed, per this skill's own completion
criterion. `GetSummary`'s value will only be meaningful if the found set is sorted by
`example::ExampleNumber` (or another break field) before the calculation runs — the field
existing is necessary but not sufficient for a meaningful result, only for valid syntax.

**A second, process-level bug found while doing this:** the fix for `Self` (and this
`GetSummary`/`NPV` re-inclusion) had been applied to `scripts/build_function_calls.py` — the
bundled, shipped copy — but a separate, ad-hoc working-copy generator used during the same session
(never bundled, not part of this skill) had drifted out of sync and still excluded/included the
wrong set. A regex-based bulk edit across "both" generator scripts also silently failed on one of
them because its `FORCE_EXCLUDE` entries spanned two physical lines with implicit string
concatenation, which the regex's single-line assumption didn't match — no error was raised, the
edit just silently did nothing. **Lesson: after any bulk find/replace across multiple files with
diverging formatting, verify counts (`Included: N Excluded: M`) rather than trusting that "no
error" means "the edit applied."** Only one generator script should exist going forward — this
skill's bundled `scripts/build_function_calls.py` — to prevent this class of drift entirely.

---

## Generation methodology (what worked, from the session that built this)

### Step 1 — source the catalogs, never from memory

- **Script steps**: `claris-filemaker-pro`'s `references/script-steps-catalog.json` for the step
  roster (name, category, purpose) — but see *Known catalog gap* below, this file has historically
  undercounted the real step list.
- **Calculation functions**: `claris-filemaker-pro`'s `references/function-catalog.json` for all
  368 functions (`name`, `format`, `parameters`, `category`).
- **Script step XML skeletons**: `filemaker-xml`'s `references/core.md` (always read first — paste
  format rules, the placeholder-ID pattern, the three silent-failure traps) then the category
  file for each step's actual skeleton (`steps-control.md`, `steps-fields-records.md`,
  `steps-navigation-editing.md`, `steps-windows-files.md`, `steps-accounts-ai-misc.md`,
  `steps-pdf.md`, `steps-plugin.md`). Do not guess a step's numeric `id` — every one used here was
  read directly from a skeleton or a "no-option steps" table in those files.

### Step 2 — the placeholder-ID pattern (core.md §5)

For schema references (`<Field>`, `<Table>`, `<Layout>`, `<Script>`) where the target file's real
internal IDs aren't known, use `id="1"` (or any non-zero placeholder) with the real `name`
attribute. FileMaker resolves these by name on paste and populates the real ID on save — this is
the primary generation strategy, not a degraded fallback.

### Step 3 — building function calls mechanically, not by hand

At 368 functions, hand-authoring every call invites exactly the kind of type-mismatch bug this
approach hit once already (see *Lesson learned* below). Instead:
1. Tokenize each function's parameter names (split camelCase/snake_case into words).
2. Classify each token against word lists: numeric, text, date/time/timestamp, JSON, field
   reference — build the literal argument from the classification, not a blind default.
3. Hand-special-case functions with documented pitfalls rather than trusting the classifier:
   `Let` (needs `var = expression` assignment syntax, not positional args), `While` (needs a real
   init/condition/logic/result shape), `Evaluate` (first argument must itself be a valid calc
   string like `"1+1"`, not arbitrary text), `Case`/`Choose`/`ExecuteSQL` (need real conditional/
   query shapes), all `Get()` functions (the catalog's `parameters` entry is the literal constant
   name already embedded in `format` — not a runtime argument to substitute into), Aggregate
   functions (`Average`/`Sum`/`Count`/etc. want numeric literals, not text).
4. `GetSummary` and `NPV` are the only two functions found so far that cannot be faked with a
   literal at all in the *general* case — but see the mandatory prerequisite-check step above
   before excluding them for a *specific* target file.

**Lesson learned the hard way**: an early version of the parameter classifier used raw substring
matching for short hint tokens (`'x'`, `'n'`, `'y'`, `'z'`) — which matched as substrings of
unrelated words (`"text"` contains `'x'`, `"fileNameWithExtension"` contains `'n'`), silently
producing wrong-typed arguments across dozens of functions. Fixed by tokenizing on word
boundaries (camelCase/snake_case splits) and matching whole words only, never substrings, for any
hint word under ~4 characters.

### Step 4 — known catalog gap (already reported and fixed upstream)

`claris-filemaker-pro`'s script-steps-catalog undercounted the real FileMaker step list by 60
steps as of this skill's creation — cross-checking its roster against `filemaker-xml`'s
independently-verified step IDs surfaced steps entirely missing from the catalog (not
duplicates), concentrated in `Open Menu Item` (half missing), an entire absent "Data File I/O"
sub-family, and most of `Spelling`. This was fixed in `claris-filemaker-pro` v1.9.2 (see that
skill's CHANGELOG) — if working from an older copy of that catalog, re-fetch it first.

### Step 5 — genuinely unresolvable steps (as of this skill's creation)

9 script steps have no verified XML step ID anywhere in `filemaker-xml`'s reference material —
not in a skeleton, not in a "no-option steps" table, not in the routing index:
`Check Spelling`, `Log Out`, `Manage Add-ons`, `Navigate to Object`, `Open Preferences`,
`Set Window Animation`, `Show Alert`, `Show/Hide Script Editor`, `Show/Hide Status Toolbar`.
These are the same 9 steps `claris-filemaker-pro`'s own CHANGELOG independently flagged as having
no verified `originated_in_version` — treat that as corroboration, not coincidence. Exclude these
from any generated script and say so; do not guess an ID for them.

### Step 6 — assembly and validation

1. Wrap everything in `<?xml version="1.0" encoding="UTF-8"?><fmxmlsnippet type="FMObjectList">`.
2. Pair flow-control steps that must nest (`If`/`Else If`/`Else`/`End If`,
   `Loop`/`Exit Loop If`/`End Loop`) properly rather than dumping them flat — an unbalanced
   structure is a likely candidate for a save failure.
3. **`Commit Transaction` and `Revert Transaction` must be flat, unconditional, top-level steps —
   never nested inside `If`/`Else`.** Confirmed by direct, isolated testing (see
   `references/known-issues.md` for the full bisection): nesting either one inside a conditional
   is rejected as an invalid script step regardless of whether `Open Transaction` is present.
   **This contradicts the general FileMaker scripting idiom `fmp-dev-gate` documents** under
   "Transactions" (branch to Commit-or-Revert based on a condition) — that pattern is good
   real-world scripting advice but does **not** survive round-trip through this XML paste format.
   A "looks correct, matches a documented idiom" fix was deployed once and still failed when
   actually tested — don't skip testing a fix just because it matches known-good general advice.
   The tested, working pattern for a syntax-reference script is flat and sequential:
   ```
   Open Transaction
   # ... transaction body ...
   Commit Transaction
   Revert Transaction
   ```
   This is semantically redundant at runtime (nothing to revert once committed) — it's a syntax
   reference, not a demonstration of correct transaction logic. Note that explicitly if a
   developer asks why it looks odd, rather than presenting it as idiomatic.
4. Parse the assembled XML back with a real XML parser (e.g. `xml.etree.ElementTree`) to confirm
   well-formedness before treating it as done — but remember well-formed ≠ paste-clean ≠
   save-clean (see *Resolved issue* above). All three gates are different, and clearing one
   save-blocking defect doesn't mean the script is fully clean — two separate "invalid script
   step" causes were found in the same script or this project; re-attempt the save after every fix.
5. Check for non-ASCII characters if the XML will pass through any pipeline stage (shell
   piping, clipboard, LLM context) — ASCII comparison operators (`<>`, `<=`, `>=`) survive
   transport more reliably than FileMaker's native Unicode glyphs (`≠`, `≤`, `≥`), which are
   multi-byte and can be silently corrupted by locale-sensitive tools.
6. **Deliver as one combined bundle with two sibling `<Script>` elements, not bare `<Step>`s
   pasted into an already-open script.** Wrap the blank `script` companion (see the mandatory
   prerequisite table above) and the main reference script in their own
   `<Script enable="True" name="...">` elements, as siblings inside one `fmxmlsnippet`, and paste
   directly into the Scripts list to create both at once:
   ```xml
   <fmxmlsnippet type="FMObjectList">
     <Script enable="True" name="script">...3 steps, the blank companion...</Script>
     <Script enable="True" name="Reference Script">...all steps and function calls...</Script>
   </fmxmlsnippet>
   ```
   **Every `Perform Script`-type step (`Perform Script`, `Perform Script on Server`,
   `Install OnTimer Script`, `Perform Script on Server with Callback`) must reference `script` by
   name** — never the reference script's own name. Self-reference would cause infinite recursion
   if the pasted script is ever actually run; see the design-decision entry in
   `references/known-issues.md` for the full reasoning.
7. **When re-delivering an updated bundle, warn about duplicates every time, not just once.**
   FileMaker scripts are identified by ID, not name — pasting this combined bundle again after
   both scripts already exist creates duplicates rather than merging or overwriting. Tell the
   developer to delete both existing scripts before pasting an updated bundle, every single time
   a fix produces a new version — this was needed twice in the same session and is easy to forget
   to repeat once it's been said once.

---

## Execution context

Building this at full scale (368 functions, 225 steps) is a code-execution task — tokenizing
parameter names, classifying against word lists, mechanically assembling and validating several
hundred XML elements is not realistically hand-authorable in chat reasoning alone, and doing it
by hand is exactly how the substring-matching bug above got introduced.

- **Claude Code / SDK**: run the bundled `scripts/` generators directly via Bash, inspect and
  validate output, iterate.
- **Claude.ai with code execution enabled**: the same Python scripts run in that sandbox — note
  the ephemeral filesystem means the source catalogs (from `claris-filemaker-pro`/`filemaker-xml`)
  need to be available in that session, not assumed present on disk.
- **Claude.ai chat with no code execution**: this workflow is not reliably achievable — say so
  rather than attempting a hand-authored version of the whole surface, which is how the known
  classifier bug happened in the first place.

---

## Bundled scripts

`scripts/build_function_calls.py` — mechanical generator for calculation-function Set Variable
calls from `claris-filemaker-pro`'s `function-catalog.json`. Reads the catalog, tokenizes
parameters, classifies, and emits one `Set Variable` XML block per function. Contains the
hand-special-cased exceptions (`Let`, `While`, `Evaluate`, etc.) as an editable table at the top —
extend it there, not by patching the classifier, when a new function needs special handling.

Run it yourself (Claude Code/Bash, or a code-execution-enabled chat session) — this skill does
not execute it automatically:
```
python3 scripts/build_function_calls.py path/to/function-catalog.json > function_calls.json
```

See `references/known-issues.md` for the full, current list of exclusions and open questions to
carry forward into the next attempt at this task.

---

## Version History

See [`CHANGELOG.md`](./CHANGELOG.md) for the full version history.

---

## Licence

This skill is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).
