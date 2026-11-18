import json, sys, urllib.request
from pathlib import Path
root=Path('art/YU7_UNREAL/reports/ue59_mcp')
url='http://127.0.0.1:8001/mcp'
def req(payload, headers={}):
    r=urllib.request.urlopen(urllib.request.Request(url,json.dumps(payload).encode(),{'Content-Type':'application/json','Accept':'application/json, text/event-stream',**headers}),timeout=45)
    raw=r.read().decode()
    if raw.startswith('event:') or raw.startswith('data:'):
        raw=next(x[5:].strip() for x in raw.splitlines() if x.startswith('data:'))
    return (json.loads(raw) if raw.strip() else {}),dict(r.headers)
i,h=req({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'VehicleStudio-copy-readonly-check','version':'1'}}})
headers={'MCP-Protocol-Version':i['result']['protocolVersion']}
for k,v in h.items():
    if k.lower()=='mcp-session-id': headers['Mcp-Session-Id']=v
req({'jsonrpc':'2.0','method':'notifications/initialized'},headers)
params=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')) if len(sys.argv)>1 else {'name':'list_toolsets','arguments':{}}
r=[]
for n,param in enumerate(params if isinstance(params,list) else [params]):
    result,_=req({'jsonrpc':'2.0','id':n+2,'method':'tools/call','params':param},headers)
    r.append(result)
out=root/(sys.argv[2] if len(sys.argv)>2 else 'toolsets.json')
out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(r,ensure_ascii=False)[:16000])

