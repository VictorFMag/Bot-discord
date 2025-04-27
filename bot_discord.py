import discord
from discord.ext import commands
import yt_dlp
import asyncio
from dice_roller import calculate_dice_expression, roll_with_advantage_or_disadvantage, calculate_initiative
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Acessar o token do Discord
TOKEN =  os.getenv("TOKEN")

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
        total_result, rolls = calculate_dice_expression(dice_expression)
        formatted_results = "\n".join(map(str, rolls))
        
        await ctx.send(f"🎲 Rolando **{dice_expression}**:\n{formatted_results}\n(Total: **{total_result}**)")

    except Exception as e:
        await ctx.send(f"❗ Ocorreu um erro: {e}.")

@bot.command()
async def rollv(ctx, *, dice_expression: str):
    try:
        results = roll_with_advantage_or_disadvantage(dice_expression, advantage=False)
        await ctx.send(f"🎲 Rolando **{dice_expression}** com desvantagem:\n(Valor final: **{results.final_result}**)")

    except Exception as e:
        await ctx.send(f"❗ Ocorreu um erro: {e}.")

@bot.command()
async def rolld(ctx, *, dice_expression: str):
    try:
        results = roll_with_advantage_or_disadvantage(dice_expression, advantage=False)
        await ctx.send(f"🎲 Rolando **{dice_expression}** com desvantagem:\n(Valor final: **{results.final_result}**)")
        
    except Exception as e:
        await ctx.send(f"❗ Ocorreu um erro: {e}.")


@bot.command()
async def initiative(ctx, *, people_list: str, initiative_dice_expression: str = "1d20"):
    """
    Rola várias quantidades de dados de diferentes lados e realiza operações matemáticas.
    Exemplo de uso: !roll 1d8 - 3d6 + 5 - 4
    """
    try:
        initiatives = calculate_initiative(people_list, initiative_dice_expression)
        formatted_results = "\n".join([f"{name}: {total_initiative}" for name, total_initiative in initiatives])

        await ctx.send(f"🎲 Iniciativas calculadas:\n{formatted_results}")
    except Exception as e:
        await ctx.send(f"❗ Ocorreu um erro: {e}. Use o formato correto, por exemplo: `!roll 1d8 - 3d6 + 5 - 4`")

@bot.command()
async def help(ctx):
    """Comando para mostrar a lista de comandos disponíveis."""
    help_text = (
        "**Aqui estão os comandos disponíveis:**\n"
        "\n🔹 **!help** -> Mostra esta lista de comandos."
        "\n🔹 **!roll XdY** -> Rola X dados de Y lados. Também aceita uma expressão, ex.: 3d8 + 3, 5d6 + 6d4..."
        "\n🔹 **!rollv XdY** -> Rola com vantagem. Também aceita uma expressão, ex.: 3d8 + 3, 5d6 + 6d4..."
        "\n🔹 **!rolld XdY** -> Rola com desvantagem. Também aceita uma expressão, ex.: 3d8 + 3, 5d6 + 6d4..."
        "\n🔹 **!play <link_do_Youtube>** -> Toco uma música do Youtube."
        "\n🔹 **!stop** -> Paro a música do Youtube."
        "\n🔹 **!loop** -> Ativo/desativo o modo de repetição da música do Youtube."
    )
    await ctx.send(help_text)


bot.run(TOKEN)
