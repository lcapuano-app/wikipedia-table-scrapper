from datetime import datetime
import sys
import pandas as pd # type: ignore
from commom import normalize_keys, normalize_data, extract_versions_and_date
import json
import re

def version_info_apple():

    # macos = version_info_macos()
    ipados = version_info_ipados()
    ios = version_info_ios()

    return ipados

def version_info_macos():

    url = "https://en.wikipedia.org/wiki/MacOS_version_history"
    tables = pd.read_html(url)

    # No momento, a tabela 1 é a que contém as releases do macOS
    # Se isso mudar, ajuste o índice da lista
    if len(tables) < 1:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        sys.exit(1)

    df = tables[1]

    # Index(['Version', 'Release Name', 'Darwin version', 'Processor support',
    #    'Application support', 'Kernel', 'Date announced', 'Release date',
    #    'Most recent version', 'Unnamed: 9'],
    #   dtype='object')
    #
    # print(df.columns)

    # Aplica a função à coluna e expande o resultado em novas colunas
    df[["major", "minor", "patch", "last_version_date"]] = df["Most recent version"].apply(
        lambda x: pd.Series(extract_versions_and_date(x))
    )

    df = normalize_data(df, ['Date announced', 'Release date'])
    res = df.to_dict('records')
    res = normalize_keys(res)

    # verificando se a propriedade "version" do útimo registro inclui a string ".mw-parser-output"
    # se sim, remove o item do array
    if ".mw-parser-output" in res[-1]["version"]:
        res.pop()

    # Remove quaisquer propriedades que contenham "unnamed" de todos os registros
    for i in range(len(res)):
        res[i] = {key: value for key, value in res[i].items() if "unnamed" not in key}

    return res

def version_info_ipados():
    url = "https://en.wikipedia.org/wiki/IPadOS_version_history"
    tables = pd.read_html(url)
    print(tables[0].head())
    # No momento, a tabela 0 é a que contém as releases do ipados
    # Se isso mudar, ajuste o índice da lista
    if len(tables) == 0:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        sys.exit(1)

    df = tables[0]
    
    # Index(['Version', 'Initial release date', 'Latest version',
    #    'Latest release date', 'Device end-of-life'],
    #   dtype='object')
    #
    # print(df.columns)
    
    df[["major", "minor", "patch", "last_version_date"]] = df["Latest version"].apply(
        lambda x: pd.Series(extract_versions_and_date(x))
    )
    
    df = normalize_data(df, ['Initial release date', 'Latest release date'])
    res = df.to_dict('records')
    res = normalize_keys(res)
    
    # verificando se a propriedade "version" do útimo registro inclui a strin ".mw-parser-output"
    # se sim, remove o item do array
    if ".mw-parser-output" in res[-1]["version"]:
        res.pop()

    for i in range(len(res)):
        res[i]["last_version_date"] = res[i]["latest_release_date"]
    return res

def version_info_ios():

    url = "https://en.wikipedia.org/wiki/IOS_version_history"
    tables = pd.read_html(url)

    # No momento, a tabela 0 é a que contém as releases do iOS
    # Se isso mudar, ajuste o índice da lista
    if len(tables) < 1:
        print("Não foi possível encontrar as 1 tabelas necessárias", file=sys.stderr)
        sys.exit(1)

    df = tables[0]
    # MultiIndex([(             'Version',              'Version'),
    #         ('Initial release date', 'Initial release date'),
    #         (      'Latest version',       'Latest version'),
    #         ( 'Latest release date',  'Latest release date'),
    #         (  'Device end-of-life',                 'iPad'),
    #         (  'Device end-of-life',               'iPhone'),
    #         (  'Device end-of-life',           'iPod Touch'),
    #         (  'Unnamed: 7_level_0',   'Unnamed: 7_level_1')],
    #        )
    #
    # print(df.head())

    # print(df["Latest version"].head())  # Veja os primeiros valores

    # Convertendo MultiIndex para colunas simples
    df.columns = [col[1] if col[0] == col[1] else ' '.join(col).strip() for col in df.columns]
    # Version Initial release date Latest version Latest release date Device end-of-life                    Unnamed: 7_level_0
    #    Version Initial release date Latest version Latest release date               iPad  iPhone iPod Touch Unnamed: 7_level_1
    # print(df.columns)

    # Aplica a função à coluna e expande o resultado em novas colunas
    df[["major", "minor", "patch", "last_version_date"]] = df["Latest version"].apply(
        lambda x: pd.Series(extract_versions_and_date(x))
    )

    df = normalize_data(df, ['Initial release date', 'Latest release date'])
    res = df.to_dict('records')
    res = normalize_keys(res)

    # verificando se a propriedade "version" do útimo registro inclui a string "Legend: Obsolete Supported Current Beta"
    # se sim, remove o item do array
    if "Legend: Obsolete Supported Current Beta" in res[-1]["version"]:
        res.pop()    

    # Remove quaisquer propriedades que contenham "unnamed" de todos os registros
    for i in range(len(res)):
        res[i] = {key: value for key, value in res[i].items() if "unnamed" not in key}

    ios = res
    return ios


def main():
    res = version_info_ios()

    with open("apple.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)


    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
