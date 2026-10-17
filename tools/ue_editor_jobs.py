"""Temporary, local-only UE editor job runner. No runtime or network dependency.

Start from the UE console with: py "C:/github2/vehicle_visualization/tools/ue_editor_jobs.py"
Jobs are explicit Python files inside this workspace, supplied through request.json.
Stops after 90 minutes or a request with stop=true. Each job gets a result file.
"""
import json
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path('C:/github2/vehicle_visualization').resolve()
QUEUE = ROOT / 'art/YU7_UNREAL/reports/ue_jobs'
QUEUE.mkdir(parents=True, exist_ok=True)
START = time.monotonic()
LAST = ''
TICK = 0.0
BUSY = False


def tick(delta):
    global LAST, TICK, BUSY
    if BUSY:
        return
    if time.monotonic() - START > 5400:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        return
    if time.monotonic() - TICK < 1.0:
        return
    TICK = time.monotonic()
    request = QUEUE / 'request.json'
    if not request.exists():
        return
    try:
        job = json.loads(request.read_text(encoding='utf-8-sig'))
    except (ValueError, OSError):
        return
    if job['id'] == LAST:
        return
    LAST = job['id']
    if job.get('stop'):
        unreal.unregister_slate_post_tick_callback(HANDLE)
        return
    result = {'id': LAST, 'started': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    BUSY = True
    result_path = QUEUE / (LAST + '.json')
    result_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    try:
        script = (ROOT / job['script']).resolve()
        if not script.is_relative_to(ROOT):
            raise ValueError('Job must be in the project workspace')
        scope = {'__name__': '__main__', '__file__': str(script)}
        exec(compile(script.read_text(encoding='utf-8-sig'), str(script), 'exec'), scope)
        result['status'] = 'success'
        result['result'] = scope.get('RESULT')
    except Exception:
        result['status'] = 'error'
        result['error'] = traceback.format_exc()
        unreal.log_error(result['error'])
    result['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    result_path.write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')
    BUSY = False
    unreal.log('YU7 editor job finished: ' + LAST + ' / ' + result['status'])


HANDLE = unreal.register_slate_post_tick_callback(tick)
unreal.log('YU7 local editor job runner ready; no network listener.')
