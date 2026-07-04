# Limitations

Functions and script steps excluded from a general-case full-surface script, and why. Confirm
with the developer whether the specific target file has what's needed before excluding any of
these — see the *Setup* checklist in `SKILL.md`.

## Functions with no general-case literal substitute

- **`Self`** — only valid inside a Conditional Formatting calculation or an object's own calc.
  Meaningless in a script's `Set Variable` context; there is no script-level substitute.
- **`GetSummary`** — needs a real Summary field and the found set sorted by an appropriate break
  field. A plain field or literal cannot substitute for either requirement.
- **`NPV`** — the `payment` parameter needs a real repeating field containing a payment series. A
  plain number is rejected at the field-type level.

`GetSummary` and `NPV` can both be included for a specific target file once the developer confirms
it has the required field — reference the real field name instead of excluding the function.

## Script steps with no verified paste-ready structure

An earlier version of this list named nine steps (`Check Spelling`, `Log Out`, `Manage Add-ons`,
`Navigate to Object`, `Open Preferences`, `Set Window Animation`, `Show Alert`,
`Show/Hide Script Editor`, `Show/Hide Status Toolbar`) as having no confirmed XML structure.
That list traced back to bad entries in the source step catalog, corrected 2026-07-04 against
live Claris docs:

- **Six of the nine don't exist as FileMaker Pro script steps at all** — `Check Spelling`,
  `Log Out`, `Manage Add-ons`, `Set Window Animation`, `Show Alert`, `Show/Hide Script Editor`.
  There is nothing to generate; they should never appear in a generated script.
- **Two were misnamed real steps** — the real steps are `Go to Object` (not "Navigate to
  Object") and `Show/Hide Toolbars` (not "Show/Hide Status Toolbar"). Under their correct names
  these are ordinary steps; generate them normally.
- **`Open Preferences` is a real step** with no options — its paste structure just hasn't been
  verified yet.

The corrected catalog (claris-filemaker-pro, 2026-07-04) also added 58 real steps that earlier
generated scripts never attempted — the Data File family, most Spelling steps, nine Open Menu
Item steps, Send Mail, Perform AppleScript, Perform JavaScript in Web Viewer, Save a Copy as
XML, Set Error Logging, Truncate Table, and more. **None of these have been paste-verified in a
generated full-surface script yet.** Treat their XML structures as unverified until a
save-and-copy-back round trip confirms them; steps whose structure can't be sourced from a
verified reference should still be excluded rather than guessed at.

## A note on schema references that won't resolve

A generated script can reference schema objects (a relationship, a value list, a container with
real data) that don't exist in a specific target file. This doesn't stop the script from pasting
or saving — the reference just won't resolve to anything functional until the real object exists.
This is different from the steps and functions listed above, which cannot be generated as valid
syntax at all in the general case.
