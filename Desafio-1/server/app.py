# server/app.py
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

load_dotenv()  # Carrega variáveis do .env

app = Flask(__name__)

# Configurações da API Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_API_KEY = os.getenv("HF_API_KEY")

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# Prompt base para o chatbot (ajustado para CS:GO)
SYSTEM_PROMPT = """Você é um especialista em Counter Strike (todas as versões) chamado SargeBot. Suas respostas devem:
- Ser em português
- Ter tom humorístico mas informativo
- Focar em dicas, atualizações de patches e cenário competitivo
- Evitar informações desatualizadas
- Negar respostas não relacionadas ao CS
Exemplo: "Soldado, pra plantar a bomba do conhecimento é aqui mesmo! 🔥"
"""

def generate_response(user_input: str) -> str:
    prompt = f"[INST] {SYSTEM_PROMPT}\n\nUsuário: {user_input} [/INST]"
    
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 150}}
        )
        return response.json()[0]['generated_text'].split("[/INST]")[-1].strip()
    except Exception as e:
        return "Erro no quartel general! Tente novamente. 💥"

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    
    # Filtro básico para temas não relacionados
    cs_keywords = [
        'cs', 'counter strike', 'mapa', 'arma', 'granada', 'bomba', 'ct', 'terrorista',
        'dust2', 'inferno', 'mirage', 'cache', 'overpass', 'strat', 'dica', 'competitivo',
        'patch', 'atualizaç', 'skins', 'treino', 'prática', 'esquadrão', 'round', 'eco',
        'headshot', 'awp', 'ak-47', 'm4a1', 'smoke', 'flashbang', 'molotov', 'clutch',
        'ace', 'spray', 'recoil', 'plantar', 'defusar', 'economia', 'frag', 'ranked',
        'fps', 'servidor', 'lan', 'hltv', 'major', 'boost', 'pixel', 'crosshair', 'demo',
        'squad', 'team', 'tática', 'estratégia', 'mapa', 'posição', 'jogador', 'skin',
        'clan', 'esports', 'competição', 'torneio', 'ranking', 'clutch', 'eco round',
        'force buy', 'save round', 'pistol round', 'anti-eco', 'anti-force', 'buy round',
        'force', 'save', 'buy', 'rush', 'split', 'exec', 'fake', 'retake',
        # Mapas do Counter Strike
        'ancient', 'anubis', 'aztec', 'cobblestone', 'train', 'nuke', 'vertigo', 'office',
        'agency', 'italy', 'assault', 'militia', 'shortdust', 'shortnuke', 'lake', 'canals',
        'dust', 'tuscan', 'seaside', 'santorini', 'abbey', 'biome', 'subzero', 'chlorine',
        'grind', 'mocha', 'blagai', 'basalt', 'pitstop', 'calavera', 'depot', 'anarchy','dust2',
        'inferno', 'mirage', 'cache', 'overpass', 'train', 'nuke', 'vertigo', 'ancient',
        'anubis', 'aztec', 'cobblestone', 'office', 'agency', 'italy', 'assault', 'militia',
    ]
    
    # Verifica se a mensagem contém palavras-chave relacionadas ao CS
    if not any(keyword in user_message.lower() for keyword in cs_keywords):
        return jsonify({"response": "Soldado, essa não é uma missão do CS! Tente algo mais relacionado ao jogo. 🚫"})
    
    bot_response = generate_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)