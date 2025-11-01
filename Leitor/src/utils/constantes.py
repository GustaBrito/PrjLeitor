import os
from pathlib import Path
 
# apoio/utils/constantes.py
class Constantes:
 
    # Caminho base do projeto
    DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
    # Configuração da chave de API do Gemini
    GEMINI_API_KEY="" #os.environ.get("GEMINI_API_KEY", "sua_api_key_aqui")
    CHAVE_API_GEMINI=""#os.environ.get("GEMINI_API_KEY", "sua_api_key_aqui")
    MODELO_GEMINI = 'gemini-2.0-flash'
 
    # Configuração do Flask
    CHAVE_FLASK = 'sua_chave_secreta'
 
    # Configuração do modelo Gemini
    CONFIG_GEMINI = {
        "temperature": 0.1,
        "top_p": 0.85,
        "top_k": 30,
        "max_output_tokens": 8000,
    }
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    # Define o caminho base "Leitor/apoio/temp" a partir da raiz do pacote
    pasta_base_temp = os.path.join(base_dir, "Leitor", "src", "temp")
    os.makedirs(pasta_base_temp, exist_ok=True)
    
    # Pastas temporárias
    PASTA_UPLOAD = os.path.join(pasta_base_temp, "uploads")
    PASTA_DADOS_TEMP = os.path.join(pasta_base_temp, "temp_data")
    PASTA_IMAGENS_TEMP = os.path.join(pasta_base_temp, "temp_images")
    # Extensões permitidas
    PERMITE_EXTENCAO_UPLOAD = {'pdf','jpg','png'}
 

class Caminhos:
    # 1) PROJECT_ROOT = pasta 'Leitor' (onde estão app.py e Leitor.py)
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    # 2) pasta src/
    SRC_DIR = PROJECT_ROOT / 'src'

    # 3) pasta utils/ dentro de src/
    UTILS_DIR = SRC_DIR / 'utils'

    # 4) pasta modules/ dentro de src/
    MODULES_DIR = SRC_DIR / 'modules'

    # 5) pasta temp/ dentro de src/
    TEMP_DIR = SRC_DIR / 'temp'

    # 6) subpastas de temp
    PASTA_UPLOAD       = TEMP_DIR / 'uploads'
    PASTA_DADOS_TEMP   = TEMP_DIR / 'temp_data'
    PASTA_IMAGENS_TEMP = TEMP_DIR / 'temp_images'

    # 7) pasta de assets web
    STATIC_DIR    = UTILS_DIR / 'static'

    TEMPLATES_DIR = UTILS_DIR / 'templates'
