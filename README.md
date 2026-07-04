# fmp-dev-full-script

A [Claude skill](https://docs.claude.ai/skills) for generating a single, comprehensive FileMaker
Pro script that exercises every resolvable script step and calculation function against a target
file — built for regression-testing FileMaker script/function reference catalogs, or for
producing a working demonstration of the full FileMaker step/function surface.

Built and maintained by [Darrin Southern](https://www.linkedin.com/in/darrin-southern/) from [CadenceUX](https://cadenceux.com.au).

---

## What it does

When this skill is active, Claude will:

- **Guide you through setup first** — confirming MBS Plugin (recommended for delivery, not
  required — see `fmp-dev-orchestrator` for alternatives), creating a blank companion script for
  `Perform Script`-type steps to reference safely, and confirming the target table has the schema
  objects (Summary field, repeating field, relationship, value list, container field, layout) a
  full-coverage script needs — offering ready-to-paste XML for anything missing
- Generate one `Set Variable` step per calculation function, using type-matched literal
  arguments built by tokenizing each parameter name
- Generate one script step per resolvable step type, using verified configured forms for the
  handful of steps whose default form isn't valid to paste
- **Deliver both the companion script and the reference script in a single combined paste**
- **Walk you through a save-and-copy-back verification step** after pasting, to confirm the
  script actually landed correctly in FileMaker rather than just assuming a clean paste means
  everything is correct

## What it does not do

- It is not a general scripting skill — use a general-purpose FileMaker scripting skill for
  everyday script authoring
- It does not bundle FileMaker's full function/script-step catalogs or paste-XML format spec —
  it depends on a FileMaker function/step reference skill and a FileMaker script-XML skill being
  available (see *Required reference skills* in `SKILL.md`)

## Limitations

See [`references/limitations.md`](./references/limitations.md) for the current list of functions
and script steps excluded from a general-case script, and why.

## Installation

1. Download the latest release zip
2. Unzip and place the `fmp-dev-full-script` folder in your Claude skills directory:
   - **macOS:** `~/Library/Application Support/Claude/skills/`
   - **Windows:** `%APPDATA%\Claude\skills\`
3. Restart Claude or reload skills

## Execution context

Building the full script (368 functions + 215 steps) is a code-execution task. It runs from
Claude Code, the Agent SDK, or a Claude.ai session with code execution enabled. It is not
reliably achievable in a no-code-execution chat session.

## Contributing

Issues and PRs welcome — particularly:
- Coverage for any of the currently-unresolvable script steps listed in
  `references/limitations.md`, if a verified paste-ready skeleton becomes available for one
- Corrections or additions to `references/step-configurations.md`
- Improvements to the parameter-type classifier in `scripts/build_function_calls.py`

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, adapt, and redistribute
with attribution.
