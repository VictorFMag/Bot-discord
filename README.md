# Bot de Discord

Este projeto é um bot de Discord com várias funcionalidades, incluindo rolagem de dados, cálculo de expressões numéricas e rolagem de dados com vantagem/desvantagem, entre outras. Ele foi desenvolvido usando a biblioteca `discord.py` e outras dependências auxiliares.

## Requisitos

Antes de rodar o bot, você precisa garantir que alguns pré-requisitos estejam instalados na sua máquina:

- **Python 3.8+**: Este projeto foi desenvolvido usando Python 3.8 ou superior.
- **ffmpeg**: O bot precisa do `ffmpeg` configurado na máquina para que possa tocar músicas. Certifique-se de que o `ffmpeg` está instalado e configurado corretamente. Você pode instalar o `ffmpeg` seguindo as instruções na [documentação oficial do ffmpeg](https://ffmpeg.org/download.html).
- **Bibliotecas de Python**: As bibliotecas necessárias para o funcionamento do bot serão instaladas via `pip`.

## Passos para rodar o projeto

### 1. Clonar o repositório

Primeiro, clone o repositório para o seu diretório local:

```bash
git clone https://github.com/usuario/bot_discord.git
cd bot_discord
```

### 2. Criar e ativar um ambiente virtual (opcional, mas recomendado)

Para isolar as dependências do seu projeto, é recomendado criar um ambiente virtual. Isso ajuda a evitar conflitos de dependência com outros projetos.

**Criar o ambiente virtual:**

```bash
python -m venv venv
```

**Ativar o ambiente virtual:**

No Windows:

```bash
venv\Scripts\activate
```

```bash
source venv/bin/activate
```

### 3. Instalar as dependências

Instale as dependências listadas no arquivo `requirements.txt`. Isso instalará todas as bibliotecas necessárias para o funcionamento do bot. Se você configurou o ambiente virtual, apenas rode o comando abaixo. Caso contrário, terá que instalar cada uma delas diretamente no ambiente global da sua máquina

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

É importante manter o token do bot e outras variáveis sensíveis fora do código-fonte. Para isso, você deve criar um arquivo .env na raiz do projeto. Crie o arquivo .env com o seguinte conteúdo:

```bash
TOKEN=seu_token_do_discord
```

### 5. Habilitar a permissão de message_content no Discord Developer Portal

Se o bot precisar acessar o conteúdo das mensagens (como mencionado no código), você também precisa habilitar a permissão Message Content Intent no Discord Developer Portal.

- Acesse o Discord Developer Portal.
- Selecione seu aplicativo (bot).
- Vá até a aba Bot.
- Em Privileged Gateway Intents, ative Message Content Intent.
- Salve as alterações.

## 6. Rodar o bot
Com o ambiente configurado e as dependências instaladas, agora você pode rodar o bot. Execute-o com o comando abaixo:

```bash
python -m bot_discord
```

## 7. Comandos do bot
Aqui estão alguns dos comandos que o bot pode executar:

- **!roll [expressão]**
Rola dados e calcula expressões numéricas. Exemplo de uso:
```bash
python -m bot_discord
```

- **!initiative [lista de pessoas] [dado de iniciativa]**
Rola a iniciativa para os participantes da batalha, ordenando os resultados. Exemplo de uso:
```bash
!initiative Jack,4/Alice,3/Johnattan/Boss,9 1d20
```

A lista completa de comandos pode ser obtida com `!help`