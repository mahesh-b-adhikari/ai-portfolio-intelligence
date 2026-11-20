"""Convert seven-tab portfolio Excel workbooks into validated pipeline JSON.

Requires: python3 -m pip install openpyxl
Usage: python3 ingest_portfolio.py portfolio_week_2.xlsx test_week_2.json
"""
import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from openpyxl import load_workbook

SHEETS = {
    'Metadata': ['portfolio_id', 'portfolio_name', 'purpose', 'reporting_date'],
    'Initiatives': ['initiative_id', 'name', 'purpose', 'objective', 'owner', 'status', 'next_milestone', 'milestone_date', 'update', 'percent_complete'],
    'Deliverables': ['initiative_id', 'name', 'weight', 'status', 'completion_criteria'],
    'Risks': ['initiative_id', 'id', 'severity', 'description'],
    'Blockers': ['initiative_id', 'id', 'severity', 'description'],
    'Dependencies': ['initiative_id', 'depends_on_initiative_id', 'description'],
    'Decisions': ['initiative_id', 'decision', 'needed_by', 'impact_if_delayed'],
}

def read_sheet(workbook, name, required):
    if name not in workbook.sheetnames:
        raise ValueError(f'Missing worksheet: {name}')
    values = workbook[name].iter_rows(values_only=True)
    header = next(values, None)
    if not header:
        raise ValueError(f'{name}: missing header row')
    headers = [str(v).strip() if v is not None else '' for v in header]
    if len(headers) != len(set(h for h in headers if h)):
        raise ValueError(f'{name}: duplicate column headers')
    missing = [h for h in required if h not in headers]
    if missing:
        raise ValueError(f'{name}: missing columns: {missing}')
    if name == 'Decisions':
        missing = [h for h in ('id', 'status') if h not in headers]
        if missing:
            raise ValueError(f'Decisions: missing columns {missing}. Add id and status columns; do not infer them.')
    result = []
    for number, row in enumerate(values, start=2):
        record = dict(zip(headers, row))
        if not any(record.get(h) not in (None, '') for h in required):
            continue
        result.append(record)
    return result

def datestr(value):
    if isinstance(value, (date, datetime)):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, (int, float)):
        return (datetime(1899, 12, 30) + timedelta(days=value)).strftime('%Y-%m-%d')
    datetime.strptime(str(value), '%Y-%m-%d')
    return str(value)

def ingest(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    rows = {name: read_sheet(workbook, name, required) for name, required in SHEETS.items()}
    if len(rows['Metadata']) != 1:
        raise ValueError('Metadata must contain exactly one row')
    metadata = {key: rows['Metadata'][0][key] for key in SHEETS['Metadata']}
    metadata['reporting_date'] = datestr(metadata['reporting_date'])
    initiatives = []
    by_id = {}
    for raw in rows['Initiatives']:
        initiative = {key: raw[key] for key in SHEETS['Initiatives']}
        identifier = initiative['initiative_id']
        if not identifier or identifier in by_id:
            raise ValueError(f'Missing or duplicate initiative ID: {identifier}')
        if initiative['status'] not in ('green', 'amber', 'red'):
            raise ValueError(f'{identifier}: invalid status')
        initiative['milestone_date'] = datestr(initiative['milestone_date'])
        initiative.update(deliverables=[], risks=[], blockers=[], dependencies=[], decisions_needed=[])
        initiatives.append(initiative)
        by_id[identifier] = initiative

    for sheet, field in [('Deliverables','deliverables'), ('Risks','risks'), ('Blockers','blockers'), ('Dependencies','dependencies')]:
        for raw in rows[sheet]:
            identifier = raw['initiative_id']
            if identifier not in by_id:
                raise ValueError(f'{sheet}: unknown initiative {identifier}')
            row = {key: raw[key] for key in SHEETS[sheet] if key != 'initiative_id'}
            if sheet == 'Deliverables':
                if row['status'] not in ('complete','in_progress','not_started'):
                    raise ValueError(f'{identifier}: invalid deliverable status')
                row['weight'] = int(row['weight'])
                if not 0 <= row['weight'] <= 100:
                    raise ValueError(f'{identifier}: invalid weight')
            if sheet in ('Risks','Blockers') and row['severity'] not in ('low','medium','high','critical'):
                raise ValueError(f'{identifier}: invalid severity')
            if sheet == 'Dependencies':
                row = {'initiative_id': row['depends_on_initiative_id'], 'description': row['description']}
            by_id[identifier][field].append(row)

    for raw in rows['Decisions']:
        identifier = raw['initiative_id']
        if identifier not in by_id:
            raise ValueError(f'Decisions: unknown initiative {identifier}')
        if not raw.get('id') or not raw.get('status'):
            raise ValueError(f'{identifier}: decision id and status are required')
        if not raw.get('decision'):
            raise ValueError(f'{identifier}: decision description is required')
        by_id[identifier]['decisions_needed'].append({
            'id': raw['id'],
            'description': raw['decision'],
            'due_date': datestr(raw['needed_by']),
            'status': raw['status'],
            'impact_if_delayed': raw['impact_if_delayed'],
        })

    for initiative in initiatives:
        identifier = initiative['initiative_id']
        if sum(d['weight'] for d in initiative['deliverables']) != 100:
            raise ValueError(f'{identifier}: deliverable weights must sum to 100')
        completion = sum(d['weight'] for d in initiative['deliverables'] if d['status'] == 'complete')
        if int(initiative['percent_complete']) != completion:
            raise ValueError(f'{identifier}: completion mismatch')
        initiative['percent_complete'] = completion
        for dep in initiative['dependencies']:
            if dep['initiative_id'] not in by_id:
                raise ValueError(f'{identifier}: unknown dependency {dep["initiative_id"]}')
        for field in ('risks','blockers','decisions_needed'):
            identifiers = [row['id'] for row in initiative[field]]
            if len(identifiers) != len(set(identifiers)):
                raise ValueError(f'{identifier}: duplicate {field} IDs')
    return {**metadata, 'initiatives': initiatives}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('workbook')
    parser.add_argument('output')
    arguments = parser.parse_args()
    result = ingest(arguments.workbook)
    Path(arguments.output).write_text(json.dumps(result, indent=2) + '\n')
    print(f'Validated {len(result["initiatives"])} initiatives: {arguments.output}')
