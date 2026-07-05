# Step Configurations

Verified, paste-ready configured XML for script steps whose default/minimal form is not valid to
generate and paste — the target file will reject it on save. Use these forms whenever including
these steps in a generated script; do not use a bare/unconfigured form for any of them.

> **Note:** `filemaker-xml` v1.13 and later documents all six configured forms natively (this
> skill's development contributed them upstream) — prefer that skill's copy as the maintained,
> authoritative source. This file is the bundled fallback for sessions where only a pre-1.13
> script-XML reference is available. Content verified identical against v1.13 on 2026-07-05.

---

## Add Account (id 134)

```xml
<Step enable="True" id="134" name="Add Account">
  <ChgPwdOnNextLogin value="False"/>
  <AccountName>
    <Calculation><![CDATA["example_account"]]></Calculation>
  </AccountName>
  <Password>
    <Calculation><![CDATA["example_password"]]></Calculation>
  </Password>
  <PrivilegeSet id="2" name="[Data Entry Only]"/>
  <AddAccount>
    <AccountType>FileMaker</AccountType>
  </AddAccount>
</Step>
```
Element order: `ChgPwdOnNextLogin` → `AccountName` → `Password` → `PrivilegeSet` → `AddAccount`.
`AccountName`/`Password` use the standard `<Calculation><![CDATA[...]]></Calculation>` wrapper.

**`PrivilegeSet` resolves by `id`, not by name** — corrected 2026-07-05 by live round-trip: a
step pasted with `id="1" name="[Data Entry Only]"` came back as `[Full Access]`, the set whose
ID is 1; the name attribute lost. An earlier round-trip appeared to confirm name resolution
only because it used the matching ID. The built-in IDs are stable FileMaker constants —
`id="1"` = `[Full Access]`, `id="2"` = `[Data Entry Only]`, `id="3"` = `[Read-Only Access]` —
so use the correct ID for the set you intend (as the form above does with `id="2"`); never
substitute a placeholder ID into `PrivilegeSet` the way the general placeholder-ID pattern
allows for `Table`/`Layout`/`Script` references.

---

## Open File (id 33)

```xml
<Step enable="True" id="33" name="Open File">
  <Option state="False"/>
  <FileReference id="1" name="TargetFileName">
    <UniversalPathList>file:TargetFileName.fmp12</UniversalPathList>
  </FileReference>
</Step>
```
`<FileReference>` wraps `id`/`name` attributes plus a `<UniversalPathList>` child using the
`file:` prefix scheme. A safe default for a syntax-reference script is to self-reference the
target file itself — always resolvable, no external dependency.

---

## Perform Script on Server with Callback (id 210)

```xml
<Step enable="True" id="210" name="Perform Script on Server with Callback">
  <CallbackScriptState value="Continue"/>
  <Script id="1" name="script"/>
  <CallbackScript>
    <ScriptName id="1" name="script"/>
  </CallbackScript>
</Step>
```
Element order: `CallbackScriptState` → `Script` → `CallbackScript` (containing `ScriptName`). Note
the two references use **different element names** for what looks like the same kind of
reference — the main script is a bare `<Script id name>` sibling, but the callback's reference is
`<ScriptName id name>` nested inside `<CallbackScript>`.

---

## Save a Copy as XML (id 3)

```xml
<Step enable="True" id="3" name="Save a Copy as XML">
  <Option state="False"/>
  <OutputEntireBinaryData state="False"/>
  <SpecifyJSONOptions state="False"/>
  <UniversalPathList>file:Destination.xml</UniversalPathList>
</Step>
```
`<UniversalPathList>` is a **direct** `<Step>` child (bare, `file:` prefix) — not wrapped in
`<FileReference>` the way `Open File`'s destination is. These two "file destination" steps use
different patterns; don't assume one implies the other.

**Expected re-export difference (FM 26):** FileMaker emits a `<SaXML><JSONOptions>` block on
copy-back **unconditionally** — even with `SpecifyJSONOptions` set to `False` and no `<SaXML>`
in the pasted XML. The minimal form above still pastes and saves; seeing `<SaXML>` appear in the
verification round trip is normalisation, not a defect (confirmed in `filemaker-xml` v1.13).

---

## Fine-Tune Model (id 213)

```xml
<Step enable="True" id="213" name="Fine-Tune Model">
  <Option state="False"/>
  <UniversalPathList type="Embedded"/>
  <Table id="1" name="table_occurrence_name"/>
  <FineTuneLLM>
    <DataSource>DataTable</DataSource>
  </FineTuneLLM>
</Step>
```
`<Table>` needs a real table occurrence reference — self-reference to the target table is fine if
no other table occurrence is available for the demonstration.

---

## Go to Related Record (id 74)

```xml
<Step enable="True" id="74" name="Go to Related Record">
  <Option state="False"/>
  <MatchAllRecords state="False"/>
  <ShowInNewWindow state="False"/>
  <Restore state="True"/>
  <LayoutDestination value="SelectedLayout"/>
  <NewWndStyles Style="Document" Close="Yes" Minimize="Yes" Maximize="Yes" Resize="Yes" Styles="983554"/>
  <Table id="1" name="table_occurrence_name"/>
  <Layout id="1" name="layout_name"/>
</Step>
```
Both `Table` and `Layout` need real references — self-reference to the target table/layout is
fine if no related table occurrence exists for the demonstration. Note `Restore` is `True` (not
`False`), `LayoutDestination` is `SelectedLayout` (not `CurrentLayout`), and `NewWndStyles`'s
`Styles` value is `983554` — these four values change together as a set, not independently.
