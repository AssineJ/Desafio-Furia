from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import re
import logging


load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})

cs_regex = re.compile(
    r'\b(cs[\s-]?2?|counter[\s-]?strike|mapa|arma|strat|granada|bomba|ct|terrorista|eco|round|clutch|retake|defuse|awp|ak|m4|pistola|skin|patch|fps|objetivo|economia)\b',
    re.IGNORECASE
)

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_API_KEY = os.getenv("HF_API_KEY")
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

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

def clean_response(text: str) -> str:
    replacements = {
        "**": "",       
        "*": "",       
        "(/": "(",      
        "*)": ")",      
        " ,": ",",      
        " .": "."       
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def generate_response(user_input: str) -> str:
    try:
        full_prompt = f"{SYSTEM_PROMPT}<|user|>\n{user_input}</s>\n<|assistant|>\n"
        
        response = requests.post(
            HF_API_URL,
            headers=headers,
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
            timeout=25
        )

        if response.status_code == 200:
            raw_text = response.json()[0]['generated_text']
            response_text = raw_text.split("<|assistant|>")[-1]
            return clean_response(response_text)
            
        return "Erro no QG! Tente novamente mais tarde. 🔧"

    except requests.exceptions.Timeout:
        return "Tempo esgotado! O servidor demorou muito para responder. ⏳"
    except Exception as e:
        app.logger.error(f"Erro crítico: {str(e)}")
        return "Falha geral no sistema! Recarregue o navegador. 💥"
    
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_key = request.headers.get('X-API-Key')
        data = request.get_json()
        
        # Validação dupla da chave
        if not user_key or not user_key.startswith('hf_'):
            return jsonify({"response": "🔒 Chave API inválida!"}), 401
            
        # Sua lógica de IA aqui
        return jsonify({"response": "Resposta de teste do servidor!"})
        
    except Exception as e:
        return jsonify({"response": f"Erro: {str(e)}"}), 500


@app.route('/api/validate-key', methods=['POST'])
def validate_key():
    try:
        app.logger.debug("Recebendo requisição de validação de chave")
        data = request.get_json()
        
        if not data or 'apiKey' not in data:
            app.logger.error("Formato JSON inválido")
            return jsonify({"valid": False, "error": "Formato inválido"}), 400
            
        user_key = data['apiKey']
        app.logger.debug(f"Chave recebida: {user_key[:6]}...")  # Log parcial por segurança

        # Primeira validação: formato básico
        if not user_key.startswith('hf_'):
            app.logger.error("Formato de chave inválido")
            return jsonify({"valid": False, "error": "Formato inválido (deve começar com hf_)"}), 400

        # Segunda validação: endpoint de status
        try:
            response = requests.get(
                'https://huggingface.co/api/whoami-v2',
                headers={'Authorization': f'Bearer {user_key}'},
                timeout=30
            )
            app.logger.debug(f"Status da HF API: {response.status_code}")
            
            if response.status_code == 200:
                return jsonify({"valid": True})
                
            return jsonify({
                "valid": False,
                "error": f"Erro de autenticação (HTTP {response.status_code})"
            }), 401

        except requests.exceptions.Timeout:
            app.logger.error("Timeout na conexão com Hugging Face")
            return jsonify({"valid": False, "error": "Timeout - Servidor não respondeu"}), 504
            
        except Exception as e:
            app.logger.error(f"Erro na requisição: {str(e)}")
            return jsonify({"valid": False, "error": str(e)}), 500

    except Exception as e:
        app.logger.critical(f"Erro crítico: {str(e)}")
        return jsonify({"valid": False, "error": "Erro interno do servidor"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "version": "1.2.0"}), 200