# Back-end em FastAPI (Python) com MongoDB

Este é o serviço back-end construído em Python (FastAPI), que processa e salva os dados no MongoDB.

## Pré-requisitos
- Python instalado na sua máquina (recomendado Python 3.9+)
- MongoDB rodando localmente (seja instalado diretamente ou via Docker)

## Passo a Passo: Configuração com MongoDB

1. **Configurar as Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz desta pasta `back-end` e adicione as configurações de conexão com o banco de dados. Exemplo:
   ```env
   MONGO_URI=<SUA_URI>
   MONGO_DB_NAME=<NOME_DB>
   ```

2. **Iniciando o MongoDB via Docker (Opcional):**
   Se preferir usar o Docker para rodar o MongoDB localmente:
   ```bash
   docker run --name myDeployment -p 27017:27017 -d mongodb/mongodb-community-server:latest
   ```

## Executando o Back-end

Abra seu terminal na pasta atual (`back-end`) e siga os passos abaixo para instalar as bibliotecas necessárias e rodar o servidor:

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
