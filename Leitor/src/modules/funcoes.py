import os
import time
import pickle
import shutil
import logging
import fitz  # PyMuPDF
import google.generativeai as genai
from pathlib import Path
from PIL import Image
from src.utils.constantes import Constantes
from werkzeug.utils import secure_filename
import json
from typing import Any, Dict, List

# Fallback para versões antigas do Pillow
try:
    from PIL import Resampling
    LANCZOS_FILTER = Resampling.LANCZOS
except ImportError:
    LANCZOS_FILTER = Image.LANCZOS

#==========================================================
# Configurações de log
#==========================================================
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#==========================================================
# Classe de manipulação de arquivos
#==========================================================
class Arquivo:

    @staticmethod
    def criar_pastas():
        """Cria as pastas necessárias se não existirem."""
        for pasta in (
            Constantes.PASTA_UPLOAD,
            Constantes.PASTA_IMAGENS_TEMP,
            Constantes.PASTA_DADOS_TEMP
        ):
            Path(pasta).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Pasta garantida: {pasta!r}")

    @staticmethod
    def limpar_conteudo_pasta(caminho: str):
        """Remove todos os arquivos e subpastas, mas mantém a pasta raiz."""
        for entry in os.listdir(caminho):
            if entry == ".keep":
                continue
            caminho_entry = os.path.join(caminho, entry)
            try:
                if os.path.isfile(caminho_entry) or os.path.islink(caminho_entry):
                    os.unlink(caminho_entry)
                    logger.debug(f"Arquivo removido: {caminho_entry!r}")
                elif os.path.isdir(caminho_entry):
                    shutil.rmtree(caminho_entry)
                    logger.debug(f"Pasta removida: {caminho_entry!r}")
            except Exception as e:
                logger.error(f"Falha ao remover {caminho_entry!r}", exc_info=e)

    @staticmethod
    def arquivo_permitido(nome_arquivo: str) -> bool:
        """Verifica se o arquivo possui uma extensão permitida."""
        ext = Path(nome_arquivo).suffix.lower().lstrip(".")
        permitido = ext in Constantes.PERMITE_EXTENCAO_UPLOAD
        logger.debug(f"Extensão de {nome_arquivo!r}: {ext!r} → {'permitido' if permitido else 'não permitido'}")
        return permitido

    @staticmethod
    def salvar_arquivo(arquivo) -> str:
        """
        Salva o arquivo na pasta de upload usando nome seguro
        e retorna o caminho completo.
        """
        filename = secure_filename(arquivo.filename)
        caminho = os.path.join(Constantes.PASTA_UPLOAD, filename)
        logger.info(f"Salvando arquivo recebido: {filename!r}")
        arquivo.save(caminho)
        logger.debug(f"Arquivo salvo em {caminho!r}")
        return caminho

    @staticmethod
    def processar_pdf(caminho_arquivo: str) -> list[str]:
        """
        Converte um PDF em várias imagens PNG, uma por página.
        Retorna lista de caminhos das imagens.
        """
        imagens = []
        documento = fitz.open(caminho_arquivo)
        base = Path(caminho_arquivo).stem
        for i in range(documento.page_count):
            pix = documento.load_page(i).get_pixmap(dpi=300)
            out = os.path.join(Constantes.PASTA_IMAGENS_TEMP, f"{base}_pagina_{i+1}.png")
            pix.save(out)
            imagens.append(out)
            logger.debug(f"Página {i+1} salva em {out!r}")
        documento.close()
        logger.info(f"PDF convertido em {len(imagens)} imagem(ns)")
        return imagens

    @staticmethod
    def converter_imagem(caminho_arquivo: str) -> str | None:
        """
        Converte JPG/JPEG/PNG em PNG otimizado.
        Retorna caminho da PNG ou None em caso de erro.
        """
        try:
            img = Image.open(caminho_arquivo).convert("RGB")
            out_path = os.path.join(Constantes.PASTA_IMAGENS_TEMP, f"{Path(caminho_arquivo).stem}.png")
            img.save(out_path, "PNG", optimize=True)
            logger.info(f"Imagem convertida: {out_path!r}")
            return out_path
        except Exception as e:
            logger.error(f"Erro ao converter imagem {caminho_arquivo!r}", exc_info=e)
            return None

    @staticmethod
    def salvar_dados_temp(data, filename: str) -> str:
        """
        Salva qualquer objeto em pickle na pasta temp_data.
        Retorna caminho completo do arquivo.
        """
        filepath = os.path.join(Constantes.PASTA_DADOS_TEMP, filename)
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
        logger.debug(f"Dados temporários salvos em {filepath!r}")
        return filepath

    @staticmethod
    def carregar_dados_temp(filepath: str):
        """
        Carrega dados de um pickle da pasta temp_data.
        Retorna o objeto desserializado.
        """
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        logger.debug(f"Dados temporários carregados de {filepath!r}")
        return data

    @staticmethod
    def analisar_resultado(texto: str) -> list[dict]:
        """
        Extrai itens formatados de uma string (produto, preço, etc.).
        Retorna lista de dicionários.
        """
        logger.info(f"Analisando resultado de {len(texto)} caracteres")
        itens = []
        atual = {"descricao": "", "preco": "", "preco_clube": "", "observacao": ""}
        for linha in texto.splitlines():
            l = linha.strip()
            low = l.lower()
            if low.startswith("produto:"):
                if any(atual.values()):
                    itens.append(atual)
                    atual = {"descricao": "", "preco": "", "preco_clube": "", "observacao": ""}
                atual["descricao"] = l.split(":", 1)[1].strip()
            elif low.startswith("preço:"):
                atual["preco"] = l.split(":", 1)[1].strip()
            elif "preço no clube" in low:
                atual["preco_clube"] = l.split(":", 1)[1].strip()
            elif "observação:" in low:
                atual["observacao"] = l.split(":", 1)[1].strip()
        if any(atual.values()):
            itens.append(atual)
        logger.info(f"{len(itens)} item(ns) extraído(s)")
        return itens

    @staticmethod
    def processar_arquivos(arquivos) -> list[dict]:
        """
        Processa lista de arquivos: valida extensão, salva, converte PDF/imagem.
        Retorna lista de {'arquivo': nome, 'imagens': [caminhos]}.
        """
        logger.info(f"Processando {len(arquivos)} arquivo(s) recebidos")
        resultados = []
        for arq in arquivos:
            if not arq or not arq.filename:
                continue
            ext = Path(arq.filename).suffix.lower().lstrip(".")
            logger.info(f"Arquivo {arq.filename!r} → extensão {ext!r}")
            if ext not in Constantes.PERMITE_EXTENCAO_UPLOAD:
                logger.warning(f"Extensão não permitida: {arq.filename!r}")
                continue
            caminho = Arquivo.salvar_arquivo(arq)
            if ext == "pdf":
                imgs = Arquivo.processar_pdf(caminho)
            else:
                conv = Arquivo.converter_imagem(caminho)
                imgs = [conv] if conv else []
            resultados.append({"arquivo": arq.filename, "imagens": imgs})
        return resultados

    @staticmethod
    def parse_validation(json_text: str) -> Dict[str, Any]:
        """
        Recebe o JSON de validação (lista de erros + total_errors)
        e devolve um dict:
          {
            'errors': [ {field, value, error}, … ],
            'total_errors': int
          }
        """
        try:
            data = json.loads(json_text)
            # se for dict com chave total_errors
            if isinstance(data, dict) and 'total_errors' in data:
                total = data.pop('total_errors')
                errors = data.get('errors', [])
            # se for lista cujos últimos elem. tem total_errors
            elif isinstance(data, list) and data and isinstance(data[-1], dict) and 'total_errors' in data[-1]:
                total = data[-1].pop('total_errors')
                errors = data[:-1]  # todos exceto o último
            else:
                errors = data if isinstance(data, list) else []
                total = len(errors)
            return {'errors': errors, 'total_errors': total}
        except json.JSONDecodeError:
            logger.error("Falha ao parsear JSON de validação", exc_info=True)
            return {'errors': [], 'total_errors': 0}

    @staticmethod
    def parse_extraction(json_text: str) -> Dict[str, Any]:
        """
        Recebe o JSON de extração com:
          {
            "table": { "columns": [...], "rows": [[...],...] },
            "charts": [
              { "chart_type": "pie"|"bar", "description": "...", "image": "<base64>" },
              …
            ]
          }
        Retorna:
          {
            'columns': [...],
            'rows': [[…], …],
            'charts': [ "data:image/png;base64,…", … ]
          }
        """
        try:
            obj = json.loads(json_text)
            tbl = obj.get('table', {})
            columns = tbl.get('columns', [])
            rows    = tbl.get('rows', [])
            charts  = []
            for c in obj.get('charts', []):
                img = c.get('image', '')
                # já pode vir com prefixo data:image…, ou só o base64
                if not img.startswith('data:image'):
                    img = f"data:image/png;base64,{img}"
                charts.append(img)
            return {'columns': columns, 'rows': rows, 'charts': charts}
        except Exception:
            logger.error("Falha ao parsear JSON de extração", exc_info=True)
            return {'columns': [], 'rows': [], 'charts': []}

    @staticmethod
    def parse_translation(text: str, target_language: str) -> Dict[str, str]:
        """
        Retorna um dict com o texto traduzido e o idioma destino.
        """
        return {'translated_text': text, 'target_language': target_language}

