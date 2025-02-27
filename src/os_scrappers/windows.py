from datetime import datetime
import sys
import pandas as pd # type: ignore
import re

from src.commom import normalize_data, normalize_keys # type: ignore


def version_info_windows():
 
    url = "https://en.wikipedia.org/wiki/List_of_Microsoft_Windows_versions"
    tables = pd.read_html(url)

    # tabela 1 = Windows Pro
    # tabela 2 = Windows Mobile
    # tabela 3 = Windows Server

    if len(tables) < 3:
        print("Não foi possível encontrar as 3 tabelas necessárias", file=sys.stderr)
        return []

    # Windows Pro
    infosPro = version_info_windows_pro(tables[0])

    # Windows Mobile
    infosMobile = version_info_windows_mobile(tables[1])

    # Windows Server
    infosServer = version_info_windows_server(tables[2])



    # Windows Mobile não o mesmo dict, mas é bem parecido
    # então vamos fazer o parse manualmente
    normMobile = []
    for info in infosMobile:
        normMobile.append({
            "name": info["name"],
            "codename": info["codename"],
            "release_date": info["release_date"],
            "version": info["version_number"],
            "editions": "-",
            "build_number": info["version_number"],
            "architecture": info["architecture"],
            "end_of_support": "-"
        })

    winMobRes = parse_res_mobile(normMobile)
    winProRes = parse_res_pro(infosPro)
    winServerRes = parse_res_server(infosServer)
    res = winMobRes + winProRes  + winServerRes
    
    return res

def version_info_windows_pro(df):
    """
    Processes a DataFrame containing Windows Pro version information and returns a list of dictionaries with normalized data.
    Args:
        df (pandas.DataFrame): A DataFrame with the following columns:
            - 'Name'
            - 'Codename'
            - 'Release date'
            - 'Version'
            - 'Editions'
            - 'Build number'
            - 'Architecture'
            - 'End of support'
    Returns:
        list: A list of dictionaries where each dictionary represents a row from the DataFrame with normalized keys and date fields.
    """
    # windows Pro (not server) headers = Index([
    # 'Name', 'Codename', 'Release date', 'Version',
    # 'Editions','Build number', 'Architecture', 'End of support'
    # ], dtype='object')

    df = normalize_data(df, ['Release date', 'End of support'])
    res = df.to_dict('records')
    res = normalize_keys(res)

    return res

def version_info_windows_mobile(df):
    """
    Processes a DataFrame containing Windows Mobile version information.
    This function normalizes the 'Release date' column in the provided DataFrame,
    converts the DataFrame to a list of dictionaries, and normalizes the keys
    of these dictionaries.
    Args:
        df (pandas.DataFrame): A DataFrame with the following columns:
            - 'Name'
            - 'Codename'
            - 'Architecture'
            - 'Release date'
            - 'Version Number'
    Returns:
        list: A list of dictionaries containing the normalized version information.
    """
    # windows Mobile (not server) headers = Index([
    # 'Name', 'Codename', 'Architecture', 'Release date','Version Number'
    # ], dtype='object')
    df = normalize_data(df, ['Release date'])
    res = df.to_dict('records')
    res = normalize_keys(res)

    return res

def version_info_windows_server(df):
    """
    Processes a DataFrame containing Windows Server version information.
    This function normalizes the 'Release date' and 'End of support' columns in the DataFrame,
    converts the DataFrame to a list of dictionaries, and normalizes the keys of these dictionaries.
    Args:
        df (pandas.DataFrame): A DataFrame with Windows Server version information. Expected columns are:
            - 'Name'
            - 'Codename'
            - 'Release date'
            - 'Version'
            - 'Editions'
            - 'Build number'
            - 'Architecture'
            - 'End of support'
    Returns:
        list: A list of dictionaries where each dictionary represents a row from the DataFrame with normalized keys.
    """
    # windows Server headers = Index([
    # 'Name', 'Codename', 'Release date', 'Version',
    # 'Editions','Build number', 'Architecture', 'End of support'
    # ], dtype='object')

    df = normalize_data(df, ['Release date', 'End of support'])
    res = df.to_dict('records')
    res = normalize_keys(res)

    return res

