from datetime import datetime
import sys
import pandas as pd # type: ignore
from src.commom import extract_versions_and_date, normalize_keys, normalize_data, remove_brackets, try_convert_to_iso
import json
import re

def keep_as_is(value):
    # Retorna o valor literal como string (sem converter para float/NaN)
    return str(value)


def version_info_ubuntu():

    url = "https://en.wikipedia.org/wiki/Ubuntu_version_history"
    tables = pd.read_html(
        url,
        keep_default_na=False,    # não tratar strings como NaN
        na_values=[],             # nenhuma string será interpretada como missing
        flavor='bs4',             # tentar BeautifulSoup, por exemplo
        converters={
            "Standard support until": keep_as_is,
            "Extended security maintenance until": keep_as_is,
        }
    )

    # No momento, a tabela 1 é a que contém as releases do ubuntu
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        return []
        
    df = tables[0]
    # Index(['Version', 'Code name', 'Release date', 'Standard support until',
    #    'Extended security maintenance until', 'Initial kernel version'],
    #   dtype='object')
    # 
    # print(df.head())
    
    # print(df.columns)
    
    # Aplica a função à coluna e expande o resultado em novas colunas
    df[["major", "minor", "patch", "last_version_date"]] = df["Version"].apply(
        lambda x: pd.Series(extract_versions_and_date(x))
    )
    
    df = normalize_data(df, [])
    res = df.to_dict('records')
    res = normalize_keys(res)


    # verificando se a propriedade "version" do útimo registro inclui a strin ".mw-parser-output"
    # se sim, remove o item do array
    if ".mw-parser-output" in res[-1]["version"]:
        res.pop()
    ubuntus = res
    return parse_res(ubuntus)

def parse_res(raws): 
    res = []
    for raw in raws:
        r = {
            "osName": "Ubuntu " + raw["code_name"],
            "major": raw["major"],
            "majorNumber": to_int_or_zero(raw["major"]),
            "minor": raw["minor"],
            "minorNumber": to_int_or_zero(raw["minor"]),
            "patch": raw["patch"],
            "patchNumber": to_int_or_zero(raw["patch"]),
            "version": raw["version"],
            "last_version_date": raw["release_date"],
            "distributionName": raw["code_name"],
            "arch": "kernel " + raw["initial_kernel_version"],
            "vendor": "ubuntu",
            "family": "linux",
        }
        res.append(r)
        
    return res

def to_int_or_zero(value):
    try:
        return int(value)
    except:
        return 0