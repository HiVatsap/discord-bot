import asyncio
import os

import discord
from dotenv import load_dotenv

from config import hello_variants, save_words
from logger import logger

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

activity = discord.Game(name="Играет Nebulabrasque")

client = discord.Client(intents=intents, activity=activity)

CONSOLE_CHANNEL_ID = 1568958721428815912
COUNT_CHANNEL_1_ID = 1558849614369521826
COUNT_CHANNEL_2_ID = 1558850421613797517
VOICE_LOG_CHANNEL_ID = 1569332801029799946
IGNORED_VOICE_CHANNEL_ID = 1558465456451625161
ROLE_1_ID = 1525602964968833257
ROLE_2_ID = 1479964252675768432

GREEN_COLOR = 0x29ff00
RED_COLOR = 0xdb0000
ORANGE_COLOR = 0xdb7200
YELLOW_COLOR = None

is_paused = False


async def update_stats_channels():
    await client.wait_until_ready()

    while not client.is_closed():
        if is_paused:
            await asyncio.sleep(5)
            continue

        for guild in client.guilds:
            channel1 = guild.get_channel(COUNT_CHANNEL_1_ID)
            channel2 = guild.get_channel(COUNT_CHANNEL_2_ID)
            role1 = guild.get_role(ROLE_1_ID)
            role2 = guild.get_role(ROLE_2_ID)

            if channel1 and role1:
                count = len(role1.members)
                new_name = f"Потужных: {count}"

                if channel1.name != new_name:
                    try:
                        await channel1.edit(name=new_name)
                        logger.info("Имя канала 1 было обновлено")
                    except discord.HTTPException as e:
                        logger.warning(f"Имя канала 1 не было обновлено из-за лимита Дискорда ({e})")

            if channel2 and role2:
                count = len(role2.members)
                new_name = f"Гостей: {count}"

                if channel2.name != new_name:
                    try:
                        await channel2.edit(name=new_name)
                        logger.info("Имя канала 2 было обновлено")
                    except discord.HTTPException as e:
                        logger.warning(f"Имя канала 2 не было обновлено из-за лимита Дискорда ({e})")

        await asyncio.sleep(300)


@client.event
async def on_voice_state_update(member, before, after):
    # if member.bot:
    #    return

    if is_paused:
        return

    log_channel = member.guild.get_channel(VOICE_LOG_CHANNEL_ID)
    if not log_channel:
        return

    is_before_ignoring = before.channel and before.channel.id == IGNORED_VOICE_CHANNEL_ID
    is_after_ignoring = after.channel and after.channel.id == IGNORED_VOICE_CHANNEL_ID

    if is_before_ignoring and is_after_ignoring:
        return

    if is_before_ignoring and not is_after_ignoring:
        text = f":green_circle: **{member.display_name}** зашёл в голосовой канал **{after.channel.name}**"
        await log_channel.send(text)

    elif not is_before_ignoring and is_after_ignoring:
        text = f"🔴 **{member.display_name}** вышел из голосового канала **{before.channel.name}**"
        await log_channel.send(text)

    elif before.channel is None and after.channel is not None:
        text = f":green_circle: **{member.display_name}** зашёл в голосовой канал **{after.channel.name}**"
        await log_channel.send(text)

    elif before.channel is not None and after.channel is None:
        text = f"🔴 **{member.display_name}** вышел из голосового канала **{before.channel.name}**"
        await log_channel.send(text)

    elif before.channel != after.channel and before.channel and after.channel:
        text = f"🔁 **{member.display_name}** переместился из **{before.channel.name}** в **{after.channel.name}**"
        await log_channel.send(text)


