# Desafio-Furia

### O que é o FURIA CS Assistente?

Um assistente virtual para o **E-sport de CS da FURIA** usando inteligência artificial que responde suas perguntas sobre o time e o jogo em português brasileiro.

### 💻 Pré-requisitos

>[!IMPORTANT]
>Antes de começar, verifique se você atendeu aos seguintes requisitos:
>- Python 3.8+ instalado (necessário para o backend)
>- Node.js e npm (opcional - apenas se quiser modificar o frontend)
>- Uma conexão de internet ativa
>- Navegador web moderno (Chrome, Firefox, Edge, Safari)
>- Sistemas compatíveis: Windows, macOS e Linux

### 🚀 Instalando FURIA CS Assistente

Para instalar o **FURIA CS Assistente**, siga estas etapas:

1. Clone este repositório:
```
git clone https://github.com/AssineJ/csgo-assistente.git
cd csgo-assistente
```
2.Instale as dependências Python:
```
pip install -r requirements.txt
```

O frontend é composto de arquivos estáticos HTML/CSS/JS que não precisam de instalação adicional, apenas do servidor rodando.

### ☕ Usando FURIA CS Assistente

Para iniciar o assistente, siga estas etapas:

1. Inicie o servidor backend:
```
cd server
python app.py
```
2. Abra o arquivo `client/index.html` no seu navegador ou crie um servidor local para servir os arquivos estáticos.
> [!TIP]
> Utilize a extenxão `Go Live` no Visua Studio Code

3. **Obtenha uma chave de API** gratuita do **Hugging Face**:
- Acesse [Hugging Face Tokens](https://huggingface.co/settings/tokens)
- Crie uma conta gratuita (se ainda não tiver uma)
- Gere um token com permissão **Read**
- Cole a chave no formulário de login do assistente
4. Comece a fazer perguntas sobre Counter-Strike!

### Exemplos de perguntas:

- "Quais são as melhores posições para AWP no mapa Dust 2?"
- "Como funciona a economia do CS?"
- "Quais são as melhores granadas para retake no Mirage?"
- "Dicas para melhorar minha precisão com rifles"

### 🔧 Resolução de problemas
> [!WARNING]
> Se você encontrar problemas ao executar o servidor:
> - Verifique se a porta 5000 está disponível
> - Certifique-se de que o firewall permite conexões na porta 5000
> - Verifique sua conexão com a internet
> - Teste o servidor com `curl http://localhost:5000/api/health`
