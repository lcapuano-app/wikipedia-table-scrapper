from datetime import datetime
import sys
import pandas as pd # type: ignore
from commom import normalize_keys, normalize_data, extract_versions_and_date
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

def version_info_android():
    url = "https://en.wikipedia.org/wiki/Android_version_history"
    tables = pd.read_html(url)

    # No momento, a tabela 0 é a que contém as releases do macOS
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        sys.exit(1)

    df = tables[0]

    # Index(['Name', 'Internal codename[11]', 'Version number(s)', 'API level',
    #    'Release date', 'Latest security patch date[16]',
    #    'Latest Google Play Services version[17] (release date)'],
    #   dtype='object')
    # print(df.columns)


    df[["major", "minor", "patch", "last_version_date"]] = df["Version number(s)"].apply(
        lambda x: pd.Series(preprocess_version(x))
    )

    df = normalize_data(df, [
        'Release date', 
        'Latest Google Play Services version[17] (release date)',
    ])
    res = df.to_dict('records')
    res = normalize_keys(res)

    # # verificando se a propriedade "version_number(s)" do útimo registro inclui a string "Legend:Old version, not maintainedOld version, still maintainedLatest versionLatest preview version"
    # # se sim, remove o item do array
    if "Legend:Old version, not maintainedOld version, still maintainedLatest versionLatest preview version" in res[-1]["version_number(s)"]:
        res.pop()

    return res

def main():
    res = version_info_android()

    with open("android.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)


    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
