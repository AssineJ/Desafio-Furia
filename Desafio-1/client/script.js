document.addEventListener('DOMContentLoaded', () => {
    const savedKey = localStorage.getItem('hfApiKey');
    if (savedKey) {
        showChatInterface();
    } else {
        document.getElementById('authContainer').style.display = 'flex';
    }
});

document.getElementById('apiKeyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const apiKey = document.getElementById('apiKeyInput').value;
    const errorElement = document.getElementById('apiError');

    try {
        const isValid = await validateAPIKey(apiKey);
        if (isValid) {
            localStorage.setItem('hfApiKey', apiKey);
            showChatInterface();
        } else {
            errorElement.textContent = 'Chave inválida! Verifique e tente novamente.';
        }
    } catch (error) {
        errorElement.textContent = 'Erro de conexão. Tente novamente mais tarde.';
    }
});

document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    const messagesDiv = document.getElementById('chatMessages');
    
    if (!message) return;

    // Adiciona mensagem do usuário
    messagesDiv.innerHTML += `
        <div class="message user-message">
            ${message}
        </div>
    `;
    input.value = '';

    // Resposta do bot
    try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': localStorage.getItem('hfApiKey')
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) throw new Error('Erro na resposta');
        
        const data = await response.json();
        messagesDiv.innerHTML += `
            <div class="message">
                🎮 Assistente: ${data.response}
            </div>
        `;
    } catch (error) {
        messagesDiv.innerHTML += `
            <div class="message error">
                💥 Erro: Não foi possível obter resposta
            </div>
        `;
    }

    // Scroll automático
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

async function validateAPIKey(key) {
    const errorElement = document.getElementById('apiError');
    errorElement.innerHTML = '<div class="loading">🔍 Validando chave...</div>';

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch('http://localhost:5000/api/validate-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ apiKey: key }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `Erro HTTP ${response.status}`);
        }

        if (!data.valid) {
            throw new Error('Chave API não autorizada');
        }

        return true;

    } catch (error) {
        let errorMessage = 'Erro de conexão';
        if (error.name === 'AbortError') {
            errorMessage = 'Timeout: Servidor não respondeu após 30 segundos';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Servidor offline ou bloqueado pelo firewall';
        } else if (error.message.includes('HTTP 401')) {
            errorMessage = 'Chave API inválida ou sem permissões';
        }

        showError(`
            ${errorMessage}
            <br>
            <small>
                Dicas:
                <ul>
                    <li>Verifique sua conexão com a internet</li>
                    <li>Libere a porta 5000 no firewall</li>
                    <li>Teste em outro navegador</li>
                    <li>Execute <code>curl http://localhost:5000/api/health</code></li>
                </ul>
            </small>
        `);
        return false;
    }
}