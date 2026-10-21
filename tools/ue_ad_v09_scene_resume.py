"""Resume only the unfinished r04 road/environment/light stage; emission already saved."""
from pathlib import Path
src=Path('C:/github2/vehicle_visualization/tools/ue_ad_v09_scene.py').read_text()
src=src[:src.index('# Dim only')]+src[src.index('# Soft elongated'):]
exec(compile(src,'ad_scene_resume','exec'))
