from datetime import datetime
import sys
import pandas as pd # type: ignore
from commom import normalize_keys, normalize_data

def version_info_windows():
    """
    Fetches and parses version information for various Microsoft Windows versions from Wikipedia.
    This function retrieves tables from the Wikipedia page that lists Microsoft Windows versions.
    It expects to find three tables: Windows Pro, Windows Mobile, and Windows Server. The function
    processes these tables to extract relevant version information and returns a consolidated list
    of dictionaries containing the parsed data.
    Returns:
        list: A list of dictionaries, each containing version information for a specific Windows version.
              The dictionary keys include:
              - "name": The name of the Windows version.
              - "codename": The codename of the Windows version.
              - "release_date": The release date of the Windows version.
              - "version": The version number of the Windows version.
              - "editions": The editions available for the Windows version (for Windows Mobile, this is set to "-").
              - "build_number": The build number of the Windows version.
              - "architecture": The architecture of the Windows version.
              - "end_of_support": The end of support date for the Windows version (for Windows Mobile, this is set to "-").
    Raises:
        SystemExit: If the required tables are not found on the Wikipedia page.
    """

    windowsInfos = []
    url = "https://en.wikipedia.org/wiki/List_of_Microsoft_Windows_versions"
    tables = pd.read_html(url)

    # tabela 1 = Windows Pro
    # tabela 2 = Windows Mobile
    # tabela 3 = Windows Server

    if len(tables) < 3:
        print("Não foi possível encontrar as 3 tabelas necessárias", file=sys.stderr)
        sys.exit(1)

    # Windows Pro
    infosPro = version_info_windows_pro(tables[0])

    # Windows Mobile
    infosMobile = version_info_windows_mobile(tables[1])

    # Windows Server
    infosServer = version_info_windows_server(tables[2])

    # Windows pro e server (no momento) tem o mesmo dict
    # então vamos concatena-los
    infosPro.extend(infosServer)



    # Windows Mobile não o mesmo dict, mas é bem parecido
    # então vamos fazer o parse manualmente
    for info in infosMobile:
        windowsInfos.append({
            "name": info["name"],
            "codename": info["codename"],
            "release_date": info["release_date"],
            "version": info["version_number"],
            "editions": "-",
            "build_number": info["version_number"],
            "architecture": info["architecture"],
            "end_of_support": "-"
        })

    windowsInfos.extend(infosPro)

    return windowsInfos

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
