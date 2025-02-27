from datetime import datetime
import sys
import pandas as pd # type: ignore
from src.commom import normalize_keys, normalize_data, extract_versions_and_date
import json
import re

def version_info_centOS():
    url = "https://en.wikipedia.org/wiki/CentOS#Latest_version_information"
    tables = pd.read_html(url)

    # No momento, a tabela 4 é a que contém as last releases do centOS
    # Se isso mudar, ajuste o índice da lista
    if len(tables) < 4:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        return []

    df = tables[4]

    # Index(['CentOS version', 'Architectures', 'RHEL base', 'Kernel',
    #    'CentOS release date', 'RHEL release date', 'Delay (days)'],
    #   dtype='object')
    # print(df.columns)

    # Remove referências [146], [147], etc. das datas
    df["CentOS release date"] = df["CentOS release date"].astype(str).apply(lambda x: re.sub(r'\[\d+\]', '', x).strip())
    df["RHEL release date"] = df["RHEL release date"].astype(str).apply(lambda x: re.sub(r'\[\d+\]', '', x).strip())

    # Ajuste para converter "x.x-xxxx" em "x.x.x (xxxx)"
    df["CentOS version"] = df["CentOS version"].astype(str).apply(lambda v: v.replace("-", ".") + f" ({v.split('-')[-1]})" if "-" in v else v)

    # Aplica a função à coluna e expande o resultado em novas colunas
    df[["major", "minor", "patch", "last_version_date"]] = df["CentOS version"].apply(
        lambda x: pd.Series(extract_versions_and_date(x))
    )

    res = df.to_dict('records')
    res = normalize_keys(res)

    return parse_res(res)

def parse_res(raws): 
    res = []
    for raw in raws:
        r = {
            "osName": "centOS",
            "major": raw["major"],
            "majorNumber": to_int_or_zero(raw["major"]),
            "minor": raw["minor"],
            "minorNumber": to_int_or_zero(raw["minor"]),
            "patch": raw["patch"],
            "patchNumber": to_int_or_zero(raw["patch"]),
            "version": raw["centos_version"],
            "last_version_date": raw["centos_release_date"],
            "distributionName": "centOS",
            "arch": raw["architectures"],
            "vendor": "centos",
            "family": "linux",
        }
        res.append(r)
        
    return res

def to_int_or_zero(value):
    try:
        return int(value)
    except:
        return 0