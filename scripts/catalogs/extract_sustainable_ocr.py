import hashlib,importlib.util
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('extract_ocr',ROOT/'scripts/inventory/extract_ocr.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def run(pg):
 return m.run(('sustainable-plantbased','C:/Users/edmad/Downloads/SUSTAINABLE-Plantbased.pdf',pg,hashlib.sha256(Path('C:/Users/edmad/Downloads/SUSTAINABLE-Plantbased.pdf').read_bytes()).hexdigest()))
if __name__=='__main__':
 with ProcessPoolExecutor(3) as pool:
  for r in pool.map(run,list(range(4,23))+[26]):print(r,flush=True)
