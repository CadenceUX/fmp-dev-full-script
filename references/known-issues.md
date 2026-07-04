# Known Issues and Exclusions — carry forward to the next attempt

## Resolved (2026-07-03): seventh and eighth "invalid script step" causes — Fine-Tune Model
## and Go to Related Record, both needing a real Table (and Layout) reference

Same underlying bug class as the others — an unconfigured/"no table set" skeleton that turned
out not to be save-valid.

**`Fine-Tune Model` (id 213)** — was using `<Table id="0" name=""/>`, the documented
"no table set" placeholder. Fixed by self-referencing the target table occurrence:
```xml
<Step enable="True" id="213" name="Fine-Tune Model">
  <Option state="False"/>
  <UniversalPathList type="Embedded"/>
  <Table id="1" name="example"/>
  <FineTuneLLM>
    <DataSource>DataTable</DataSource>
  </FineTuneLLM>
</Step>
```

**`Go to Related Record` (id 74) — this one was not a documentation gap, it was a generator
error.** `filemaker-xml`'s spec already documents a working "Basic form" configured example for
this step — the generator simply used the wrong (unconfigured, "no table set") variant instead
of the one that was already there to use. Fixed by switching to the documented Basic form,
self-referencing `example` for both Table and Layout:
```xml
<Step enable="True" id="74" name="Go to Related Record">
  <Option state="False"/>
  <MatchAllRecords state="False"/>
  <ShowInNewWindow state="False"/>
  <Restore state="True"/>
  <LayoutDestination value="SelectedLayout"/>
  <NewWndStyles Style="Document" Close="Yes" Minimize="Yes" Maximize="Yes" Resize="Yes" Styles="983554"/>
  <Table id="1" name="example"/>
  <Layout id="1" name="example"/>
</Step>
```
Note the attribute differences from the unconfigured form that were easy to miss: `Restore` is
`True` (not `False`), `LayoutDestination` is `SelectedLayout` (not `CurrentLayout`), and
`NewWndStyles`'s `Styles` value is `983554` (not `3606018`) — all four differences matter
together, not just adding the `Table`/`Layout` elements on top of the unconfigured attribute set.

**Lesson: when a step has multiple documented variants (unconfigured, basic configured, fully
configured), don't default to the simplest-looking one without checking whether it's actually
save-valid.** The unconfigured "no table set" form for GTRR is explicitly documented as a real,
observed export state (`filemaker-xml` describes it as coming from a genuinely empty/unset GTRR
dialog) — but "this is what FileMaker exports when unconfigured" is not the same claim as "this
is safe to deliberately generate and expect to save."

## Resolved: LookupField now resolves correctly with a real relationship in place

