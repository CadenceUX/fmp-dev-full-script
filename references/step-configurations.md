# Step Configurations

Verified, paste-ready configured XML for script steps whose default/minimal form is not valid to
generate and paste — the target file will reject it on save. Use these forms whenever including
these steps in a generated script; do not use a bare/unconfigured form for any of them.

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
`PrivilegeSet` is self-closing with `id`/`name` attributes — FileMaker's three built-in privilege
sets (`[Full Access]`, `[Data Entry Only]`, `[Read-Only Access]`) resolve by name, including the
literal square brackets, in any file, since they're FileMaker constants rather than
solution-specific schema.

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
