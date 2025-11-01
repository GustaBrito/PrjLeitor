import os
import sys
import json
import pickle
import google.generativeai as genai
from flask import Flask, request, render_template, redirect, url_for, flash, session
from markdown import markdown
import logging
logger = logging.getLogger(__name__)

from src.utils.constantes import Constantes, Caminhos
from src.modules.funcoes import Arquivo, Gemini
from src.utils.prompts import Prompts

# Evita criação de __pycache__
sys.dont_write_bytecode = True

# === Configuração do Gemini ===
print("\n🔌 Configurando conexão com Gemini...")
try:
    genai.configure(api_key=Constantes.CHAVE_API_GEMINI)
    modelo = genai.GenerativeModel(
        model_name=Constantes.MODELO_GEMINI,
        generation_config=Constantes.CONFIG_GEMINI
    )
    print("✅ Conexão com Gemini configurada com sucesso")
except Exception as e:
    print(f"❌ Erro na configuração do Gemini: {str(e)}")
    raise

# === Configuração do Flask ===
app = Flask(
    __name__,
    template_folder=str(Caminhos.TEMPLATES_DIR),
    static_folder=str(Caminhos.STATIC_DIR),
)
app.secret_key = Constantes.CHAVE_FLASK
app.config["UPLOAD_FOLDER"] = Constantes.PASTA_UPLOAD

# Garante que as pastas existem
Arquivo.criar_pastas()

# === Rota inicial ===
@app.route("/", methods=["GET"])
def index():
    session.clear()
    return render_template("upload.html")





# === Rota de upload ===
@app.route("/upload", methods=["POST"])
def upload_arquivo():
    print("\n=== NOVO PROCESSAMENTO INICIADO ===")
    
    # Validação básica (mantida igual)
    if "file" not in request.files:
        print("❌ Erro: Nenhum arquivo foi enviado")
        flash("Nenhum arquivo foi enviado.")
        return render_template("upload.html")

    arquivos = request.files.getlist("file")
    if not arquivos or all(f.filename == '' for f in arquivos):
        print("❌ Erro: Nenhum arquivo selecionado")
        flash("Nenhum arquivo selecionado.")
        return render_template("upload.html")

    # CORREÇÃO: Obter opções com nomes alinhados ao HTML
    function_option = request.form.get("function_option", "text_analysis")  # Nome do radio group
    sub_option = request.form.get("analysis_type") if function_option == "text_analysis" else None
    target_lang = request.form.get("target_lang", "en") if function_option == "translation" else None
    
    print(f"\n📌 Opções selecionadas pelo usuário:")
    print(f"   - Função principal: {function_option}")
    print(f"   - Sub-opção: {sub_option if sub_option else 'Nenhuma'}")

    if function_option == "translation":
        print(f"   - Idioma de destino: {target_lang}")
    
    # Debug avançado
    logger.debug(f"Valores do formulário: {request.form.to_dict()}")

    # Mantendo compatibilidade com sua sessão existente
    session.update({
        # Nomes antigos (para compatibilidade)
        "prompt_option": function_option,
        "sub_prompt_option": sub_option,
        "target_language": target_lang,
        
        # Nomes novos (padronizados)
        "function_option": function_option,
        "analysis_type": sub_option, 
        "target_lang": target_lang,
        "sort_alpha": "sort_alpha" in request.form
    })

    # CORREÇÃO: Montagem do prompt com todas as opções
    prompt_text = Prompts.get_prompt(function_option, sub_option)
    
    if function_option == "text_analysis":
        if sub_option == "summary":
            prompt_text += Prompts.PROMPT_ANALISE_TEXTO_RESUMO

        elif sub_option == "full_extraction":
            prompt_text += Prompts.PROMPT_ANALISE_TEXTO

        elif sub_option == "sanitize":
            prompt_text += Prompts.PROMPT_ANALISE_TEXTO_HIGIENIZAR

    elif function_option == "translation":
        prompt_text += f"\n\nTraduzir para: {target_lang}\n"

    elif function_option == "math_operation":
        prompt_text += Prompts.PROMPT_OPERACAO_MATEMATICA

    elif function_option == "ai_check":
        prompt_text += Prompts.PROMPT_CHECAGEM_IA

    session["prompt"] = prompt_text
    print(f"   - Prompt configurado: {prompt_text[:200]}...")  # Log parcial do prompt

    # Processamento de arquivos (mantido igual)
    print("\n🔄 Processando arquivos recebidos...")
    resultados = Arquivo.processar_arquivos(arquivos)
    imagens = []
    for r in resultados:
        imagens += r.get("imagens", [])

    if not imagens:
        print("❌ Falha: Nenhuma imagem foi processada corretamente")
        flash("Nenhum arquivo foi processado corretamente.")
        return render_template("upload.html")

    print(f"✅ {len(imagens)} imagem(s) processada(s) com sucesso")

    # Cria os pickles temporários (mantido igual)
    session["images_file"] = Arquivo.salvar_dados_temp(imagens, "images.pkl")
    session["results_file"] = Arquivo.salvar_dados_temp([], "results.pkl")
    session["raw_file"] = Arquivo.salvar_dados_temp([], "raw_results.pkl")
    session["current_page"] = 0

    print("\n⏳ Redirecionando para processamento...")
    return redirect(url_for("process_page"))




