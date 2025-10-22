import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import re

TOKEN = 'SEU_TOKEN_AQUI'

# Intents necessários para o bot funcionar corretamente
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Variável para armazenar o estado do loop
looping = False

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def join(ctx):
    """Comando para o bot entrar no canal de voz do usuário."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
    else:
        await ctx.send("Você precisa estar em um canal de voz para eu entrar!")

@bot.command()
async def leave(ctx):
    """Comando para o bot sair do canal de voz."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Não estou em nenhum canal de voz!")

@bot.command()
async def play(ctx, url):
    """Comando para tocar uma música a partir de um link do YouTube."""
    global looping

    if not ctx.voice_client:
        await ctx.invoke(join)

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        title = info['title']

    def after_playing(error):
        if error:
            print(f"Erro: {error}")
        if looping:
            asyncio.run_coroutine_threadsafe(play(ctx, url), bot.loop)


    ctx.voice_client.stop()  # Para qualquer áudio anterior antes de tocar outro
    ctx.voice_client.play(discord.FFmpegPCMAudio(url2), after=after_playing)

    await ctx.send(f"🎶 Tocando agora: **{title}**")

@bot.command()
async def stop(ctx):
    """Comando para parar a música."""
    global looping
    looping = False  # Desliga o loop ao parar a música

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Música parada.")
        await ctx.invoke(leave)
    else:
        await ctx.send("Não estou tocando nenhuma música no momento.")

@bot.command()
async def loop(ctx):
    """Comando para ativar o loop da música."""
    global looping

    looping = not looping
    await ctx.send(f"🔁 Loop {'ativado' if looping else 'desativado'}.")


@bot.command()
async def roll(ctx, *, dice_expression: str):
    """
    Rola várias quantidades de dados de diferentes lados e realiza operações matemáticas.
    Exemplo de uso: !roll 1d8 - 3d6 + 5 - 4
    """
    try:
        # Expressão regular para encontrar padrões do tipo XdY, números fixos e operadores
        pattern = re.compile(r'(\d+d\d+)|(\d+)|([+-])')
        matches = pattern.findall(dice_expression)
        
        total = 0
        results = []
        current_operator = '+'  # Começa com soma por padrão
        
        for match in matches:
            dice, fixed, operator = match
            
            if operator:
                # Atualiza o operador atual
                current_operator = operator
            
            elif dice:
                # Processa rolagens de dados
                amount, sides = map(int, dice.lower().split('d'))
                
                # Limita a quantidade e o número de lados para evitar abusos
                if amount <= 0 or sides <= 0:
                    await ctx.send("🚫 A quantidade e o número de lados devem ser maiores que zero.")
                    return
                if amount > 100:
                    await ctx.send("🚫 Não posso rolar mais de 100 dados de uma vez!")
                    return
                
                # Rola os dados e armazena os resultados
                dice_results = [random.randint(1, sides) for _ in range(amount)]
                sum_dice = sum(dice_results)
                
                # Aplica o operador atual
                if current_operator == '+':
                    total += sum_dice
                elif current_operator == '-':
                    total -= sum_dice
                
                results.append(f"**{dice}**: {', '.join(map(str, dice_results))}")
            
            elif fixed:
                # Processa valores fixos
                value = int(fixed)
                
                # Aplica o operador atual
                if current_operator == '+':
                    total += value
                elif current_operator == '-':
                    total -= value
                
                results.append(f"**{fixed}**")
        
        # Formata a mensagem com quebras de linha após cada rolagem
        formatted_results = "\n".join(results)
        
        # Mensagem de resposta com os resultados e o total
        await ctx.send(f"🎲 Rolando **{dice_expression}**:\n{formatted_results}\n(Total: **{total}**)")

    except Exception as e:
        await ctx.send(f"❗ Ocorreu um erro: {e}. Use o formato correto, por exemplo: `!roll 1d8 - 3d6 + 5 - 4`")

@bot.command()
async def help(ctx):
    """Comando para mostrar a lista de comandos disponíveis."""
    help_text = (
        "**Aqui estão os comandos disponíveis:**\n"
        "\n🔹 **!help** -> Mostra esta lista de comandos."
        "\n🔹 **!roll XdY** -> Rola X dados de Y lados."
        "\n🔹 **!play <link_do_Youtube>** -> Toco uma música do Youtube."
        "\n🔹 **!stop** -> Paro a música do Youtube."
        "\n🔹 **!loop** -> Ativo/desativo o modo de repetição da música do Youtube."
        "\n🔹 **!consultar_dnd** -> Busco alguma informação de D&D para os nerdolas de plantão. Digite (!help_command consultar_dnd para ver as opções de busca)"
    )
    await ctx.send(help_text)

