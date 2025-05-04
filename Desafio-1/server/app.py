from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import re
import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

<<<<<<< HEAD
# Expressões regulares para identificar consultas relacionadas à FURIA e CS
furia_regex = re.compile(
    r'\b(furia|furiagg|furiabet|kscerato|yuurih|art|saffee|chelo|fallen|honda|guerri|tacitus|brazil|cs[\s-]?2?|counter[\s-]?strike|mapa|arma|strat|granada|bomba|ct|terrorista|eco|round|clutch|retake|defuse|awp|ak|m4|pistola|skin|patch|fps|objetivo|economia|major|blast|esl|iem)\b',
=======
cs_regex = re.compile(
    r'\b(cs[\s-]?2?|counter[\s-]?strike|mapa|arma|strat|granada|bomba|ct|terrorista|eco|round|clutch|retake|defuse|awp|ak|m4|pistola|skin|patch|fps|objetivo|economia)\b',
>>>>>>> 43eca185ff679b4261273b7c5de71a1990fd6383
    re.IGNORECASE
)

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

SYSTEM_PROMPT = """<|system|>
Você é um assistente especialista sobre a equipe FURIA Esports de Counter-Strike. Siga estas regras:

1. Português brasileiro claro e objetivo
2. Tom entusiasmado de fã, usando gírias e termos do cenário competitivo
3. 2-3 parágrafos curtos com quebras de linha
4. Use **negrito** apenas para termos técnicos importantes
5. Máximo 2-4 emojis por resposta (preferencialmente relacionados à FURIA: 🐯🖤💛)
6. Formatação proibida: markdown excessivo, parênteses complexos
7. Sempre priorize informações sobre a FURIA Esports

INFORMAÇÕES SOBRE A FURIA ESPORTS:
- Fundada em 2017 por Jaime "guru" Pádua e André "gordo" Akkari
- Conhecida como "Pantera Negra" ou "Os Panteras"
- Cores: Preto e Dourado
- Sede: São Paulo, Brasil
- Website: furiagg.com

ROSTER ATUAL DE CS2 (2025):
- Andrei "arT" Piovezan - Capitão/Entry Fragger/IGL
- Kaike "KSCERATO" Cerato - Rifler/Estrela do time
- Yuri "yuurih" Santos - Rifler/Clutcher
- Rafael "saffee" Costa - AWPer principal
- Gabriel "FalleN" Toledo - Rifler/AWPer secundário/Veterano
- André "chelo" Naspolini - Rifler (reserva)
- Nicholas "guerri" Nogueira - Treinador

CONQUISTAS RECENTES (2022-2025):
- Campeão BLAST Premier Fall 2024
- Top 4 Major Copenhagen 2024
- Campeão ESL Pro League Season 19
- Vice-campeão IEM Katowice 2024
- Campeão BLAST Premier World Final 2023
- Top 6 Mundial HLTV 2023 e 2024

FATOS INTERESSANTES:
- arT é conhecido por seu estilo agressivo como IGL
- KSCERATO é considerado um dos melhores riflers do mundo
- yuurih tem uma das melhores taxas de clutch do cenário
- FalleN é uma lenda do CS brasileiro que se juntou à FURIA em 2024
- A FURIA tem uma das maiores torcidas do Brasil no cenário de esports

DADOS DO TIME:
- Mapas fortes: Nuke, Ancient, Vertigo
- Mapas de ban frequentes: Mirage, Dust2
- Mapa signature: Vertigo (conhecido como "Vertigo da FURIA")
- Pontos fortes: Agressividade, adaptação mid-round, trabalho em equipe
- Rivalidades: NAVI, Vitality, Imperial (clássico brasileiro)

Responda perguntas sobre CS2 em geral também, mas sempre relacione ao contexto da FURIA quando possível.
</s>
"""

def clean_response(text):
    """Limpa formatações indesejadas da resposta do modelo"""
    if not text or not isinstance(text, str):
        return "Não foi possível gerar uma resposta válida. Tente novamente."
        
    if "<|assistant|>" in text:
        text = text.split("<|assistant|>")[-1]
    
    replacements = {
        "**": "",       
        "*": "",       
        "(/": "(",      
        "*)": ")",      
        " ,": ",",      
        " .": ".",
        "</s>": ""
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text.strip()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para processar mensagens de chat"""
    try:
        user_key = request.headers.get('X-API-Key')
        data = request.get_json()
        
        if not user_key or not user_key.startswith('hf_'):
            logger.warning("Tentativa de acesso com chave API inválida")
            return jsonify({"response": "🔒 Chave API inválida! Por favor, recarregue a página e insira uma chave válida."}), 401
        
        user_message = data.get('message', '')
        logger.info(f"Mensagem recebida: {user_message[:30]}...")
        
        full_prompt = f"{SYSTEM_PROMPT}<|user|>\n{user_message}</s>\n<|assistant|>\n"
        
        try:
            response = requests.post(
                HF_API_URL,
                headers={"Authorization": f"Bearer {user_key}"},
                json={
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 600,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "repetition_penalty": 1.2,
                        "do_sample": True
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    logger.debug(f"Resposta bruta da HF: {str(response_json)[:200]}...")
                    
                    raw_text = ""
                    if isinstance(response_json, list) and len(response_json) > 0:
                        if isinstance(response_json[0], dict):
                            raw_text = response_json[0].get('generated_text', '')
                        elif isinstance(response_json[0], str):
                            raw_text = response_json[0]
                    elif isinstance(response_json, dict):
                        raw_text = response_json.get('generated_text', '')
                    
                    if not raw_text:
                        logger.warning("Não foi possível extrair texto da resposta")
                        return jsonify({"response": "Não consegui gerar uma resposta. Por favor, tente novamente. 🤔"}), 500
                        
                    clean_text = clean_response(raw_text)
                    return jsonify({"response": clean_text})
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {str(e)}")
                    try:
                        raw_text = response.text
                        if raw_text:
                            clean_text = clean_response(raw_text)
                            return jsonify({"response": clean_text})
                    except Exception:
                        pass
                    return jsonify({"response": "Erro ao processar resposta do modelo. Formato inválido. 📝"}), 500
                    
                except Exception as e:
                    logger.error(f"Erro ao processar JSON da resposta: {str(e)}")
                    return jsonify({"response": f"Erro ao processar resposta do modelo: {str(e)}. 📝"}), 500
            else:
                error_msg = f"Erro na API Hugging Face: Código {response.status_code}"
                logger.error(error_msg)
                
                error_details = ""
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error_details = f": {error_data['error']}"
                except:
                    pass
                
                if response.status_code == 401:
                    return jsonify({"response": "🔑 Chave API inválida ou sem permissões! Verifique se sua chave possui acesso Read."}), 401
                elif response.status_code == 503:
                    return jsonify({"response": "⏳ O modelo está sendo carregado ou está sobrecarregado. Tente novamente em alguns segundos."}), 503
                else:
                    return jsonify({"response": f"Erro no servidor{error_details}. Tente novamente. 🛠️"}), response.status_code
        
        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição ao modelo")
            return jsonify({"response": "⏱️ Tempo esgotado! O servidor do modelo demorou muito para responder. Tente novamente mais tarde."}), 504
            
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com a API Hugging Face")
            return jsonify({"response": "📡 Erro de conexão com o servidor do modelo. Verifique sua conexão com a internet."}), 502
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta: {str(e)}")
            return jsonify({"response": f"Erro interno ao processar a mensagem: {str(e)}. 🐞"}), 500

    except Exception as e:
        logger.error(f"Erro no endpoint /api/chat: {str(e)}")
        return jsonify({"response": f"Erro geral do sistema: {str(e)}. Por favor, recarregue a página. 💥"}), 500

@app.route('/api/validate-key', methods=['POST'])
def validate_key():
    """Endpoint para validar a chave API do Hugging Face"""
    try:
        logger.debug("Recebendo requisição de validação de chave")
        data = request.get_json()
        
        if not data or 'apiKey' not in data:
            logger.error("Formato JSON inválido na validação de chave")
            return jsonify({"valid": False, "error": "Formato inválido"}), 400
            
        user_key = data['apiKey']
        if len(user_key) >= 6:
            logger.debug(f"Chave recebida: {user_key[:6]}...")  

        if not user_key.startswith('hf_'):
            logger.error("Formato de chave inválido")
            return jsonify({"valid": False, "error": "Formato inválido (deve começar com hf_)"}), 400

        try:
            response = requests.get(
                'https://huggingface.co/api/whoami-v2',
                headers={'Authorization': f'Bearer {user_key}'},
                timeout=30
            )
            logger.debug(f"Status da HF API: {response.status_code}")
            
            if response.status_code == 200:
                return jsonify({"valid": True})
                
            return jsonify({
                "valid": False,
                "error": f"Erro de autenticação (HTTP {response.status_code})"
            }), 401

        except requests.exceptions.Timeout:
            logger.error("Timeout na conexão com Hugging Face")
            return jsonify({"valid": False, "error": "Timeout - Servidor não respondeu"}), 504
            
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return jsonify({"valid": False, "error": str(e)}), 500

    except Exception as e:
        logger.critical(f"Erro crítico na validação: {str(e)}")
        return jsonify({"valid": False, "error": "Erro interno do servidor"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde do servidor"""
    return jsonify({"status": "online", "version": "1.2.1"}), 200

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=5000)