@client.event
async def on_ready():
    logger.info(f'Я {client.user.name}, и я поздравляю тебя с победой!')

    client.loop.create_task(update_stats_channels())

    channel = client.get_channel(CONSOLE_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Бот запущен! (:white_check_mark:)",
            description="Щас буду побеждать, ведь я А6! :alhamdulilah::alhamdulilah::alhamdulilah:",
            color=GREEN_COLOR
        )
        await channel.send(embed=embed)
    else:
        logger.error("Не найден путь к консоли бота, проверьте CONSOLE_CHANNEL_ID")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global is_paused

    console_channel = message.guild.get_channel(CONSOLE_CHANNEL_ID)
    content_lower = message.content.lower()

    if content_lower in ("a6!help", "а6!help"):
        embed1 = discord.Embed(
            title="Стандартные команды",
            description=(
                "`a6!addhello [слово]` - добавляет слово в список приветствий\n"
                "`a6!help` - выводит список команд\n"
                "`a6!removehello [слово]` - убирает слово из списка приветствий\n"
                "`a6!version` - показывает информацию о версии бота\n"
            ),
            color=0x65b5ff
        )
        await message.channel.send(embed=embed1)

        if not message.author.guild_permissions.administrator:
            return

        embed2 = discord.Embed(
            title="Команды администратора",
            description=(
                "`a6!pause` - приостанавливает работу бота\n"
                "`a6!continue` - возобновляет работу бота\n"
            ),
            color=0xe44b10
        )
        await message.channel.send(embed=embed2)

        return

    if content_lower in ("a6!continue", "а6!continue"):
        if not message.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="!!! У вас нет права на использование данной команды !!!",
                color=RED_COLOR
            )
            await message.channel.send(embed=embed)
            return

        if not is_paused:
            embed = discord.Embed(
                title="**Бот уже работает!** :white_check_mark:",
                color=GREEN_COLOR
            )
            await message.channel.send(embed=embed)
            return

        is_paused = False

        await client.change_presence(status=discord.Status.online, activity=discord.Game(name="Играет Nebulabrasque"))

        if console_channel:
            embed = discord.Embed(
                title="✅ Бот возобновил работу! ✅",
                color=GREEN_COLOR
            )
            await console_channel.send(embed=embed)
        else:
            logger.error("Не найден путь к консоли бота, проверьте CONSOLE_CHANNEL_ID")
        logger.info(f"Бот возобновил работу!")

        return

    if is_paused:
        return

    if content_lower.startswith(("a6!addhello", "а6!addhello")):
        parts = message.content.split(maxsplit=1)
        if len(parts) < 2:
            embed = discord.Embed(
                title=":warning: Укажите слово, которое хотите вставить! :warning:",
                description="> *Например: a6!addhello ку*",
                color=ORANGE_COLOR
            )
            await message.channel.send(embed=embed)
            return
        new_word = parts[1].strip().lower()

        if new_word in hello_variants:
            embed = discord.Embed(
                title=f'⚠️ Слово "{new_word}" уже есть в списке приветствий ⚠️',
                color=ORANGE_COLOR
            )
            await message.channel.send(embed=embed)
            return

        hello_variants.append(new_word)
        save_words(hello_variants)

        embed = discord.Embed(
            title=f'ℹ️  Слово "{new_word}" добавлено в список приветствий  ℹ️',
            color=0x1098d8
        )
        await message.channel.send(embed=embed)
        return

    if content_lower.startswith(("a6!removehello", "а6!removehello")):
        parts = message.content.split(maxsplit=1)
        if len(parts) < 2:
            embed = discord.Embed(
                title=":warning: Укажите слово, которое хотите убрать! :warning:",
                description="> *Например: a6!removehello йолоп*",
                color=ORANGE_COLOR
            )
            await message.channel.send(embed=embed)
            return
        word = parts[1].strip().lower()

        if word not in hello_variants:
            embed = discord.Embed(
                title=f'⚠️ Слово "{word}" не находится в списке приветствий ⚠️',
                color=ORANGE_COLOR
            )
            await message.channel.send(embed=embed)
            return

        hello_variants.remove(word)
        save_words(hello_variants)

        embed = discord.Embed(
            title=f'ℹ️  Слово "{word}" удалено из списка приветствий  ℹ️',
            color=0x1098d8
        )
        await message.channel.send(embed=embed)
        return

    if content_lower in ("a6!version", "а6!version"):
        embed = discord.Embed(
            title="Я А6 и я поздравляю тебя с победой!",
            description=(
                "Версия бота: 1.4.0\n"
                "Выпущена: 10.11.2026\n\n"
                "Что нового:\n"
                "> - Добавлена команда а6!addhello\n"
                "> - Добавлена команда а6!removehello\n"
                "> - Добавлена команда а6!help\n"
                "> - Добавлена команда а6!version\n"
                "> - Багфиксы и улучшение структуры кода\n"
            ),
            color=0xcae6c7
        )

        await message.channel.send(embed=embed)
        return

    if content_lower in ("a6!pause", "а6!pause"):
        if not message.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="!!! У вас нет права на использование данной команды !!!",
                color=RED_COLOR
            )
            await message.channel.send(embed=embed)
            return

        if is_paused:
            return

        is_paused = True

        await client.change_presence(
            status=discord.Status.dnd, activity=discord.Game(name="Бот приостановлен")
        )

        if console_channel:
            embed = discord.Embed(
                title=":warning: **Бот был приостановлен** :warning:",
                color=0xdbb800
            )
            await console_channel.send(embed=embed)
        else:
            logger.error("Не найден путь к консоли бота, проверьте CONSOLE_CHANNEL_ID")
        logger.info(f"Бот приостановлен игроком {message.author}!")

        return

    if content_lower in hello_variants:
        await message.channel.send(f"{content_lower.capitalize()}, {message.author.mention}!")
    if content_lower in ("ас-саляму алейкум", "السَّلَامُ عَلَيْكُمْ", "ассаляму алейкум"):
        await message.channel.send(f"Ваалейкум ассалям, {message.author.mention}!")


async def main():
    async with client:
        try:
            await client.start(TOKEN)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Отключение бота...")

            console_channel = client.get_channel(CONSOLE_CHANNEL_ID)
            if console_channel:
                try:
                    embed = discord.Embed(
                        title="Бот отключается! (🏮)",
                        color=RED_COLOR
                    )
                    await console_channel.send(embed=embed)
                    logger.info("Доставлено сообщение о отключении!")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.warning(f"При отправке сообщения получена ошибка ({e})")

            raise


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот отключен!")