# === Rota de processamento iterativo ===
@app.route("/process_page")
def process_page():
    print("\n=== PROCESSANDO PÁGINA ===")
    
    # Verificação completa da sessão
    required_session_keys = ["images_file", "results_file", "raw_file", "prompt_option", "prompt"]
    for key in required_session_keys:
        if key not in session:
            print(f"❌ Erro: Sessão inválida - chave '{key}' faltando")
            flash("Sessão inválida. Por favor, tente novamente.")
            return redirect(url_for("index"))
    
    try:
        imagens = Arquivo.carregar_dados_temp(session["images_file"])
        if not imagens:
            print("❌ Erro: Nenhuma imagem disponível para processamento")
            flash("Nenhuma imagem disponível para processamento.")
            return redirect(url_for("index"))

        page = session.get("current_page", 0)
        
        # Verificação crítica para evitar IndexError
        if page >= len(imagens):
            print("ℹ️ Todas as imagens foram processadas, finalizando...")
            result = finalizar_processamento()
            if result is None:
                flash("Erro ao finalizar processamento.")
                return redirect(url_for("index"))
            return result
            
        print(f"📋 Configuração atual:")
        print(f"   - Página: {page+1}/{len(imagens)}")
        print(f"   - Opção: {session['prompt_option']}")
        print(f"   - Sub-opção: {session.get('sub_prompt_option', 'Nenhuma')}")
        print(f"   - Prompt: {session['prompt'][:100]}...")

        # Processamento seguro da imagem
        img_path = imagens[page]
        print(f"🖼️ Processando imagem {page+1}: {img_path}")
        
        try:
            print("   🔄 Enviando para Gemini...")
            raw_text = Gemini.processar_imagem(img_path, modelo, session["prompt"])
            print(f"   ✅ Resposta recebida ({len(raw_text)} caracteres)")
            
            # Salva o resultado conforme o tipo de operação
            if session["prompt_option"] in ["summarize", "translate", "text_analysis"] and \
               session.get("sub_prompt_option") in [None, "resumo", "higienizar"]:
                print("   💾 Salvando em raw_file")

                chunks = Arquivo.carregar_dados_temp(session["raw_file"])
                chunks.append(raw_text)
                Arquivo.salvar_dados_temp(chunks, session["raw_file"])
            else:
                print("   💾 Salvando em results_file")
                lst = Arquivo.carregar_dados_temp(session["results_file"])
                lst.append(raw_text)
                Arquivo.salvar_dados_temp(lst, session["results_file"])
                
            # Atualiza a página ou finaliza
            session["current_page"] = page + 1
            if page + 1 < len(imagens):
                return redirect(url_for("process_page"))
            
            result = finalizar_processamento()
            if result is None:
                flash("Erro ao finalizar processamento.")
                return redirect(url_for("index"))
            return result
                
        except Exception as e:
            print(f"❌ Erro no processamento: {str(e)}")
            logger.error(f"Erro ao processar imagem: {str(e)}", exc_info=True)
            flash("Erro ao processar imagem. Por favor, tente novamente.")
            return redirect(url_for("index"))
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        logger.error(f"Erro geral no processamento: {str(e)}", exc_info=True)
        flash("Erro no processamento. Por favor, tente novamente.")
        return redirect(url_for("index"))

