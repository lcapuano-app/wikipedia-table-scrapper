from datetime import datetime
import sys
import pandas as pd # type: ignore
from src.commom import normalize_dataframe_columns, normalize_keys, normalize_data, extract_versions_and_date
import json
import re

def preprocess_version(version):
    # Divide a versão por " – " caso tenha intervalos de versões
    version_parts = version.split(" – ")[-1].split(".")
    
    # Se a versão tem apenas 1 número, definimos os outros como 0
    if len(version_parts) == 1:
        major = version_parts[0]
        minor = "0"
        patch = "0"
    # Se a versão tem 2 números, definimos como major e minor
    elif len(version_parts) == 2:
        major = version_parts[0]
        minor = version_parts[1]
        patch = "0"
    # Se a versão tem 3 números, usamos major, minor e patch
    elif len(version_parts) == 3:
        major, minor, patch = version_parts
    else:
        major = minor = patch = "-"
    
    # Como não temos a data na versão, podemos deixar o campo "last_version_date" como "-"
    last_version_date = "-"
    
    return major, minor, patch, last_version_date

def keep_as_is(value):
    # Retorna o valor literal como string (sem converter para float/NaN)
    return str(value)

def version_info_android():
    url = "https://en.wikipedia.org/wiki/Android_version_history"
    tables = pd.read_html(
        url,
        keep_default_na=False,    # não tratar strings como NaN
        na_values=[],             # nenhuma string será interpretada como missing
        flavor='bs4',             # tentar BeautifulSoup, por exemplo
        converters={"Version number(s)": keep_as_is}
    )
    #tables = pd.read_html(url, converters=defaultdict(lambda: str), flavor='bs4')
    # No momento, a tabela 0 é a que contém as releases do macOS
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        return []

    df = tables[0]

    # Index(['Name', 'Internal codename[11]', 'Version number(s)', 'API level',
    #    'Release date', 'Latest security patch date[16]',
    #    'Latest Google Play Services version[17] (release date)'],
    #   dtype='object')
    # print(df.columns)
    
    # renames data frame columns to its current name, to lowercase and snake case
    df = normalize_dataframe_columns(df)
  
    df[["major", "minor", "patch", "last_version_date"]] = df["version_number"].apply(
        lambda x: pd.Series(preprocess_version(x))
    )
    
    df = normalize_data(df, [
        'release_date', 
        'latest_google_play_services_version',
        'latest_security_patch_date'
    ])
    res = df.to_dict('records')
    res = normalize_keys(res)

    # # verificando se a propriedade "version_number(s)" do útimo registro inclui a string "Legend:Old version, not maintainedOld version, still maintainedLatest versionLatest preview version"
    # # se sim, remove o item do array
    if "Legend:Old version, not maintainedOld version, still maintainedLatest versionLatest preview version" in res[-1]["version_number"]:
        res.pop()

    return parse_res(res)

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
            "version": raw["version_number"],
            "last_version_date": raw["latest_security_patch_date"],
            "distributionName": raw["internal_codename"],
            "arch": "arm",
            "vendor": "google",
            "family": "android",
        }
        res.append(r)
        
    return res

def to_int_or_zero(value):
    try:
        return int(value)
    except:
        return 0