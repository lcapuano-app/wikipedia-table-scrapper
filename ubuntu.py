from datetime import datetime
import sys
import pandas as pd # type: ignore
from commom import extract_versions_and_date, normalize_keys, normalize_data, try_convert_to_iso
import json
import re


def version_info_ubuntu():

    url = "https://en.wikipedia.org/wiki/Ubuntu_version_history"
    tables = pd.read_html(url)
    
    # No momento, a tabela 1 é a que contém as releases do ubuntu
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        sys.exit(1)
        
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
    
    df = normalize_data(df, [
        'Standard support until', 
        'Release date', 
        'Extended security maintenance until',
    ])
    res = df.to_dict('records')
    res = normalize_keys(res)


    # verificando se a propriedade "version" do útimo registro inclui a strin ".mw-parser-output"
    # se sim, remove o item do array
    if ".mw-parser-output" in res[-1]["version"]:
        res.pop()
    ubuntus = res
    return ubuntus

def main():
    res = version_info_ubuntu()

    with open("ubuntu.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)


    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