def finalizar_processamento():
    """Função para processar resultados finais"""
    try:
        prompt_opt = session["prompt_option"]
        sub_opt = session.get("sub_prompt_option")
        
        print(f"\n🏁 Finalizando processamento - {prompt_opt}")
        if sub_opt:
            print(f"   - Sub-opção: {sub_opt}")
        
        # --- SUMMARIZE ---
        if prompt_opt == "summarize":
            print("📝 Gerando resumo do conteúdo...")
            chunks = Arquivo.carregar_dados_temp(session["raw_file"])
            md = "\n\n".join(chunks)
            html = markdown(md, extensions=["fenced_code","tables","smarty"])
            return render_template(
                "result.html",
                results={"summary_text": html},
                prompt_option=prompt_opt
            )

        # --- VALIDATE ---
        elif prompt_opt == "validate":
            print("🔍 Validando conteúdo...")
            raw_list = Arquivo.carregar_dados_temp(session["results_file"])
            all_errors = []
            
            for raw in raw_list:
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        errs = parsed.get("errors", [])
                    elif isinstance(parsed, list):
                        errs = parsed
                    else:
                        continue
                        
                    all_errors.extend(errs)
                except json.JSONDecodeError:
                    continue

            return render_template(
                "result.html",
                results={"errors": all_errors, "total_errors": len(all_errors)},
                prompt_option=prompt_opt
            )

        # --- EXTRACT ---
        elif prompt_opt == "extract":
            print("📊 Extraindo dados...")
            raw_list = Arquivo.carregar_dados_temp(session["results_file"])
            all_data = {"columns": [], "rows": [], "charts": []}
            
            for raw in raw_list:
                try:
                    obj = json.loads(raw)
                    if not all_data["columns"]:
                        all_data["columns"] = obj.get("table", {}).get("columns", [])
                    all_data["rows"].extend(obj.get("table", {}).get("rows", []))
                    all_data["charts"].extend([
                        f"data:image/png;base64,{c['image']}" 
                        if not c['image'].startswith("data:image") 
                        else c['image']
                        for c in obj.get("charts", [])
                    ])
                except:
                    continue

            return render_template(
                "result.html",
                results=all_data,
                prompt_option=prompt_opt
            )

        # --- TRANSLATE ---
        elif prompt_opt == "translate":
            print(f"🌍 Traduzindo para {session.get('target_language', 'en')}...")
            blocks = Arquivo.carregar_dados_temp(session["results_file"])
            html = markdown("\n\n".join(blocks), extensions=["fenced_code", "tables", "smarty"])
            return render_template(
                "result.html",
                results={"summary_text": html},
                prompt_option=prompt_opt
            )
            
    # --- TEXT ANALYSIS ---
        elif prompt_opt == "text_analysis":
            if sub_opt == "resumo":
                print("📑 Gerando resumo...")
                chunks = Arquivo.carregar_dados_temp(session["raw_file"])
                html = markdown("\n\n".join(chunks), extensions=["fenced_code","tables","smarty"])
                return render_template(
                    "result.html",
                    results={"summary_text": html},
                    prompt_option=prompt_opt,
                    sub_prompt_option=sub_opt
                )
            
            elif sub_opt == "full_extraction":
                print("🔎 Extraindo dados completos...")
                try:
                    # Carrega os dados brutos
                    raw_responses = Arquivo.carregar_dados_temp(session["results_file"])
                    
                    # Debug - verifique o conteúdo real
                    print(f"Conteúdo bruto recebido (primeiros 300 chars): {str(raw_responses)[:300]}")
                    
                    # Processa como texto puro
                    extracted_text = "\n\n".join([str(r) for r in raw_responses])
                    
                    # Debug crítico - salva em arquivo
                    debug_path = os.path.join(Constantes.PASTA_DADOS_TEMP, "FULL_DEBUG.txt")
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(f"=== DEBUG FULL EXTRACTION ===\n")
                        f.write(f"Tipo do conteúdo: {type(raw_responses)}\n")
                        f.write(f"Tamanho: {len(raw_responses)}\n")
                        f.write(f"Conteúdo:\n{extracted_text}")
                    
                    return render_template(
                        "result.html",
                        results={
                            "extracted_text": extracted_text,
                            "raw_data": raw_responses  # Envia os dados brutos também
                        },
                        prompt_option=prompt_opt,
                        sub_prompt_option="extracao_completa"  # Aqui é o pulo do gato - deve bater com o template
                    )
                except Exception as e:
                    print(f"ERRO CRÍTICO NO PROCESSAMENTO: {str(e)}")
                    logger.error(f"Erro fatal em full_extraction: {str(e)}", exc_info=True)
                    flash("Falha ao processar extração completa")
                    return redirect(url_for("index"))

        # --- AI CHECK ---
        elif prompt_opt == "ai_check":
            print("🤖 Verificando IA...")
            ai_results = []
            for raw in Arquivo.carregar_dados_temp(session["results_file"]):
                try:
                    ai_results.append(json.loads(raw))
                except:
                    continue
            
            return render_template(
                "result.html",
                results={"ai_results": ai_results},
                prompt_option=prompt_opt
            )

        # --- MATH OPERATION ---
        elif prompt_opt == "math_operation":
            print("🧮 Processando matemática...")
            html = markdown("\n\n".join(Arquivo.carregar_dados_temp(session["raw_file"])), 
                         extensions=["fenced_code","tables","smarty"])
            return render_template(
                "result.html",
                results={"math_solutions": html},
                prompt_option=prompt_opt
            )
        
        else:
            print(f"❌ Opção desconhecida: {prompt_opt}")
            flash("Opção de processamento não reconhecida")
            return redirect(url_for("index"))
            
    except Exception as e:
        print(f"❌ Erro ao finalizar: {str(e)}")
        logger.error(f"Erro finalizando processamento: {str(e)}", exc_info=True)
        flash("Erro ao gerar resultados finais.")
        return redirect(url_for("index"))

# === Rota para limpar temp via beacon ===
@app.route("/limpar", methods=["POST"])
def limpar_dados():
    for p in (
        Constantes.PASTA_UPLOAD,
        Constantes.PASTA_DADOS_TEMP,
        Constantes.PASTA_IMAGENS_TEMP
    ):
        try:
            Arquivo.limpar_conteudo_pasta(p)
        except Exception as e:
            logger.error(f"Erro limpando pasta {p}: {str(e)}")
    return "Dados limpos", 200

def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    run_flask()