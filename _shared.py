from datetime import datetime
import re
import pandas as pd # type: ignore

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
        data[i] = {key.lower().replace(" ", "_"): value for key, value in data[i].items()}
        
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

# Função para tentar converter uma string para data ISO ou retornar "-"
def try_convert_to_iso(date_str):
    """
    Converts a date string in the format '%B %d, %Y' to ISO format '%Y-%m-%d'.

    Args:
        date_str (str): The date string to be converted.

    Returns:
        str: The date in ISO format if conversion is successful, otherwise "-".
    """
    if not isinstance(date_str, str):  # Verifica se o valor é uma string
        return "-"  # Retorna "-" se não for uma string
    try:
        # Tenta converter a string para datetime
        date = datetime.strptime(date_str, '%B %d, %Y')
        # Se conseguir, retorna no formato ISO
        return date.strftime('%Y-%m-%d')
    except ValueError:
        # Se não conseguir, retorna "-"
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

