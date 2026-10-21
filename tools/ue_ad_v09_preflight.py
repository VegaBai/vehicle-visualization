from pathlib import Path
R=Path('C:/github2/vehicle_visualization');results={}
for name in ['ue_ad_v09_camera_export','ue_ad_v09_audit']:
    scope={'__name__':'__main__'};exec(compile((R/'tools'/f'{name}.py').read_text(),name,'exec'),scope);results[name]=scope['RESULT']
RESULT=results
