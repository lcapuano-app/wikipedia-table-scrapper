from datetime import datetime
import re
import pandas as pd # type: ignore

def normalize_dataframe_columns(df):
    """
    Normalize the column names of a pandas DataFrame.
    This function renames the columns of the given DataFrame by:
    - Removing any brackets from the column names.
    - Stripping leading and trailing whitespace.
    - Converting all characters to lowercase.
    - Replacing spaces with underscores.
    Args:
        df (pandas.DataFrame): The DataFrame whose columns need to be normalized.
    Returns:
        pandas.DataFrame: A DataFrame with normalized column names.
    """
  
    df = df.rename(columns=lambda x:
        remove_parentheses( 
            remove_brackets(x))
                .strip()
                .lower()
                .replace(" ", "_"))
    
    return df

def normalize_keys(data):
    """
        Normalize the keys of dictionaries in a list.
        This function takes a list of dictionaries and normalizes the keys of each dictionary
        by converting them to lowercase and replacing spaces with underscores.
        Args:
            data (list of dict): A list of dictionaries whose keys need to be normalized.
        Returns:
            list of dict: A list of dictionaries with normalized keys.
    """
    for i in range(len(data)):
        data[i] = {key.lower()
                   .replace(" ", "_")
                   .replace("(", "")
                   .replace(")", ""): value for key, value in data[i].items()}
        
    return data

def normalize_data(df, date_columns):
    """
    Normalize the data in the given DataFrame.
    This function performs the following operations:
    1. Removes brackets from all columns.
    2. Strips leading and trailing whitespace from string values.
    3. Converts specified date columns to ISO format.
    Args:
        df (pandas.DataFrame): The DataFrame to normalize.
        date_columns (list of str): List of column names that contain date values to be converted to ISO format.
    Returns:
        pandas.DataFrame: The normalized DataFrame.
    """
    # Aplica a função para remover colchetes em todas as colunas
    df = df.applymap(remove_brackets)
    
    # Remove espaços em branco no início e no final das strings
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    
    # Aplica a função de conversão nas colunas de datas
    for col in date_columns:
        df[col] = df[col].apply(try_convert_to_iso)
      
    return df


def try_convert_to_iso(date_str):
    """
    Tenta converter 'date_str' nos formatos:
      - '%B %d, %Y' (ex: 'February 10, 2025')
      - '%B %Y'     (ex: 'February 2023')
    Se não conseguir, retorna '-'.
    Se houver algo em parênteses, tenta parsear ali também.
    """
    if not isinstance(date_str, str):
        return "-"

    date_str = date_str.strip()

    def try_formats(s):
        # Tenta '%B %d, %Y' e '%B %Y'
        formats = ["%B %d, %Y", "%B %Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return None  # não conseguiu

    # 1) Tenta a string como está
    iso = try_formats(date_str)
    if iso is not None:
        return iso

    # 2) Se falhou, mas há algo entre parênteses, tenta esse substring
    match = re.search(r"\(([^)]+)\)", date_str)
    if match:
        inside = match.group(1).strip()
        iso2 = try_formats(inside)
        if iso2 is not None:
            return iso2

    # 3) Se nada funcionou, retorna "-"
    return "-"

# Função para remover texto entre colchetes
def remove_brackets(text):
    """
    Remove brackets and their contents from a string.
    Args:
        text (str or any): The input text from which brackets and their contents should be removed.
                           If the input is NaN, it returns "-".
                           If the input is not a string, it returns the original value.
    Returns:
        str or any: The text with brackets and their contents removed if the input is a string.
                    If the input is NaN, it returns "-".
                    If the input is not a string, it returns the original value.
    """
    if pd.isna(text):  # Verifica se o valor é NaN | pd.isna() é equivalente a pd.isnull()
        return "-"
    if isinstance(text, str):  # Verifica se o valor é uma string
        return re.sub(r'\[.*?\]', '', text)
  
    return text  # Retorna o valor original se não for uma string

def remove_parentheses(text):
    """
    Remove parentheses and their contents from a string.
    Args:
        text (str or any): The input text from which parentheses and their contents should be removed.
                           If the input is NaN, it returns "-".
                           If the input is not a string, it returns the original value.
    Returns:
        str or any: The text with parentheses and their contents removed if the input is a string.
                    If the input is NaN, it returns "-".
                    If the input is not a string, it returns the original value.
    """
    if pd.isna(text):  # Verifica se o valor é NaN | pd.isna() é equivalente a pd.isnull()
        return "-"
    if isinstance(text, str):  # Verifica se o valor é uma string
        return re.sub(r'\(.*?\)', '', text)
  
    return text  # Retorna o valor original se não for uma string

# Função para extrair major, minor, patch e a data da última versão
def extract_versions_and_date(version_string):
    # Verifica se a string é válida
    if not version_string or version_string == "-":
        return {"major": "-", "minor": "-", "patch": "-", "last_version_date": "-"}
    
    # Expressão regular para extrair major, minor e patch (ou major e minor)
    version_pattern = re.compile(r'(\d+)\.(\d+)(?:\.(\d+))?')
    match = version_pattern.search(version_string)
    
    # Extrai a última substring entre parênteses
    date_pattern = re.compile(r'\(([^)]+)\)')
    date_matches = date_pattern.findall(version_string)
    last_version_date = date_matches[-1] if date_matches else "-"
    
    # Converte a data para o formato ISO
    last_version_date_iso = try_convert_to_iso(last_version_date)
    
    if match:
        major, minor, patch = match.groups()
        # Se o patch não existir, define como "-"
        patch = patch if patch else "-"
        return {
            "major": major,
            "minor": minor,
            "patch": patch,
            "last_version_date": last_version_date_iso
        }
    else:
        return {"major": "-", "minor": "-", "patch": "-", "last_version_date": last_version_date_iso}