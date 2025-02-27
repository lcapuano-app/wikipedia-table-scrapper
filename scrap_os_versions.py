from datetime import datetime, timezone
import os

import sys
import json

from src.os_scrappers.android import version_info_android
from src.os_scrappers.apple import version_info_apple
from src.os_scrappers.linux import version_info_linux
from src.os_scrappers.windows import version_info_windows

def utc_timestamp_iso():
    # Gera algo como '2025-02-27T15:28:31.378+00:00'
    dt = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    # Substitui '+00:00' por 'Z'
    return dt.replace('+00:00', 'Z')


def just_save(fname: str, data: dict):
    # timestamp as a DateISOString
    timestamp = utc_timestamp_iso()
    
    out = "temp"
    # searchs --out flag value
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    elif "-o" in sys.argv:
        out = sys.argv[sys.argv.index("-o") + 1]
    
    fpath = os.path.join(out, f"{fname}.json")
  
    try:
        # if the output directory does not exist, create it
        if not os.path.exists(out): 
            os.makedirs(out)
        
        for d in data:
            d["timestamp"] = timestamp
            
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
       
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

def get_n_save(fname: str, version_info_fn: callable):
    try:
        res = version_info_fn()
        just_save(fname, res)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
        
def one_by_one():
     # Android
    get_n_save("android", version_info_android)
    
    # Apple
    get_n_save("apple", version_info_apple)
    
    # Linux
    get_n_save("linux", version_info_linux)
    
    # Windows
    get_n_save("windows", version_info_windows)
    
def all_in_one():
    androids = version_info_android()
    apples = version_info_apple()
    linuxes = version_info_linux()
    windowses = version_info_windows()
    data = androids + apples + linuxes + windowses
    return just_save("all_os", data)
    
    
def main():
    try:
        # one_by_one()
        all_in_one()
        sys.exit(0)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
    
   

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
