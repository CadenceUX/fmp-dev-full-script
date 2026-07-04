#!/usr/bin/env python3
"""
Mechanical generator for calculation-function Set Variable XML blocks.

Reads claris-filemaker-pro's function-catalog.json and emits one Set Variable
<Step> per function, with literal arguments type-matched to each parameter
name. Extend SPECIAL / FORCE_EXCLUDE / FIELD_REF below when adding new
hand-cases — do not "fix" a bad call by loosening the classifier's word list,
that's how the substring-matching bug (see references/known-issues.md)
happened the first time.

Usage:
    python3 build_function_calls.py path/to/function-catalog.json > calls.json

Requires Bash/Python execution (Claude Code, SDK, or a code-execution-enabled
chat session) — this is not something a no-code-execution chat session can
run; read SKILL.md's "Execution context" section first.
"""
import json
import re
import sys


def tokenize(param):
    """Split a camelCase/PascalCase/snake_case parameter name into lowercase words."""
    s = re.sub(r'[_\-]', ' ', param)
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', s)
    return [w.lower() for w in s.split() if w]


NUMERIC_WORDS = {
    'number', 'count', 'index', 'position', 'length', 'width', 'height', 'angle', 'year', 'month',
    'day', 'hour', 'minute', 'second', 'seconds', 'value', 'precision', 'places', 'digits',
    'repetitions', 'repetition', 'iterations', 'maxiterations', 'interestrate', 'periods', 'term',
    'payment', 'principal', 'weight', 'red', 'green', 'blue', 'opacity', 'size', 'id', 'from', 'to',
    'start', 'end', 'n', 'x', 'y', 'z', 'rfcnumber', 'rowindex', 'columnindex', 'timeout', 'major',
    'minor', 'option1', 'option2', 'value1', 'value2', 'v1', 'v2', 'parameternumber',
}
TEXT_WORDS = {
    'text', 'string', 'searchstring', 'replacestring', 'name', 'filename', 'path', 'pattern',
    'delimiter', 'separator', 'label', 'message', 'title', 'key', 'format', 'locale', 'language',
    'accountname', 'password', 'layoutname', 'scriptname', 'tablename', 'basetablename',
    'fieldname', 'themename', 'valuelistname', 'url', 'data', 'expression', 'calculation', 'tag',
    'encoding', 'addonid', 'algorithm', 'privatersakey', 'publicrsakey', 'signature', 'uuid',
    'modelname', 'parametername1', 'attributename', 'objectname', 'sensorname', 'standardpath',
    'filemakerpath', 'lineendings', 'valuelist',
}
FIELD_WORDS = {'field', 'container', 'repeatingfield', 'nonrepeatingfield', 'tableoccurrenceorportal'}

# Populate FIELD_REF with real field names from the target file before running
# for real — these are placeholders matching the "example" table built during
# this skill's originating session. Ask the developer for real names first
# (see SKILL.md "Mandatory first step").
FIELD_REF = {
    'container': 'example::ExampleContainer',
    'field': 'example::ExampleText',
    'repeatingfield': 'example::ExampleRepeating',
    'nonrepeatingfield': 'example::ExampleText',
}

# Hand-built canonical calls for functions with documented pitfalls where
# naive positional substitution produces a misleading or invalid call.
SPECIAL = {
    'Let': 'Let ( [ x = 5 ; y = 10 ] ; x * y )',
    'While': 'While ( [ i = 1 ; r = 1 ] ; i <= 5 ; [ r = r * i ; i = i + 1 ] ; r )',
    'Evaluate': 'Evaluate ( "1 + 1" )',
    'EvaluationError': 'EvaluationError ( Evaluate ( "1 + 1" ) )',
    'Case': 'Case ( 1 = 1 ; "true branch" ; "false branch" )',
    'If': 'If ( 1 = 1 ; "true branch" ; "false branch" )',
    'Choose': 'Choose ( 1 ; "zero" ; "one" ; "two" )',
    'ExecuteSQL': 'ExecuteSQL ( "SELECT COUNT ( * ) FROM \\"example\\"" ; "" ; "" )',
    'ExecuteSQLe': 'ExecuteSQLe ( "SELECT COUNT ( * ) FROM \\"example\\"" ; "" ; "" )',
    'RGB': 'RGB ( 255 ; 0 ; 0 )',
    'DatabaseNames': 'DatabaseNames',
    'WindowNames': 'WindowNames',
    'LayoutObjectUUID': 'LayoutObjectUUID',
    'Timestamp': 'Timestamp ( Get ( CurrentDate ) ; Get ( CurrentTime ) )',
    'GetSummary': 'GetSummary ( example::ExampleSummary ; example::ExampleNumber )',  # needs example::ExampleSummary (a real Summary field) and the found set sorted by example::ExampleNumber to be meaningful - the field exists, but ask whether the target's found set is sorted appropriately before relying on the returned value
    'NPV': 'NPV ( example::ExampleRepeating ; .05 )',  # needs example::ExampleRepeating (a real repeating field) - exists structurally but has no populated payment values in a fresh table; syntactically valid, may return 0 until populated
}

