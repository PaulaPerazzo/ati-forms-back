# Novo Back-end em FastAPI (Python)

Este é o novo serviço back-end construído em Python, substituindo o Node.js, com integração direta para o Google Planilhas (Google Sheets).

## Pré-requisitos
- Python instalado na sua máquina (recomendado Python 3.9+)
- Ter uma Service Account (Conta de Serviço) do Google configurada e acesso de editor ao Google Sheets.

## Passo a Passo: Configuração com o Google Planilhas

1. **Ativar API do Google Sheets:**
   Vá no [Google Cloud Console](https://console.cloud.google.com/), crie um projeto (se necessário) e ative as APIs:
   - Google Drive API
   - Google Sheets API

2. **Criar Credenciais (Service Account):**
   - Acesse, no seu projeto, **Credenciais > Criar Credenciais > Conta de Serviço (Service Account)**.
   - Forneça um nome para ela, e crie a conta.
   - Vá na aba "Chaves" dessa conta recém-criada e adicione uma nova chave do tipo **JSON**. 
   - Baixe esse arquivo gerado, renomeie para `credentials.json` e **coloque-o nesta pasta `back-end`** (mesmo local deste arquivo README.md e do `google_sheets.py`).

3. **Compartilhar sua Planilha:**
   - Pegue o email gerado para sua Conta de Serviço (ex: `forms-xxx@project-xyz.iam.gserviceaccount.com`).
   - Abra a sua planilha do Google Sheets que receberá os dados.
   - Clique em "Compartilhar" e adicione o email acima dando permissão de **Editor**.
   
4. **Configurar os Arquivos Locais:**
   Abra o arquivo `google_sheets.py` e altere a seguinte linha para conter o link (ou ID) da sua planilha:
   ```python
   SPREADSHEET_KEY_OR_URL = "COLOQUE_AQUI_O_LINK_DA_PLANILHA"
   ```

## Executando o Back-end

Abra seu terminal na pasta atual (`back-end`) e siga os passos abaixo para instalar as bibliotecas necessarias e rodar o servidor:

1. **Crie um ambiente virtual (Opcional, mas recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No macOS/Linux
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o servidor FastAPI:**
   ```bash
   python main.py
   ```

O servidor iniciará automaticamente na porta **3001** e estará pronto para receber as submissões (`POST /api/submit`) oriundas do seu frontend!
# ati-forms-back
