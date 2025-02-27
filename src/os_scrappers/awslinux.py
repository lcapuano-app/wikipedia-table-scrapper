import sys
import pandas as pd # type: ignore
import re

from src.commom import normalize_data, normalize_keys, try_convert_to_iso # type: ignore

def get_versions_from_change_2(name, item):
    change = item["change"]
    desc = item["description"]
    res = {
        "name": name,
        "version": "2",
        "major": "-",
        "minor": "-",
        "patch": "-",
        "date": "-",
    }
    
    date = try_convert_to_iso(item["date"])
    res["date"] = date

 	# na change ou na release
    # Amazon Linux 2 2.0.20230119.1 includes updated packages for this release.
    versions = change.split("Amazon Linux 2 2.0.")
    if len(versions) < 2:
        versions = desc.split("Amazon Linux 2 2.0.")
        
    if len(versions) < 2:
        return res
    
    res["major"] = "2.0"
    vr = versions[1].split(".")
    if len(vr) > 1:
        res["minor"] = vr[0]
        res["patch"] = vr[1].split(" ")[0]
    
    return res

def get_versions_from_change_2023(name, item):
    change = item["change"]
    res = {
        "name": name,
        "version": "",
        "major": "",
        "minor": "",
        "patch": "",
        "date": "",
    }
    
    date = try_convert_to_iso(item["date"])
    res["date"] = date

    # AL2023 2023.3.20240122 released
    change = change.split(" ")
    
    if len(change) < 2:
        print(f"Erro ao processar a mudança {change}", file=sys.stderr)
        return res
        
    version = change[0]
    res["version"] = version
    
    # Expressão regular para extrair major, minor e patch (ou major e minor)
    version_pattern = re.compile(r'(\d+)\.(\d+)(?:\.(\d+))?')
    match = version_pattern.search(change[1])
    if match:
        major, minor, patch = match.groups()
        res["major"] = major
        res["minor"] = minor
        res["patch"] = patch
    
    return res

def version_info_awslinux():
    al2 = version_info_awslinux2()
    al2023 = version_info_awslinux2023()
    # res = {
    #     "al2": al2,
    #     "al2023": al2023,
    # }
    res =  []
    res.extend(al2)
    res.extend(al2023)
    return parse_res(res)

def version_info_awslinux2023():
    url = "https://docs.aws.amazon.com/linux/al2023/release-notes/document-history.html"
    tables = pd.read_html(url)
    
    # No momento, a tabela 0 é a que contém as releases do al2023
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        return []
        
    df = tables[0]
    
    df = normalize_data(df, [])
    res = df.to_dict('records')
    res = normalize_keys(res)

    final_res = []
    for item in res:
        fr = get_versions_from_change_2023("amazon 2023", item)
        final_res.append(fr)
   
    return final_res

def version_info_awslinux2():
    url = "https://docs.aws.amazon.com/AL2/latest/relnotes/relnotes-al2.html"
    tables = pd.read_html(url)
    
    # No momento, a tabela 0 é a que contém as releases do al2
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        return []
        
    df = tables[0]
    
    df = normalize_data(df, [])
    res = df.to_dict('records')
    res = normalize_keys(res)

    final_res = []
    for item in res:
        fr = get_versions_from_change_2("amazon2", item)
        final_res.append(fr)
   
    return final_res


def parse_res(raws): 
    res = []
    for raw in raws:
        r = {
            "osName": raw["name"],
            "major": raw["major"],
            "majorNumber": to_int_or_zero(raw["major"]),
            "minor": raw["minor"],
            "minorNumber": to_int_or_zero(raw["minor"]),
            "patch": raw["patch"],
            "patchNumber": to_int_or_zero(raw["patch"]),
            "version": raw["version"],
            "last_version_date": raw["date"],
            "distributionName": raw["name"],
            "arch": "arm64, x86_64, amd64",
            "vendor": "amazon",
            "family": "linux",
        }
        res.append(r)
        
    return res

def to_int_or_zero(value):
    try:
        return int(value)
    except:
        return 0