def parse_res_mobile(raws): 
    def find_build(ver, n):
      
        # "version": "CE 6.0",
        mj = "-"
        mn = "-"
        pt = "-"
        if "Windows 10 Mobile" in n:
            mj = "10"
            mn = ver
            return mj, mn, pt
        
        parts = ver.split(" ")
        if len(parts) < 2:
            return mj, mn, pt
        
        mj = parts[0]
        
        mnParts = parts[1].split(".")
        
        if len(mnParts) < 2:
            mn = parts[1]
            return mj, mn, pt
        
        mn = mnParts[0]
        pt = mnParts[1]
        return mj, mn, pt
       
    res = []
    for raw in raws:
        
        major, minor, patch = find_build(raw["version"], raw["name"])
        
        r = {
            "osName": raw["name"],
            "major": major,
            "majorNumber": to_int_or_zero(major),
            "minor": minor,
            "minorNumber": to_int_or_zero(minor),
            "patch": patch,
            "patchNumber": to_int_or_zero(patch),
            "version": raw["version"],
            "last_version_date": raw["release_date"],
            "distributionName": raw["codename"],
            "arch": raw["architecture"],
            "vendor": "microsoft",
            "family": major,
        }
        res.append(r)
        
    return res


def parse_res_pro(raws): 
    def find_build(ver, bd):
        mj = ver
        mn = bd
        pt = "-"
        
        if "." in ver:
            parts = ver.split(".")
            
            if len(parts) < 2:
                return mj, mn, pt
            
            mj = parts[0]
            mn = parts[1].split(" ")[0]
            pt = bd
            
            majorParts = parts[0].split(" ")
            if len(majorParts) < 2:
                return mj, mn, pt
            
            mj = majorParts[1]
            return mj, mn, pt
        
        
        return mj, mn, pt
       
    res = []
    for raw in raws:
        name = raw["name"].split("version")[0]
        name = name.replace(",", "").strip()
        major, minor, patch = find_build(raw["version"], raw["build_number"])
        
        r = {
            "osName": name,
            "major": major,
            "majorNumber": to_int_or_zero(major),
            "minor": minor,
            "minorNumber": to_int_or_zero(minor),
            "patch": patch,
            "patchNumber": to_int_or_zero(patch),
            "version": raw["version"],
            "last_version_date": raw["release_date"],
            "distributionName": raw["codename"],
            "arch": raw["architecture"],
            "vendor": "microsoft",
            "family": raw["version"],
        }
        res.append(r)
        
    return res

    
def parse_res_server(raws): 
    
    def find_build(ver, bd):
        mj = ver
        mn = bd
        pt = "-"

        if "." in ver:
            parts = ver.split(".")
            
            if len(parts) < 2:
                return mj, mn, pt
            
            mj = parts[0]
            mn = parts[1].split(" ")[0]
            pt = bd
            
            majorParts = parts[0].split(" ")
            if len(majorParts) < 2:
                return mj, mn, pt
            
            mj = majorParts[1]
            return mj, mn, pt


        return mj, mn, pt
       
    res = []
    for raw in raws:
        name = raw["name"].split("version")[0]
        name = name.replace(",", "").strip()
        major, minor, patch = find_build(
            raw["version_number"], raw["build_number"])
        
        r = {
            "osName": name,
            "major": major,
            "majorNumber": to_int_or_zero(major),
            "minor": minor,
            "minorNumber": to_int_or_zero(minor),
            "patch": patch,
            "patchNumber": to_int_or_zero(patch),
            "version": raw["version_number"],
            "last_version_date": raw["release_date"],
            "distributionName": raw["codename"],
            "arch": raw["architecture"],
            "vendor": "microsoft",
            "family": raw["version_number"],
        }
        res.append(r)
        
    return res

def version_to_int(version: str) -> str:
    """
    Localiza cada letra (A-Za-z) na string 'version'
    e substitui pela soma dos códigos ASCII.
    
    Exemplo:
      "19H1" -> "19721" ('H' = 72)
    """
    # Substitui cada letra por seu valor ASCII (str(ord(...)))
    return re.sub(r"[A-Za-z]", lambda match: str(ord(match.group(0))), version)

def to_int_or_zero(value):
    # print("chegamos aqui?", value)
    try:
        value = version_to_int(value)
        return int(value)
    except:
        return 0