#==========================================================
# Classe responsável pelo Gemini
#==========================================================
class Gemini:
    # Configura o SDK
    genai.configure(api_key=Constantes.CHAVE_API_GEMINI)

    @staticmethod
    def processar_imagem(img_path: str, model, prompt: str) -> str:
        """
        Envia a imagem ao modelo, faz polling até ACTIVE e retorna o texto gerado.
        Em caso de erro, reduz a imagem e tenta de novo.
        """
        logger.info(f"Gerando conteúdo para {img_path!r}")
        def _upload_e_gerar(caminho):
            upload = genai.upload_file(caminho, mime_type="image/png")
            while genai.get_file(upload.name).state.name != "ACTIVE":
                time.sleep(2)
            resp = model.generate_content([upload, prompt])
            return resp.text or "Nenhuma informação extraída."

        try:
            return _upload_e_gerar(img_path)
        except Exception:
            logger.exception("Falha na primeira tentativa")
            reduzido = os.path.join(Constantes.PASTA_IMAGENS_TEMP, "temp_reduzida.png")
            with Image.open(img_path) as img:
                w, h = img.size
                img.resize((int(w*0.9), int(h*0.9)), LANCZOS_FILTER).save(reduzido, optimize=True, quality=85)
            logger.info("Tentando novamente com imagem reduzida")
            try:
                return _upload_e_gerar(reduzido)
            except Exception:
                logger.exception("Falha na segunda tentativa")
                return "Erro ao processar imagem."
