# fmp-dev-full-script

A [Claude skill](https://docs.claude.ai/skills) for generating a single, comprehensive FileMaker
Pro script that exercises every resolvable script step and calculation function against a target
file — built for regression-testing the `claris-filemaker-pro` and `filemaker-xml` skills'
catalogs, or for producing a working demonstration of the full FileMaker step/function surface.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).

---

## What it does

When this skill is active, Claude will:

- Ask, before generating anything, which optional schema objects (Summary field, repeating
  field, relationship/table occurrence, value list, container field, configured AI Account)
  already exist in the target file — rather than assuming a generic file's limitations apply
- Generate one `Set Variable` step per calculation function (366 of 368 — the 2 exceptions are
  documented, not silently dropped), using type-matched literal arguments built by tokenizing
  each parameter name
- Generate one script step per resolvable step type, sourced from `filemaker-xml`'s verified XML
  skeletons — never a guessed step ID
- Flag the known, currently-unresolved issue that the assembled script fails to *save* in Script
  Workspace ("invalid script step") even after a clean paste, and document the bisection approach
  to isolate the cause next time

## What it does not do

- It is not a general scripting skill — for everyday script authoring, use `fmp-dev-gate`
- It does not duplicate the `claris-filemaker-pro` function/step catalogs or the `filemaker-xml`
  XML spec — it reads them live each time, so it never drifts out of sync with those skills
- It does not claim the generated script actually saves in FileMaker — that's the open issue
  this skill exists partly to track

## Known issues

See [`references/known-issues.md`](./references/known-issues.md) for the full, current list:
the unresolved save failure, the two functions that genuinely can't be faked with a literal in
the general case, the 9 script steps with no verified XML ID anywhere, and a parameter-classifier
bug that was found and fixed during this skill's creation (documented so it isn't reintroduced).

## Installation

1. Download the latest release zip
2. Unzip and place the `fmp-dev-full-script` folder in your Claude skills directory:
   - **macOS:** `~/Library/Application Support/Claude/skills/`
   - **Windows:** `%APPDATA%\Claude\skills\`
3. Restart Claude or reload skills

## Execution context

Building the full script (368 functions + 225 steps) is a code-execution task. It runs from
Claude Code, the Agent SDK, or a Claude.ai session with code execution enabled. It is not
reliably achievable in a no-code-execution chat session — attempting the full surface by hand is
exactly how a parameter-classifier bug was introduced during this skill's own creation.

## Contributing

Issues and PRs welcome — particularly:
- A fix for the "invalid script step" save failure once isolated
- Coverage for any of the 9 currently-unresolvable script steps, if `filemaker-xml` adds a
  verified skeleton for one
- Corrections to the parameter-type classifier in `scripts/build_function_calls.py`

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, adapt, and redistribute
with attribution.