def format_value(value, level=0):
    """
    Formata recursivamente valores de dicionários e listas para exibir no embed.
    Aplica capitalize em strings, adiciona quebra de linha extra para listas,
    remove chaves indesejadas e trata 'name' de forma especial.
    """
    indent = "  " * level
    remove_keys = {"updated_at", "url", "index"}

    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if k in remove_keys:
                continue  # pula chaves indesejadas
            # Se for name, mostra apenas o valor
            if k == "name":
                if isinstance(v, str):
                    lines.append(f"{indent}{v.capitalize()}")
                else:
                    lines.append(f"{indent}{str(v).capitalize()}")
            else:
                k_cap = str(k).capitalize()
                if isinstance(v, (dict, list)):
                    lines.append(f"{indent}{k_cap}:")
                    lines.append(format_value(v, level + 1))
                else:
                    v_cap = str(v).capitalize()
                    lines.append(f"{indent}{k_cap}: {v_cap}")
        return "\n".join(lines)
    elif isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(format_value(item, level))
            else:
                lines.append(f"{indent}- {str(item).capitalize()}")
        return "\n".join(lines) + "\n"
    else:
        return f"{indent}{str(value).capitalize()}"

@bot.command()
async def consultar_dnd(ctx, tipo: str, *, nome: str):
    """
    Comando para buscar informações na D&D 5e API. 
    Exemplo: !consultar_dnd spells Fireball 
    Opções de tipo: 
    - ability-scores: Pontuações de habilidade (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma). 
    - alignments: Alinhamentos de personagem (Leal/Bom, Caótico/Mau, etc.). 
    - backgrounds: Antecedentes de personagens (história, ocupação e habilidades iniciais). 
    - classes: Classes de personagem (Mago, Guerreiro, Clérigo, etc.). 
    - conditions: Condições que podem afetar personagens ou monstros (enfeitiçado, paralisado, etc.). 
    - damage-types: Tipos de dano (físico, mágico, cortante, perfurante, etc.). 
    - equipment: Equipamentos gerais (armas, armaduras, itens diversos). 
    - equipment-categories: Categorias de equipamentos (armas simples, armas marciais, etc.). 
    - feats: Talentos especiais que personagens podem adquirir. 
    - features: Habilidades de classes ou raças. 
    - languages: Idiomas existentes no mundo de D&D. 
    - magic-items: Itens mágicos. 
    - magic-schools: Escolas de magia (Abjuração, Conjuração, Necromancia, etc.). 
    - monsters: Monstros e criaturas. 
    - proficiencies: Proficiências de personagens (armas, ferramentas, perícias). 
    - races: Raças de personagem (Humano, Elfo, Anão, etc.). 
    - rule-sections: Seções das regras (partes do Livro do Jogador e guias de regras). 
    - rules: Regras específicas de D&D 5e. 
    - skills: Perícias de personagem (Furtividade, Atletismo, Arcanismo, etc.). 
    - spells: Magias. 
    - subclasses: Subclasses de classes (como Arqueiro Arcano, Guerreiro Eldritch Knight). 
    - subraces: Sub-raças (como Elfo Alto, Anão da Colina). 
    - traits: Traços de personagens ou monstros. 
    - weapon-properties: Propriedades de armas (leve, pesada, alcance, versátil, etc.). 
    """
    tipo = tipo.lower()
    nome_formatado = nome.lower().replace(" ", "-")
    url = f"https://www.dnd5eapi.co/api/{tipo}/{nome_formatado}"

    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    name = data.get("name", nome)
                    embed = discord.Embed(title=name, color=0x00ff00)

                    # Mostrar todas as chaves retornadas formatadas, ignorando updated_at e url
                    for key in data.keys():
                        if key in {"updated_at", "url", "index", "name"}:
                            continue
                        value = format_value(data[key])
                        # Limitar tamanho do valor para não quebrar embed
                        if len(value) > 1024:
                            value = value[:1020] + "..."
                        embed.add_field(name=str(key).capitalize(), value=value, inline=False)

                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❗ {tipo.capitalize()} '{nome}' não encontrado.")

@bot.command()
async def help_command(ctx, command_name: str):
    if command_name == "consultar_dnd":
        help_text = (
            "**Comando !consultar_dnd:**\n"
            "Busca informações na D&D 5e API.\n\n"
            "**Uso:** `!consultar_dnd <tipo> <nome>`\n\n"
            "**Tipos disponíveis:**\n"
            "- ability-scores: Pontuações de habilidade (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma).\n"
            "- alignments: Alinhamentos de personagem (Leal/Bom, Caótico/Mau, etc.).\n"
            "- backgrounds: Antecedentes de personagens (história, ocupação e habilidades iniciais).\n"
            "- classes: Classes de personagem (Mago, Guerreiro, Clérigo, etc.).\n"
            "- conditions: Condições que podem afetar personagens ou monstros (enfeitiçado, paralisado, etc.).\n"
            "- damage-types: Tipos de dano (físico, mágico, cortante, perfurante, etc.).\n"
            "- equipment: Equipamentos gerais (armas, armaduras, itens diversos).\n"
            "- equipment-categories: Categorias de equipamentos (armas simples, armas marciais, etc.).\n"
            "- feats: Talentos especiais que personagens podem adquirir.\n"
            "- features: Habilidades de classes ou raças.\n"
            "- languages: Idiomas existentes no mundo de D&D.\n"
            "- magic-items: Itens mágicos.\n"
            "- magic-schools: Escolas de magia (Abjuração, Conjuração, Necromancia, etc.).\n"
            "- monsters: Monstros e criaturas.\n"
            "- proficiencies: Proficiências de personagens (armas, ferramentas, perícias).\n"
        )
        ctx.send(help_text)
    else:
        ctx.send(f"❗ Comando de ajuda para '{command_name}' não encontrado.")

bot.run(TOKEN)
