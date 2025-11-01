
==========================================================================================
==                                  PrjLeitor                                           ==
==========================================================================================


Estrutura do Projeto
====================
>__init__.py                 # Arquivos para inicialização dos módulos

Leitor/                           # Pasta raiz do projeto
│
├── src/                            # Código-fonte principal
│   │
│   ├── modules/                    # Módulos de funcionalidades
│   │   └── funcoes.py              # Funções principais (Arquivo, Validação, etc.)
│   │
│   ├── temp/                       # Dados temporários
│   │   ├── uploads/                # Arquivos enviados pelo usuário
│   │   ├── temp_data/              # Dados processados temporários
│   │   └── temp_images/            # Imagens processadas temporárias
│   │
│   └── utils/ 
│       ├── icons/                  # Ícones do aplicativo
│       │   └── Leitor.ico          # Ícone principal
│       │
│       ├── static/                 # Arquivos estáticos (CSS, JS, imagens)
│       │   ├── css/                # Estilos gráficos do Template
|       |   |    └── logo.svg
|       |   |    └── styles.css
|       |   |    └── tela.png
│       │   ├── js/                 # Lógica do Template
|       |   |    └── export.js
|       |   |    └── upload.js
│       │   └── Leitor.ico         # Ícone principal para navegador (Appweb)
│       │                 
│       ├── templates/              # Templates HTML (Flask)
│       │   ├── result.html         # Template secundário (resultado final)
│       │   └── upload.html         # Template principal (tela inicial)
│       │
│       │
│       ├── constantes.py           # Constantes do projeto
│       ├── prompts.py              # Prompts do projeto
│       └── requirements.txt        # Dependências do projeto
│
├── app.py                          # Aplicação Flask (server)
├── Leitor.py                          # Interface gráfica PyQt6 (gui)
├── README.md                       # Documentação



import os

#==========================================================
# Mapeamento de Pastas
#==========================================================

# Caminho para o diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para a pasta 'apoio'
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Caminho para a pasta 'utils'
UTILS_DIR = os.path.join(SRC_DIR, 'utils')

# Caminho para a pasta 'modules'
MODULES_DIR = os.path.join(SRC_DIR, 'modules')

# Caminho para a pasta 'temp'
TEMP_DIR = os.path.join(SRC_DIR, 'temp')

# Caminho para a pasta 'config'
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# Caminho para a pasta 'resources'
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

# Caminho para a pasta 'dist' (onde o PyInstaller colocará o executável)
DIST_DIR = os.path.join(BASE_DIR, 'dist')