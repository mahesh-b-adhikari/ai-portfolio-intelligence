import json
from artifact_tool import Workbook,SpreadsheetFile
from pathlib import Path
P=Path(__file__).parent
SPECS={
'Metadata':['portfolio_id','portfolio_name','purpose','reporting_date'],
'Initiatives':['initiative_id','name','purpose','objective','owner','status','next_milestone','milestone_date','update','percent_complete'],
'Deliverables':['initiative_id','name','weight','status','completion_criteria'],
'Risks':['initiative_id','id','severity','description'],
'Blockers':['initiative_id','id','severity','description'],
'Dependencies':['initiative_id','depends_on_initiative_id','description'],
'Decisions':['initiative_id','decision','needed_by','impact_if_delayed']}
for week in (1,2):
 data=json.loads((P/f'portfolio_week_{week}.json').read_text()); rows={k:[] for k in SPECS}
 rows['Metadata']=[[data[k] for k in SPECS['Metadata']]]
 for a in data['initiatives']:
  rows['Initiatives'].append([a.get(k) for k in SPECS['Initiatives']])
  for section in ('Deliverables','Risks','Blockers'):
   for item in a[section.lower()]:rows[section].append([a['initiative_id']]+[item.get(k) for k in SPECS[section][1:]])
  for dep in a['dependencies']:rows['Dependencies'].append([a['initiative_id'],dep['initiative_id'],dep.get('description')])
  ds=a.get('decisions_needed',a.get('decision_needed'))
  if isinstance(ds,dict):ds=[ds]
  for d in ds or []:rows['Decisions'].append([a['initiative_id']]+[d.get(k) for k in SPECS['Decisions'][1:]])
 wb=Workbook.create()
 for name,cols in SPECS.items():
  sh=wb.worksheets.add(name);matrix=[cols]+rows[name]
  sh.get_range_by_indexes(0,0,len(matrix),len(cols)).values=matrix
  head=sh.get_range_by_indexes(0,0,1,len(cols));head.format.fill='#17324D';head.format.font.color='#FFFFFF';head.format.font.bold=True
  sh.freeze_panes.freeze_rows(1)
  sh.get_range_by_indexes(0,0,len(matrix),len(cols)).format.column_width=23
  if name=='Initiatives':sh.get_range('B:B').format.column_width=34
  if name in ('Risks','Blockers','Dependencies','Decisions'):sh.get_range_by_indexes(0,len(cols)-1, max(2,len(matrix)),1).format.column_width=65
  if name=='Deliverables':sh.get_range('E:E').format.column_width=65
  if name=='Initiatives':sh.get_range('F2:F200').data_validation={'rule':{'type':'list','values':['green','amber','red']}}
  if name=='Deliverables':sh.get_range('D2:D250').data_validation={'rule':{'type':'list','values':['complete','in_progress','not_started']}}
 out=P/f'portfolio_week_{week}.xlsx';SpreadsheetFile.export_xlsx(wb).save(str(out));print(out)