Not a script step — a field, from the extended field set built earlier in this session. Its
`Lookup` auto-enter was deliberately left unresolved at creation time
(`<Field table="" id="0" name=""/>`, the documented broken-lookup-reference pattern) because no
relationship existed in the target file for it to source from. The developer created a real
relationship (a second table occurrence, `example 2`, related to `example`) and the field now
resolves correctly:
```xml
<Lookup>
  <Table id="1065090" name="example"/>
  <Field table="example 2" id="32" name="PrimaryKey"/>
  <NoMatchCopyOption value="DoNotCopy"/>
  <CopyEmptyContent value="False"/>
</Lookup>
```
**Useful structural confirmation**: the outer `<Table>` inside `<Lookup>` was *already* resolved
to `example` (the field's own table) even before the relationship existed — it describes the
field's own context, not the related side, and doesn't depend on a relationship at all. The part
that actually needs a real relationship to resolve is specifically the inner
`<Field table="RelatedTOName" id name>` — its `table` attribute is the name of the *related*
table occurrence reached via the relationship graph, not the field's own table. Don't conflate
the two `Table`-ish references in this element — only one of them is relationship-dependent.

**This sharpens the existing "A relationship / table occurrence" prerequisite-check row**: it's
not enough to ask "does a relationship exist" in the abstract — for a Lookup field specifically,
confirm the *related table occurrence's name* and a *real field name on that occurrence* to
reference, since both appear literally in the generated `<Field table name>` attributes.

## Resolved (2026-07-03): fourth, fifth, sixth "invalid script step" causes — three more
## steps with undocumented configured forms, all fixed using real captured XML

Same bug class as `Add Account` below: `filemaker-xml`'s only documented skeleton for each of
these was a bare/unconfigured form missing a reference element the step actually needs to be
save-valid. All three were fixed the same way — asked the developer to manually configure the
real step in Script Workspace and copy it out, rather than guessing.

**`Open File` (id 33)** — no `<FileReference>` at all in the documented skeleton. Real structure:
```xml
<Step enable="True" id="33" name="Open File">
  <Option state="False"/>
  <FileReference id="1" name="Blank">
    <UniversalPathList>file:Blank.fmp12</UniversalPathList>
  </FileReference>
</Step>
```
Fixed by pointing at the target file itself (`Blank.fmp12`) — safe, always-resolvable, no
external dependency for a syntax-reference script.

**`Perform Script on Server with Callback` (id 210)** — the documented skeleton's
`<CallbackScript/>` was a bare empty tag with no actual script reference, and there was no
reference for the main "script to perform" either — two separate "unknown" script slots. Real
structure:
```xml
<Step enable="True" id="210" name="Perform Script on Server with Callback">
  <CallbackScriptState value="Continue"/>
  <Script id="1" name="script"/>
  <CallbackScript>
    <ScriptName id="1" name="script"/>
  </CallbackScript>
</Step>
```
Note the two different element names for what looks like the same kind of reference: the main
script uses `<Script id name>`, but the callback wraps its reference in `<ScriptName id name>`
inside `<CallbackScript>` — not the same tag name, easy to get wrong by assuming symmetry.

**`Save a Copy as XML` (id 3)** — the documented skeleton (both the pre-FM26 minimal form and the
FM26-expanded form with `SaXML`/`JSONOptions`) never included a destination file path at all.
Real structure adds a direct `<UniversalPathList>` child (not wrapped in `<FileReference>` the
way `Open File`'s destination is — these two "file destination" steps use different patterns,
don't assume one implies the other):
```xml
<Step enable="True" id="3" name="Save a Copy as XML">
  <Option state="False"/>
  <OutputEntireBinaryData state="False"/>
  <SpecifyJSONOptions state="False"/>
  <UniversalPathList>file:Blank.xml</UniversalPathList>
  <!-- <SaXML>/<JSONOptions> follow automatically on FileMaker's own re-export -->
</Step>
```

**Checked and confirmed fine, no fix needed:** `Go to Layout`'s `<Layout id="1" name="example"/>`
(using the target table's name as the layout name) was suspected as a likely seventh issue —
tables don't automatically get a same-named layout in FileMaker — but the developer confirmed a
layout literally named `example` already existed in this target file, and the reference resolved
correctly. **This is target-file-specific, not a general guarantee** — a different target file
without a same-named layout would still hit this. Don't treat this as "solved for all cases," only
"solved for this specific file because the layout happens to exist there."

**Total now: six confirmed "invalid script step" causes found and fixed in this single
618-step script** (`Self`, transaction nesting, `Add Account`, `Open File`,
`Perform Script on Server with Callback`, `Save a Copy as XML`). This is a strong signal that
**any full-surface script covering the entire step catalog should expect multiple rounds of this
same failure mode** — budget for it rather than treating each fix as likely-the-last-one.

## Design decision (2026-07-03): dedicated blank `script` companion instead of self-reference

`Perform Script`, `Perform Script on Server`, `Install OnTimer Script`, and
`Perform Script on Server with Callback` all need a real script name to reference. Two options
were considered:
1. **Self-reference** — have the reference script call itself by whatever name it's saved under.
2. **A dedicated blank companion script**, literally named `script`, that the developer creates
   ahead of time purely as a safe target for these steps to point at.

**Went with option 2, and the reason matters more than the mechanism**: self-reference would
cause infinite recursion if anyone actually *ran* the pasted reference script (each
`Perform Script` call would call the whole script again, forever). A separate blank companion —
`Allow User Abort [Off]` → `Set Error Capture [On]` → `Exit Script [""]`, nothing else — is safe
to actually invoke and eliminates the risk entirely. This is now a standing prerequisite for this
skill's workflow: **a blank script literally named `script` must exist in the target file before
generating the full reference script**, alongside the schema-object prerequisites already
documented. Offer the ready-to-paste blank-script XML as part of the same setup conversation,
the same way the full field set is offered.

## Design decision (2026-07-03): combine both scripts into one paste via sibling `<Script>` elements

Originally the workflow was: paste the blank `script` companion separately (as its own
`<Script>`-wrapped snippet), confirm it landed, then separately paste the 618 bare `<Step>`
elements into an already-open, manually-created new script. **This was unnecessarily manual** —
both the companion and the main reference script can be wrapped in their own `<Script name="...">`
element and combined as two siblings inside one `fmxmlsnippet`, then pasted once directly into
the Scripts list (not into an already-open script) to create both simultaneously:
```xml
<fmxmlsnippet type="FMObjectList">
  <Script enable="True" name="script">...3 steps...</Script>
  <Script enable="True" name="Reference Script">...618 steps...</Script>
</fmxmlsnippet>
```
**Real gotcha when re-delivering an updated bundle**: FileMaker scripts are identified internally
by ID, not name — pasting this combined bundle again after both scripts already exist (e.g. after
fixing a bug and regenerating) creates **duplicates**, it does not merge or overwrite by name. The
developer must delete both existing scripts before pasting an updated combined bundle. This
happened twice in this session and needs to be called out proactively every time an updated
bundle is delivered, not left as a surprise.

## Resolved (2026-07-03): third "invalid script step" — Add Account missing required fields

**Symptom:** after the `Self` and transaction fixes below, the 618-step script still failed on
`Add Account` (id 134) specifically.

**Root cause:** the `filemaker-xml` skill's only documented `Add Account` skeleton was the bare,
unconfigured form:
```
<Step enable="True" id="134" name="Add Account">
  <ChgPwdOnNextLogin value="False"/>
  <AddAccount>
    <AccountType>FileMaker</AccountType>
  </AddAccount>
</Step>
```
No `AccountName`, `Password`, or `PrivilegeSet` — and unlike some other steps' bare/unconfigured
forms (e.g. `Commit Transaction`'s empty self-closing form, which is genuinely valid), this
particular bare form is not save-valid. `filemaker-xml`'s spec never documented a configured
variant to fall back on.

**How the real structure was obtained — same technique as the `Self` fix, applied proactively
this time instead of after another failed guess:** rather than guess candidate XML, the developer
was asked to manually configure a real `Add Account` step in Script Workspace (Account Name:
placeholder, Password: placeholder, Privilege Set: the built-in `[Data Entry Only]`), copy just
that step, and paste the native XML back. This is preferable to guessing for anything
security/account-related — getting Add Account XML wrong from speculation risks more than a
failed save.

**Real, verified structure (native FileMaker export, DisableStepCollapsed omitted):**
```xml
<Step enable="True" id="134" name="Add Account">
  <ChgPwdOnNextLogin value="False"/>
  <AccountName>
    <Calculation><![CDATA["test"]]></Calculation>
  </AccountName>
  <Password>
    <Calculation><![CDATA["test"]]></Calculation>
  </Password>
  <PrivilegeSet id="2" name="[Data Entry Only]"/>
  <AddAccount>
    <AccountType>FileMaker</AccountType>
  </AddAccount>
</Step>
```
Element order: `ChgPwdOnNextLogin` → `AccountName` → `Password` → `PrivilegeSet` → `AddAccount`.
`AccountName`/`Password` use the same `<Calculation><![CDATA[...]]></Calculation>` wrapper as
other calculation-bearing elements. `PrivilegeSet` is a self-closing element with `id`/`name`
attributes — `[Data Entry Only]` is one of FileMaker's three built-in privilege sets (alongside
`[Full Access]` and `[Read-Only Access]`) present in every file by default, including the square
brackets in its literal name — safe to reference by name in any target file without the
placeholder-ID pattern's usual "does this object exist" caveat, since it's a FileMaker constant,
not solution-specific schema.

**Fix applied:** the reference script's `Add Account` skeleton updated to this configured form,
using placeholder account/password text and the built-in `[Data Entry Only]` privilege set.

**Worth reporting upstream:** `filemaker-xml`'s spec should have this configured variant added —
it's genuinely new, verified information that skill didn't have before.

**Process note:** while fixing this, a file-naming collision in the generator's working files
(`step_final.json` vs `steps_final.json` — singular/plural, easy to misread) caused an edit to
silently apply to the wrong file, producing no error but also no effect. Caught by re-inspecting
the regenerated script's actual `Add Account` content rather than assuming the edit took effect.
Same class of lesson as the `FORCE_EXCLUDE` regex failure noted elsewhere in this file: verify the
actual regenerated output, don't trust that an edit script ran without error.

## Resolved (2026-07-03): the "won't save" bug, root cause and fix

**Symptom:** the generated script pasted successfully but failed to save in Script Workspace with
an "invalid script step" error.

**Ruled out first:** this was not a clipboard-delivery-mechanism problem. The delivery method
used (Claude writes XML directly to the OS clipboard, MBS Plugin merely installed, no FileMaker
field/variable, no MBS script call) was independently confirmed to work — the paste was correctly
recognized as real steps by Script Workspace.

**Root cause, found by diffing FileMaker's own re-exported copy of the pasted script against the
originally-generated XML** (the developer copied the pasted script's steps back out of Script
Workspace after the save failure, which is the actual debugging technique that cracked this —
simpler and more direct than the bisection approach originally planned): one `Set Variable` step
called the `Self` function with no arguments (`Set Variable [ $fn_264_Self ; Value: Self ]`).
`Self` is only valid inside a Conditional Formatting calculation or an object's own calc — it is
meaningless in a script's `Set Variable` context, since there's no "self" object to refer to
there. FileMaker's paste handler accepted the step structurally, but on save it silently dropped
the entire `<Value>` element, leaving a `Set Variable` step with a name and no calculation —
which FileMaker's save-time validation then rejected as an "invalid script step."

**Fix applied:** `Self` added to `scripts/build_function_calls.py`'s `FORCE_EXCLUDE` table.
Regenerating with the fixed script produces 365 (not 366) function calls and a script confirmed
to have no dangling `Set Variable` with an empty `<Value>`.

**Lesson for the next full-surface attempt:** diffing FileMaker's own re-exported copy of a
pasted-and-saved (or pasted-and-failed) script against the originally-generated XML is a more
direct debugging technique than bisecting by half — it shows exactly which step's content
FileMaker itself considers different from what was sent, in one pass, without needing multiple
save attempts. Prefer this over bisection when the developer can copy the current script state
back out of Script Workspace.

**Residual open question:** whether `Self` is the *only* zero-argument function whose bare name
is invalid in a script context, or whether others share this property and simply haven't been
exercised yet. No other function in the 368-function catalog is known to have this issue, but it
was only found by testing, not by inspection — a similarly-shaped function could exist undetected.
Re-run the full script after any catalog update and re-diff if save failures recur.

## Resolved (2026-07-03): second, separate "invalid script step" — Transaction-closing steps
## cannot be nested inside If/Else (two wrong hypotheses ruled out by direct testing first)

**Symptom:** after fixing the `Self` bug above, a second, distinct "invalid script step" error
appeared — this one traced to the transaction pair intended to demonstrate `Revert Transaction`.

**First hypothesis (wrong, but a useful step): the original assembly generated two independent
transaction pairs** — `Open Transaction` → `Commit Transaction`, and a *separate*
`Open Transaction` → `Revert Transaction` with no `Commit Transaction` anywhere in that second
block. The developer's own diagnosis was that the second `Open Transaction` lacked a
`Commit Transaction` to close it.

**First fix attempt (deployed, then proven wrong by testing):** collapsed both pairs into one
block using the pattern `fmp-dev-gate` already documents under "Transactions" — `Open Transaction`
→ `If` → `Commit Transaction` → `Else` → `Revert Transaction` → `End If`. This looked correct on
paper (matches a documented FileMaker idiom) and passed XML validation, but **the developer
tested it and it still failed to save** with the same generic "invalid script step" error.

**Bisected with 4 minimal isolated test snippets, tested one at a time in a fresh empty script
(the technique that actually found the real rule — don't skip this step next time just because a
fix looks structurally correct):**

| Test | Structure | Result |
|---|---|---|
| A | `Open Transaction` → `Commit Transaction`, flat, no `If` | **Saves fine** |
| B | `Open Transaction` → `If` → `Commit Transaction` (nested) → `End If`, no Else/Revert | **Fails** |
| D | `Open Transaction` → `Commit Transaction` → `Revert Transaction`, both flat, no `If` | **Saves fine** |

(Test C — `If`/`Commit`/`Else`/`Revert`/`End If` with no `Open Transaction` at all — was prepared
but not needed once B failed; B alone already isolated the real constraint.)

**Real root cause, confirmed by direct testing, not documentation:** `Commit Transaction` and
`Revert Transaction` must be **flat, unconditional, top-level steps** — nesting either one inside
an `If`/`Else` is rejected as an invalid script step, regardless of whether `Open Transaction` is
present, regardless of whether only one or both are nested. This is not documented anywhere in
`filemaker-xml`'s spec (which shows the individual step skeletons but says nothing about their
required relationship to each other) — it was found empirically, and should be added to that
skill's spec if a maintainer has a way to contribute back.

**Actual fix applied:** flat, sequential, unconditional `Open Transaction` → `Commit Transaction`
→ `Revert Transaction` — both closing steps present, neither nested in a conditional. This is
semantically redundant at runtime (a transaction that's committed then "reverted" does nothing
on the revert) but is structurally valid and confirmed to save. This is a syntax-reference
script, not a demonstration of correct production transaction logic — do not present this
pattern as a real-world idiom; note the redundancy explicitly if a developer asks why it looks
odd.

**Lesson for the next full-surface attempt:** when a "looks correct on paper" fix is deployed,
**test it before considering the issue closed** — the `fmp-dev-gate`-documented If/Else branching
pattern is a legitimate *general FileMaker scripting idiom* for real production code (conditional
commit-vs-revert logic), but that does not mean it survives round-trip through this XML paste
format unchanged. A pattern being good general FileMaker advice and a pattern being
paste-XML-safe are two different claims — verify both, don't assume one implies the other.

**This is now the second of two "invalid script step" causes found in this same script** — a
reminder that clearing one save error does not mean the script is clean; re-attempt the save
after every fix and be ready to repeat the diagnosis process. Bisecting with small, targeted,
isolated test snippets (one variable changed at a time, tested in a fresh empty script) found the
real rule in 3 rounds after the diff technique and the developer's own direct diagnosis both
proved insufficient on their own — prefer this technique when a fix doesn't hold up under test.

## Prerequisite-check miss (fixed process, noted here as the concrete example)

`GetSummary()` was excluded from a generated script on the general-case assumption that no real
Summary field existed in the target table to reference. The target table actually had one
(`ExampleSummary`) — created earlier in the same session, before the reference script was
generated. The exclusion was avoidable. This is why SKILL.md now makes the prerequisite check
mandatory and first: ask the developer what schema objects the *actual* target file has, don't
reason from what's typically true of a blank/generic file.

## Genuinely unresolvable, general case

**Functions (as of this skill's creation):**
- `GetSummary` — needs a real Summary field + a sorted break field. Include if the target file
  has one (ask first); otherwise exclude and say why.
- `NPV` — the `payment` parameter needs a real repeating field with an unequal payment series; a
  plain number literal is rejected at the field-type level. Include if the target file has a
  suitable repeating field (ask first); otherwise exclude and say why.

**Script steps — no verified XML step ID anywhere in `filemaker-xml`'s reference material** (not
in a skeleton, not in a "no-option steps" table, not in the routing index):
- `Check Spelling`
- `Log Out`
- `Manage Add-ons`
- `Navigate to Object`
- `Open Preferences`
- `Set Window Animation`
- `Show Alert`
- `Show/Hide Script Editor`
- `Show/Hide Status Toolbar`

These are the same 9 steps `claris-filemaker-pro`'s own CHANGELOG independently flagged as having
no verified `originated_in_version` — corroborating evidence, not coincidence. If `filemaker-xml`
is updated to cover any of these, remove it from this list and wire it into the generator.

## Catalog completeness (fixed upstream, note for anyone working from an older copy)

`claris-filemaker-pro`'s `script-steps-catalog.json` undercounted the real FileMaker step roster
by 60 steps prior to v1.9.2 — cross-checking its step names against `filemaker-xml`'s
independently-verified step IDs surfaced steps that were simply never added (not duplicates or
renames), concentrated in `Open Menu Item` (half missing), an entire absent "Data File I/O"
sub-family under `Files`, and most of `Spelling`. Fixed in `claris-filemaker-pro` v1.9.2 — if
working from a copy older than that, re-fetch the catalog before trusting its step count.

## Parameter-classifier bug (fixed, documented so it isn't reintroduced)

An early version of the function-call generator's parameter-type classifier used raw substring
matching for short hint tokens (`'x'`, `'n'`, `'y'`, `'z'`). Since substring matching doesn't
respect word boundaries, `"text"` (contains `'x'`) and `"fileNameWithExtension"` (contains `'n'`)
were misclassified as numeric parameters, producing wrong-typed literal arguments across dozens
of functions before this was caught by spot-checking output. Fixed by tokenizing parameter names
on camelCase/snake_case word boundaries and matching whole words only. Any future change to
`scripts/build_function_calls.py`'s classifier should keep this constraint — never substring-match
a hint word shorter than about 4 characters.
