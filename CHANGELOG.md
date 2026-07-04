# fmp-dev-full-script — Changelog

## v1.0 — 2026-07-03 (updated same day)

### Resolved — seventh and eighth "invalid script step" causes, plus a resolved field-level issue
- **`Fine-Tune Model`** (id 213) — bare "no table set" skeleton, fixed by self-referencing the
  target table occurrence (`<Table id="1" name="example"/>`).
- **`Go to Related Record`** (id 74) — **not a documentation gap, a generator error**:
  `filemaker-xml` already documents a working "Basic form" for this step; the generator had used
  the wrong (unconfigured) variant. Fixed by switching to the documented form — four attribute
  values change together (`Restore` → `True`, `LayoutDestination` → `SelectedLayout`,
  `NewWndStyles`'s `Styles` → `983554`), not just adding `Table`/`Layout` on top of the
  unconfigured attribute set. New lesson captured: when a step has multiple documented variants,
  don't default to the simplest-looking one without checking it's actually save-valid.
- **`LookupField` (a field, not a script step) now resolves correctly** after the developer
  created a real relationship (`example` → `example 2`). Confirmed structurally: a Lookup
  reference's outer `<Table>` describes the field's own table and resolves regardless of whether
  a relationship exists; only the inner `<Field table="RelatedTOName">` actually depends on the
  relationship. The "A relationship / table occurrence" prerequisite-check row sharpened to ask
  for the specific related TO name and a real field on it, not just "does a relationship exist."
- Total confirmed "invalid script step" causes for this script: **eight**. `Go to Layout` checked
  and cleared as a false-alarm ninth suspect (target-file-specific, not general).
- No version bump.

### Resolved — three more "invalid script step" causes (fourth, fifth, sixth), plus two
### workflow design decisions, closing out this generation's debugging cycle
- **`Open File`** (id 33) — bare skeleton had no `<FileReference>` at all. Fixed by pointing at
  the target file itself (`Blank.fmp12`), obtained from the developer's own captured XML.
- **`Perform Script on Server with Callback`** (id 210) — two separate missing script references;
  the documented `<CallbackScript/>` was an empty tag with nothing inside. Fixed using captured
  XML: main script via `<Script id name>`, callback via `<ScriptName id name>` inside
  `<CallbackScript>` — different element names for what looks like the same kind of reference.
- **`Save a Copy as XML`** (id 3) — no destination path in either documented form. Fixed by
  adding a direct `<UniversalPathList>` child (not wrapped in `<FileReference>` — different
  pattern from `Open File`'s destination, confirmed by testing rather than assumed symmetrical).
- **`Go to Layout` checked and confirmed fine** — suspected as a likely seventh cause (table name
  used as layout name, no general guarantee a same-named layout exists) but the developer
  confirmed one already existed in this target file. Documented as target-file-specific, not a
  general fix.
- **Design decision: dedicated blank `script` companion, not self-reference.** All
  `Perform Script`-type steps now reference a separate, blank, always-safe companion script
  (`Allow User Abort` → `Set Error Capture` → `Exit Script [""]`) rather than the reference
  script's own name — self-reference would cause infinite recursion if the pasted script is ever
  actually run. This is now a standing prerequisite, added to the mandatory schema-object
  checklist alongside Summary field / repeating field / relationship / value list / container
  field / AI Account / a layout matching the table name.
- **Design decision: combined single-paste delivery.** Both the blank `script` companion and the
  main reference script are now wrapped in their own `<Script name="...">` elements and delivered
  as two siblings in one `fmxmlsnippet`, pasted directly into the Scripts list to create both at
  once — replacing the earlier two-step manual workflow (paste companion, confirm, then paste
  bare steps into a separately-created open script).
- **Field-prerequisite flow refined**: confirm the target table name first, then offer the
  complete ready-to-paste field set (all data types, all `fieldType`s, every validation/storage
  variant) parameterized to that table — not a piecemeal per-object ask.
- **Duplicate-script gotcha documented as a standing warning, not a one-off note**: FileMaker
  scripts are identified by ID, not name — re-pasting the combined bundle after both scripts
  already exist creates duplicates. Warn every time an updated bundle is delivered, not just the
  first time — this was needed twice in the same session.
- Total confirmed "invalid script step" causes for this single 618-step script: **six**. Treat
  this ratio (roughly one save-blocking defect per ~100 steps, for a script this size generated
  for the first time against a real file) as the expected norm for this workflow, not a sign
  something unusual went wrong.
- No version bump.

### Resolved — third "invalid script step" cause: Add Account missing required fields
- `filemaker-xml`'s only documented `Add Account` skeleton was the bare, unconfigured form
  (`ChgPwdOnNextLogin` + `AddAccount`/`AccountType` only) — no `AccountName`, `Password`, or
  `PrivilegeSet`. That bare form is not save-valid, unlike some other steps' genuinely-valid
  empty/unconfigured forms.
- **Obtained the real structure proactively rather than guessing**: asked the developer to
  manually configure a real `Add Account` step in Script Workspace (Privilege Set: the built-in
  `[Data Entry Only]`) and copy it out, rather than fabricating account/privilege-set XML from
  speculation — treated as too security-adjacent to guess at.
- **Fix**: updated the `Add Account` skeleton to the real, verified configured form —
  `ChgPwdOnNextLogin` → `AccountName` → `Password` → `PrivilegeSet` → `AddAccount`, with
  `AccountName`/`Password` using the standard `<Calculation><![CDATA[...]]></Calculation>`
  wrapper and `PrivilegeSet` as a self-closing `id`/`name` element referencing the built-in
  `[Data Entry Only]` set (safe to reference by name in any file — a FileMaker constant, not
  solution-specific schema).
- **Process bug caught while fixing this**: a file-naming collision between two working files
  (`step_final.json` vs `steps_final.json`) caused an edit to silently apply to the wrong file —
  no error, no effect. Caught by re-inspecting the regenerated script's actual `Add Account`
  content rather than trusting that the edit ran without error — the same class of lesson as an
  earlier regex-edit failure in this same session.
- Now 618 steps total, all three known "invalid script step" causes fixed. The 616-step
  pre-`Add-Account`-fix version was the one independently confirmed to save; this specific
  addition has not yet been independently re-confirmed, though it's built from FileMaker's own
  real exported XML rather than a guess.
- Worth reporting upstream: `filemaker-xml` should have this configured `Add Account` variant
  added to its own spec — genuinely new, verified information that skill didn't have.
- No version bump.

### Added — GetSummary/NPV re-included using confirmed real fields (not yet re-tested)
- Both required objects confirmed to already exist in the target table (`example`, in
  `blank.fmp12`): `ExampleSummary` (Summary field) and `ExampleRepeating` (repeating field).
  Moved `GetSummary`/`NPV` from `FORCE_EXCLUDE` to `SPECIAL` with real field references:
  `GetSummary ( example::ExampleSummary ; example::ExampleNumber )`,
  `NPV ( example::ExampleRepeating ; .05 )`.
- Produces a 367/368-function, 618-step script (only `Self` excluded now). **Not yet
  paste-and-save tested** — the previously-confirmed 616-step version didn't include these two;
  don't claim this version saves until actually verified, per this skill's own completion
  criterion (see "Execution context").
- **Process bug found and fixed**: a separate, non-bundled working-copy generator used earlier in
  the session had drifted out of sync with the bundled `scripts/build_function_calls.py` (missing
  the `Self` fix entirely). A bulk regex edit intended to fix both copies at once silently failed
  on the bundled copy specifically, because its `FORCE_EXCLUDE` entries used multi-line implicit
  string concatenation that the regex's single-line assumption didn't match — no error was
  raised. Caught by checking `Included: N Excluded: M` counts after the "fix" rather than trusting
  the absence of an error. Documented as a lesson in SKILL.md's *Resolved issues* section.
- No version bump.

### Confirmed — full end-to-end save success
- The 616-step reference script (365 functions + resolvable steps, both fixes below applied) was
  pasted and **saved successfully in Script Workspace** — the workflow's actual completion
  criterion, not just clean XML validation, was met for this generation.
- SKILL.md's "Resolved issues" heading and closing caution note updated to record this concrete
  success while still cautioning that future generations (different catalog snapshot, different
  target file) should re-verify rather than assume the same result.
- Noted as a remaining loose end, not yet acted on: `GetSummary`/`NPV` are still excluded from
  this saved script even though the target table has a real Summary field (`ExampleSummary`) —
  the prerequisite-check step exists in this skill because of that exact gap, but the script
  itself was never regenerated to take advantage of it. Left as an explicit note for whoever
  next wants full 368/368 coverage against this target, rather than silently left unmentioned.
- No version bump.

### Resolved — second, separate "invalid script step" cause: transaction-closing steps
### cannot be nested inside If/Else (first attempted fix deployed, tested, found wrong)
- After fixing the `Self` bug below, a distinct second "invalid script step" error appeared,
  traced by the developer directly to the transaction pair demonstrating `Revert Transaction`.
- **First hypothesis:** two independent transaction pairs existed — `Open Transaction`/
  `Commit Transaction`, and a separate `Open Transaction`/`Revert Transaction` with no
  `Commit Transaction` anywhere in that second block. Deployed a fix collapsing both into one
  `Open Transaction` → `If`/`Else`/`End If` branching to Commit or Revert — the pattern
  `fmp-dev-gate` already documents under "Transactions". This passed XML validation and looked
  correct against a known-good FileMaker idiom.
- **That fix was tested and still failed.** Bisected with isolated minimal test snippets, each
  pasted into a fresh empty script one at a time: flat `Open Transaction`→`Commit Transaction`
  saved fine; the same pair with `Commit Transaction` nested inside an `If` (no Else/Revert even
  involved) failed; flat `Open Transaction`→`Commit Transaction`→`Revert Transaction` (both
  closers, no `If` at all) saved fine.
- **Real, tested root cause:** `Commit Transaction`/`Revert Transaction` must be flat and
  unconditional — nesting either inside `If`/`Else` is rejected regardless of context. Not
  documented anywhere in `filemaker-xml`'s spec; found only by testing.
- **Actual fix**: flat, sequential `Open Transaction` → `Commit Transaction` → `Revert Transaction`,
  both closers present, neither nested. Semantically redundant at runtime, structurally valid and
  confirmed to save — documented explicitly as a syntax reference, not a production idiom.
- `references/known-issues.md` and SKILL.md's *Step 6* and *Resolved issues* sections rewritten
  to describe the tested fix, not the first (wrong) hypothesis, with the bisection table kept as
  a record of how it was actually found.
- **Key lesson captured**: a fix that matches a documented general-scripting idiom and passes XML
  validation can still fail to save — test every fix before considering an issue closed, even
  when it "looks right."
- No version bump — content correction to the existing v1.0 release, made the same day it shipped.

### Resolved — root cause of the "won't save" bug found and fixed
- Found by diffing FileMaker's own re-exported copy of the pasted script against the originally
  generated XML (the developer copied the pasted steps back out of Script Workspace after the
  save failure) — a `Set Variable` step calling the zero-argument function `Self`
  (`Set Variable [ $var ; Value: Self ]`). `Self` is only valid inside a Conditional Formatting
  calculation or an object's own calc, not a script context. FileMaker's paste handler accepted it
  structurally, then silently dropped the entire `<Value>` element on save, leaving a
  `Set Variable` with a name and no calculation — rejected by save-time validation.
- **Fix**: `Self` added to `scripts/build_function_calls.py`'s `FORCE_EXCLUDE` table. Regenerating
  now produces 365 (not 366) function calls; confirmed no dangling empty-`<Value>`
  `Set Variable` steps remain in the reassembled script.
- **New debugging technique documented, preferred over bisection**: diff FileMaker's own
  re-exported copy of a pasted script against the originally-generated XML — shows the exact
  offending step in one pass, no repeated save attempts needed. Used to actually find this bug.
- Left as an open question: whether `Self` is the only zero-argument function with this property,
  or whether others share it undetected — re-diff if a future full-surface script fails to save.
- SKILL.md's section renamed from "Known unresolved issue" to "Resolved issue"; frontmatter
  description updated to describe the confirmed exclusion rather than an open question.
- No version bump — content correction to the existing v1.0 release, made the same day it shipped.

### Updated — clipboard-delivery mechanism confirmed, narrowing the save-failure bug
- Direct testing confirmed the "won't save" issue is **not** a clipboard-delivery-mechanism
  problem: writing XML straight to the OS clipboard with MBS Plugin merely installed (no
  FileMaker field/variable, no MBS script call — see `fmp-dev-gate`'s Method 1) pastes correctly
  as real steps. The save failure is a defect in a specific step's XML structure somewhere in the
  assembled script, not in how the XML got onto the clipboard.
- `references/known-issues.md` and SKILL.md's *Known unresolved issue* section both updated to
  rule this out explicitly, so the next debugging attempt bisects script content, not the
  delivery method.
- No version bump — content correction to the existing v1.0 release, made the same day it shipped.

### Initial release

Extracted from a live session that built a 613-step reference script exercising
366 of 368 calculation functions and 216 of 225 script steps against a `blank.fmp12` / `example`
table target.

- **Mandatory prerequisite-check step** — ask which optional schema objects (Summary field,
  repeating field, relationship, value list, container field, AI Account) exist in the target
  file before excluding any function/step that needs one. Added directly in response to
  `GetSummary` being wrongly excluded when the target table already had a Summary field.
- **Known unresolved issue documented** — the assembled script currently fails to save in Script
  Workspace with an "invalid script step" error after a clean paste. Root cause not yet isolated;
  a bisection debugging approach is documented for the next attempt.
- **Generation methodology documented** — sourcing from `claris-filemaker-pro` (catalogs) and
  `filemaker-xml` (verified step-XML skeletons, placeholder-ID pattern), the tokenize-and-classify
  approach for building function calls mechanically, and the hand-special-cased functions
  (`Let`, `While`, `Evaluate`, `Case`, `ExecuteSQL`, `Get()` functions, Aggregate functions) where
  naive positional substitution produces wrong or misleading calls.
- **`scripts/build_function_calls.py`** bundled — the actual generator used in the originating
  session, cleaned up and documented. Verified against a live `function-catalog.json`: 366
  included, 2 excluded with clear reasons, matching the originating session's results exactly.
- **`references/known-issues.md`** — the carried-forward list of exclusions, the 9 script steps
  with no verified XML ID anywhere in `filemaker-xml` (cross-referenced against
  `claris-filemaker-pro`'s own CHANGELOG, which independently flagged the same 9 as having no
  verified `originated_in_version`), the parameter-classifier substring-matching bug that was
  found and fixed during generation (documented so it isn't reintroduced), and a note on the
  60-step catalog gap this same session found and fixed in `claris-filemaker-pro` v1.9.2.
- No GitHub repo yet — no `VERSION` self-check section in SKILL.md. Add one if/when this skill
  gets published, per the skill-creator's own guidance not to fetch a URL that doesn't exist yet.
