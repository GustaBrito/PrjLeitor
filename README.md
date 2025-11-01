# 🤖 LEITOR COM INTERAÇÃO COM GEMINI

Um aplicativo web em Python (Flask) que utiliza o modelo Gemini do Google AI para realizar diversas operações de processamento e análise em arquivos de imagem e texto, ideal para fluxos de trabalho que envolvem OCR, análise de documentos e tradução.

## ✨ Funcionalidades Principais

O projeto permite o upload de arquivos e oferece as seguintes operações avançadas, todas potencializadas pelo Google Gemini:

* **Análise de Conteúdo (Text Analysis):**
    * **Resumo (Summary):** Gera um resumo conciso do conteúdo.
    * **Extração Completa (Full Extraction):** Extrai texto e dados brutos de forma completa e detalhada, ideal para documentos grandes.
    * **Higienização (Sanitize):** Processa o texto para limpeza, normalização e formatação estruturada.
* **Tradução (Translation):** Traduz o conteúdo integral dos arquivos para um idioma de destino especificado.
* **Extração de Dados Estruturados (Extract):** Processa imagens e documentos para extrair tabelas, dados em formato JSON, e possivelmente gráficos.
* **Checagem de IA (AI Check):** Verifica e analisa o conteúdo para detectar padrões e artefatos comuns de geração por Inteligência Artificial.
* **Operações Matemáticas (Math Operation):** Analisa e resolve problemas e expressões matemáticas complexas presentes nos arquivos.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

1.  **Python:** Versão 3.x instalada.
2.  **Chave de API do Google Gemini:** Obtenha sua chave de API no [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key).

### 1. Configuração do Ambiente

1.  **Clone o repositório:**
    ```bash
    git clone [LINK_DO_SEU_REPOSITORIO]
    cd [pasta_do_projeto]
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    # Dependências principais: Flask, google-genai, markdown, pillow
    ```

### 2. Configuração da Chave de API

O projeto acessa a chave de API do Gemini através de um arquivo de constantes (`src/utils/constantes.py`). Recomenda-se definir a chave como uma **variável de ambiente** para maior segurança.

```bash
# Exemplo para Linux/macOS
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
# Exemplo para Windows (CMD)
set GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

# 3. Inicialize o Aplicativo

Execute o arquivo principal para iniciar o servidor Flask:

python app.py

# 📂 Estrutura do Projeto

A estrutura sugere uma organização modular para as funcionalidades do Gemini e do Flask:

```bash
gemini-web-processor/
├── app.py                  # Ponto de entrada e rotas principais do Flask
├── requirements.txt        # Lista de dependências Python
├── templates/
│   ├── upload.html         # Formulário de upload de arquivos e seleção de função
│   └── result.html         # Página para exibição dos resultados processados
├── static/                 # Arquivos CSS, JavaScript e Imagens estáticas
├── src/
│   ├── modules/
│   │   ├── funcoes.py      # Contém classes/funções para manipulação de Arquivo e interação com Gemini
│   ├── utils/
│   │   ├── constantes.py   # Configurações de chaves, caminhos e modelo Gemini
│   │   └── prompts.py      # Prompts (instruções) enviadas ao modelo Gemini
└── temp/                   # Pasta para uploads temporários e pickles de sessão (Gerada em tempo de execução)
```

🛠️ Tecnologias Utilizadas
Python

Flask: Framework web para servir a aplicação.

Google GenAI SDK: Para comunicação com a API do Google Gemini.

Markdown: Para formatação rica dos resultados na página web.

pickle, json, os, sys: Módulos utilitários padrão do Python para manipulação de arquivos e dados de sessão.
