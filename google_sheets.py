import gspread
import os

CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_KEY_OR_URL = "https://docs.google.com/spreadsheets/d/1WsQuyb4MoFCq195dIenaprtkTxn30SR_rEvf_a6pYOY/edit?gid=0#gid=0"

def get_google_sheets_client():
    """Autentica com as credenciais fornecidas no credentials.json"""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado. "
            "Por favor, siga as instruções no README e coloque o arquivo na pasta back-end."
        )

    try:
        client = gspread.service_account(filename=CREDENTIALS_FILE)    
        return client
    
    except Exception as e:
        raise Exception(f"Erro de autenticação com o Google. Certifique-se de que o arquivo JSON é válido: {e}")

def append_to_sheet(data_dict: dict):
    """
    Função principal que adiciona os dados recebidos pelo form ao Google Sheets.
    :param data_dict: Dicionário contendo os dados do forms (keys: perguntas, values: respostas)
    """
    client = get_google_sheets_client()

    try:
        if SPREADSHEET_KEY_OR_URL.startswith("http"):
            sheet = client.open_by_url(SPREADSHEET_KEY_OR_URL).sheet1
        else:
            sheet = client.open_by_key(SPREADSHEET_KEY_OR_URL).sheet1

    except Exception as e:
        raise Exception(
            f"Erro ao abrir a planilha. A Conta de Serviço tem acesso de Editor à planilha? "
            f"Verifique o erro: {e}"
        )

    headers = list(data_dict.keys())
    
    existing_headers = sheet.row_values(1)

    if not existing_headers:
        sheet.append_row(headers)
        existing_headers = headers

    row_to_append = []

    for header in existing_headers:
        row_to_append.append(str(data_dict.get(header, "")))

    new_headers = [h for h in headers if h not in existing_headers]
    
    if new_headers:
        existing_headers.extend(new_headers)
        sheet.update([existing_headers], 'A1') 

        for new_header in new_headers:
            row_to_append.append(str(data_dict.get(new_header, "")))

    try:
        sheet.append_row(row_to_append)

    except Exception as e:
        raise Exception(f"Erro ao inserir a linha na planilha. Verifique as configurações: {e}")

def get_all_data():
    """Busca e retorna todos os dados da planilha."""
    client = get_google_sheets_client()

    try:
        if SPREADSHEET_KEY_OR_URL.startswith("http"):
            sheet = client.open_by_url(SPREADSHEET_KEY_OR_URL).sheet1
        else:
            sheet = client.open_by_key(SPREADSHEET_KEY_OR_URL).sheet1

        records = sheet.get_all_records()

        for i, record in enumerate(records):
            record['row_index'] = i + 2
        
        return records
    
    except Exception as e:
        raise Exception(f"Erro ao ler os dados da planilha: {e}")

def update_project_status(row_index: int, status: str):
    """Atualiza a coluna 'status' de uma linha específica."""
    client = get_google_sheets_client()
    
    try:
        if SPREADSHEET_KEY_OR_URL.startswith("http"):
            sheet = client.open_by_url(SPREADSHEET_KEY_OR_URL).sheet1
        else:
            sheet = client.open_by_key(SPREADSHEET_KEY_OR_URL).sheet1
        
        headers = sheet.row_values(1)
    
        if "status" not in headers:
            status_col_index = len(headers) + 1
            sheet.update_cell(1, status_col_index, "status")
        else:
            status_col_index = headers.index("status") + 1
        
        sheet.update_cell(row_index, status_col_index, status)
    
    except Exception as e:
        raise Exception(f"Erro ao atualizar o status na planilha: {e}")
