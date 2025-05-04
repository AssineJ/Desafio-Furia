from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import re
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Regex para detectar termos relacionados a CS:GO
cs_regex = re.compile(
    r'\b(cs[\s-]?2?|counter[\s-]?strike|mapa|arma|strat|granada|bomba|ct|terrorista|eco|round|clutch|retake|defuse|awp|ak|m4|pistola|skin|patch|fps|objetivo|economia)\b',
    re.IGNORECASE
)

# URL da API do Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

# Prompt do sistema para o bot
SYSTEM_PROMPT = """<|system|>
Você é o SargeBot, assistente especialista em Counter-Strike. Siga estas regras:
1. Português brasileiro claro e objetivo
2. Tom militar humorístico (ex: "Recruta!", "Soldado!")
3. 2-3 parágrafos curtos com quebras de linha
4. Use **negrito** apenas para termos técnicos importantes
5. Máximo 2 emojis por resposta
6. Formatação proibida: markdown, parênteses complexos
7. Sempre expanda siglas na primeira menção (ex: "CS (Counter-Strike)")
8. Respostas devem ser informativas e úteis 


- Use 2-4 emojis relevantes por resposta
- Exemplos de combinações:
  Armas: 🔫💣
  Mapas: 🗺️📍
  Estratégias: 🧠🎯
  Vitórias: 🏆✨
  Erros: 💥🚨
- Mantenha a profissionalidade militar

Exemplo ruim: "Counter Strike (*CS** pra os íntimos)"
Exemplo correto: "Counter-Strike (CS para os íntimos)"
</s>
"""

def clean_response(text):
    """Limpa formatações indesejadas da resposta do modelo"""
    # Remove texto antes de <|assistant|> se presente
    if "<|assistant|>" in text:
        text = text.split("<|assistant|>")[-1]
    
    # Remove tags e outros elementos de formatação
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
        # Obtém a chave API do cabeçalho
        user_key = request.headers.get('X-API-Key')
        data = request.get_json()
        
        # Validação básica
        if not user_key or not user_key.startswith('hf_'):
            logger.warning("Tentativa de acesso com chave API inválida")
            return jsonify({"response": "🔒 Chave API inválida! Por favor, recarregue a página e insira uma chave válida."}), 401
        
        user_message = data.get('message', '')
        logger.info(f"Mensagem recebida: {user_message[:30]}...")
        
        # Gera o prompt completo
        full_prompt = f"{SYSTEM_PROMPT}<|user|>\n{user_message}</s>\n<|assistant|>\n"
        
        # Faz a requisição para o modelo
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
            
            # Verifica a resposta da API
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    if isinstance(response_json, list) and len(response_json) > 0:
                        raw_text = response_json[0].get('generated_text', '')
                        clean_text = clean_response(raw_text)
                        return jsonify({"response": clean_text})
                    else:
                        logger.error(f"Formato de resposta inesperado: {response_json}")
                        return jsonify({"response": "Formato de resposta inesperado do modelo. Tente novamente. 🔄"}), 500
                except Exception as e:
                    logger.error(f"Erro ao processar JSON da resposta: {str(e)}")
                    return jsonify({"response": f"Erro ao processar resposta do modelo: {str(e)}. 📝"}), 500
            else:
                error_msg = f"Erro na API Hugging Face: Código {response.status_code}"
                logger.error(error_msg)
                
                # Tratamento específico para erros comuns
                if response.status_code == 401:
                    return jsonify({"response": "🔑 Chave API inválida ou sem permissões! Verifique se sua chave possui acesso Read."}), 401
                elif response.status_code == 503:
                    return jsonify({"response": "⏳ O modelo está sendo carregado ou está sobrecarregado. Tente novamente em alguns segundos."}), 503
                else:
                    return jsonify({"response": f"Erro no servidor: {error_msg}. Tente novamente. 🛠️"}), response.status_code
        
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
            logger.debug(f"Chave recebida: {user_key[:6]}...")  # Log parcial por segurança
        
        # Primeira validação: formato básico
        if not user_key.startswith('hf_'):
            logger.error("Formato de chave inválido")
            return jsonify({"valid": False, "error": "Formato inválido (deve começar com hf_)"}), 400

        # Segunda validação: endpoint de status da HF
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

def showChatInterface():
    """Função auxiliar para mostrar a interface de chat"""
    pass

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=5000)