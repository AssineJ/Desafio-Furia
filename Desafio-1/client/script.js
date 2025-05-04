// Função para mostrar a interface de chat
function showChatInterface() {
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('chatContainer').classList.add('visible');
    
    // Adiciona mensagem de boas-vindas
    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.innerHTML = `
        <div class="message">
            🎮 Assistente: Olá, recruta! Sargento Bot a seu serviço para ajudar com Counter-Strike (CS)! Qual informação você precisa hoje? Mapas, armas, estratégias ou dicas para melhorar sua performance? 🫡🔫
        </div>
    `;
}

// Função para mostrar mensagens de erro
function showError(message) {
    const errorElement = document.getElementById('apiError');
    errorElement.innerHTML = `
        <div class="error-details">
            <p class="error-message">${message}</p>
            <small>
                Dicas:
                <ul>
                    <li>Verifique sua conexão com a internet</li>
                    <li>Libere a porta 5000 no firewall</li>
                    <li>Teste em outro navegador</li>
                    <li>Execute <code>curl http://localhost:5000/api/health</code></li>
                </ul>
            </small>
        </div>
    `;
}

// Função para resetar a chave API
function resetAPIKey() {
    if (confirm('Tem certeza que deseja alterar sua chave API? Você será desconectado.')) {
        localStorage.removeItem('hfApiKey');
        window.location.reload();
    }
}

// Função para validar a chave API
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

        showError(errorMessage);
        return false;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log("Página carregada, verificando chave API...");
    const savedKey = localStorage.getItem('hfApiKey');
    if (savedKey) {
        console.log("Chave encontrada, mostrando interface de chat");
        showChatInterface();
    } else {
        console.log("Nenhuma chave encontrada, mostrando tela de autenticação");
        document.getElementById('authContainer').style.display = 'flex';
    }
    
    // Configuração do formulário de chave API
    document.getElementById('apiKeyForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log("Formulário de chave API enviado");
        const apiKey = document.getElementById('apiKeyInput').value;
        
        try {
            const isValid = await validateAPIKey(apiKey);
            console.log("Resultado da validação:", isValid);
            if (isValid) {
                localStorage.setItem('hfApiKey', apiKey);
                showChatInterface();
            }
        } catch (error) {
            console.error("Erro durante validação:", error);
            document.getElementById('apiError').textContent = error.message || 'Erro de conexão. Tente novamente mais tarde.';
        }
    });
    
    // Configuração do formulário de chat
    document.getElementById('chatForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        const messagesDiv = document.getElementById('chatMessages');
        
        if (!message) return;
        
        console.log("Enviando mensagem:", message.substring(0, 20) + "...");

        // Adiciona mensagem do usuário
        messagesDiv.innerHTML += `
            <div class="message user-message">
                ${message}
            </div>
        `;
        input.value = '';
        
        // Adiciona mensagem de "digitando..."
        const typingId = Date.now();
        messagesDiv.innerHTML += `
            <div class="message typing" id="typing-${typingId}">
                🎮 Assistente está digitando...
            </div>
        `;
        
        // Scroll automático
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        // Resposta do bot
        try {
            console.log("Enviando requisição para o servidor...");
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': localStorage.getItem('hfApiKey')
                },
                body: JSON.stringify({ message })
            });

            // Remove mensagem de digitando
            const typingElement = document.getElementById(`typing-${typingId}`);
            if (typingElement) {
                typingElement.remove();
            }

            const data = await response.json();
            console.log("Resposta recebida:", data.response ? data.response.substring(0, 20) + "..." : "nenhuma resposta");
            
            if (!response.ok) {
                throw new Error(data.response || `Erro HTTP ${response.status}`);
            }
            
            // Adiciona resposta do assistente
            messagesDiv.innerHTML += `
                <div class="message">
                    🎮 Assistente: ${data.response || "Desculpe, não consegui processar sua mensagem. Tente novamente."}
                </div>
            `;
        } catch (error) {
            console.error("Erro ao obter resposta:", error);
            
            // Remove mensagem de digitando se ainda existir
            const typingElement = document.getElementById(`typing-${typingId}`);
            if (typingElement) {
                typingElement.remove();
            }
            
            // Adiciona mensagem de erro
            messagesDiv.innerHTML += `
                <div class="message error">
                    💥 Erro: ${error.message || 'Não foi possível obter resposta'}
                </div>
            `;
        }

        // Scroll automático novamente após a resposta
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
});