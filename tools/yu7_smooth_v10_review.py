"""Make inspection derivatives; never edit original rendered pixels."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
code=(R/'tools/yu7_ad_v09_review_sheets.py').read_text().replace('/ArtDirection_v09','/RoofSmooth_v10')
exec(compile(code,str(R/'tools/yu7_smooth_v10_review.py'),'exec'))