# Functions that cannot be faked with a literal in the GENERAL case. Before
# excluding these for a SPECIFIC target file, ask whether the real objects
# they need already exist there (see SKILL.md's mandatory prerequisite check
# and references/known-issues.md for why this list is a starting point, not
# a blanket rule).
FORCE_EXCLUDE = {
    'Self': 'only valid inside a Conditional Formatting calculation or an object\'s own calc - '
            'meaningless in a script Set Variable context. CONFIRMED (2026-07-03) this is the '
            'actual cause of a real "invalid script step" save failure: FileMaker silently '
            'dropped the entire <Value> element on save, leaving Set Variable with a name but '
            'no calculation. Genuinely unfakeable in this general case - there is no script-level '
            'substitute for the object-scoped "self" reference.',
}


def classify(tok):
    if tok in ('json', 'keyorindexorpath'):
        return 'json'
    if tok == 'timestamp':
        return 'timestamp'
    if tok == 'time':
        return 'time'
    if tok == 'date':
        return 'date'
    if tok in FIELD_WORDS:
        return 'field'
    if tok in NUMERIC_WORDS:
        return 'number'
    if tok in TEXT_WORDS:
        return 'text'
    return None


def literal_for(param):
    p_lower = param.lower()
    if p_lower in ('v1', 'v2'):
        return '"[0.1,0.2,0.3]"'
    toks = tokenize(param)
    kind = None
    for t in toks:
        k = classify(t)
        if k:
            kind = k
            break
    if kind == 'json':
        return '"{\\"key\\":\\"value\\"}"'
    if kind == 'timestamp':
        return 'Get ( CurrentTimestamp )'
    if kind == 'time':
        return 'Get ( CurrentTime )'
    if kind == 'date':
        return 'Get ( CurrentDate )'
    if kind == 'field':
        for t in toks:
            if t in FIELD_REF:
                return FIELD_REF[t]
        return FIELD_REF['field']
    if kind == 'number':
        return '1'
    if kind == 'text':
        if toks and toks[0] == 'key':
            return '"key"'
        return '"example"'
    return '"example"'


def build_call(fn):
    name = fn['name']
    fmt = fn['format']
    params = fn.get('parameters', [])
    cat = fn['category']

    if name in FORCE_EXCLUDE:
        return None, FORCE_EXCLUDE[name]
    if name in SPECIAL:
        return SPECIAL[name], None
    if cat == 'Get functions':
        # format is already the complete call, e.g. "Get ( AccountName )" -
        # the parameters entry is the literal constant name, not a runtime arg.
        return fmt, None
    if not params:
        return name, None

    variadic = '...' in fmt
    if cat == 'Aggregate functions':
        args = ['1', '2', '3']
    else:
        args = [literal_for(p) for p in params]
        if variadic and args:
            args = args + [args[-1]]

    return f"{name} ( " + ' ; '.join(args) + " )", None


def set_variable_xml(varname, calc):
    calc = calc.replace(']]>', ']]]]><![CDATA[>')  # guard literal ]]> inside calc
    return (
        '  <Step enable="True" id="141" name="Set Variable">\n'
        '    <Value>\n'
        f'      <Calculation><![CDATA[{calc}]]></Calculation>\n'
        '    </Value>\n'
        '    <Repetition>\n'
        '      <Calculation><![CDATA[1]]></Calculation>\n'
        '    </Repetition>\n'
        f'    <Name>{varname}</Name>\n'
        '  </Step>'
    )


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)

    included, excluded = [], []
    for fn in data['functions']:
        call, reason = build_call(fn)
        if call is None:
            excluded.append({'name': fn['name'], 'category': fn['category'], 'reason': reason})
        else:
            included.append({
                'name': fn['name'], 'category': fn['category'], 'call': call,
                'xml': set_variable_xml(f"$fn_{fn['name']}", call),
            })

    print(json.dumps({'included': included, 'excluded': excluded}, indent=2), file=sys.stdout)
    print(f"Included: {len(included)}  Excluded: {len(excluded)}  Total: {len(data['functions'])}",
          file=sys.stderr)


if __name__ == '__main__':
    main()
