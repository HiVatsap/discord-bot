import asyncio
import datetime
import os
from zoneinfo import ZoneInfo

import discord
from dotenv import load_dotenv

from config import hello_variants, save_words
from light import light
from logger import logger


load_dotenv()

is_tested = os.getenv("IS_TESTED", "false").lower() == "true"
TOKEN = (os.getenv("DISCORD_TOKEN_TEST") if is_tested else os.getenv("DISCORD_TOKEN"))


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

TARGET_USER_ID = 849706753587150920


GREEN_COLOR = 0x29ff00
RED_COLOR = 0xdb0000
ORANGE_COLOR = 0xdb7200
YELLOW_COLOR = None

is_paused = False


async def update_stats_channels() -> None:
    """Updates the member count for a role using private voice channels."""
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
async def on_voice_state_update(
        member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
) -> None:
    """Logs members joining and leaving voice channels, excluding the secret channel."""
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
async def on_ready() -> None:
    """Prints a startup notification to the console and runs update_stats_channel() in the background."""
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
async def on_message(message: discord.Message) -> None:
    """Starts processing text commands and displays a welcome message."""
    if message.author == client.user:
        return

    global is_paused

    console_channel = message.guild.get_channel(CONSOLE_CHANNEL_ID)
    content_lower = message.content.lower()

    target_nickname = message.author.guild.get_member(TARGET_USER_ID).nick

    if content_lower in ("a6!stop", "а6!stop"):
        await stop(message)

    if content_lower in ("a6!help", "а6!help"):
        await send_help(message, target_nickname)
        return

    if content_lower in ("a6!continue", "а6!continue"):
        await get_continue(message, console_channel)
        return

    if is_paused:
        return

    if content_lower in ("a6!light", "а6!light"):
        await get_light(message, target_nickname)
        return

    if content_lower.startswith(("a6!addhello", "а6!addhello")):
        await add_hello(message)
        return

    if content_lower.startswith(("a6!removehello", "а6!removehello")):
        await remove_hello(message)
        return

    if content_lower in ("a6!version", "а6!version"):
        await version(message)
        return

    if content_lower in ("a6!pause", "а6!pause"):
        await pause(message, console_channel)
        return

    sorted_variants = sorted(hello_variants, key=len, reverse=True)
    matched_variant = None

    for variant in sorted_variants:
        if content_lower.startswith(variant.lower()):
            matched_variant = variant
            break

    if matched_variant:
        if matched_variant in ("ас-саляму алейкум", "السَّلَامُ عَلَيْكُمْ", "ассаляму алейкум"):
            await message.channel.send(f"Ваалейкум ассалям, {message.author.mention}!")
        else:
            await message.channel.send(f"{matched_variant.capitalize()}, {message.author.mention}!")


async def stop(message: discord.Message) -> None:
    """Shuts down the bot with a console notification if the user has administrator permissions."""
    if not message.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="!!! У вас нет права на использование данной команды !!!",
            color=RED_COLOR
        )
        await message.channel.send(embed=embed)
        return

    logger.info("Администратор вызвал экстренное завершение программы!")
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

    await client.close()


async def send_help(message: discord.Message, target_nickname: str) -> None:
    embed1 = discord.Embed(
        title="Стандартные команды",
        description=(
            "`a6!addhello [слово]` - добавляет слово в список приветствий\n"
            "`a6!help` - выводит список команд\n"
            "`a6!removehello [слово]` - убирает слово из списка приветствий\n"
            "`a6!version` - показывает информацию о версии бота\n"
            f"`a6!light` - показывает график отключения света у {target_nickname}\n"
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
            "`a6!stop` - экстренная остановка бота\n"
        ),
        color=0xe44b10
    )
    await message.channel.send(embed=embed2)


async def get_continue(message: discord.Message, console_channel: discord.TextChannel) -> None:
    """Resumes the bot's operation if it is paused"""
    global is_paused

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


async def get_light(message: discord.Message, target_nickname: str) -> None:
    """Retrieves the user's power outage schedule."""
    logger.info("Вызвана команда а6!light")

    now = datetime.datetime.now(ZoneInfo("Europe/Kyiv"))
    datetime_str = now.strftime("%H:%M")

    connect, light_intervals_str, light_status = light()
    if connect:
        if light_intervals_str is not None:
            if light_status is None:
                embed = discord.Embed(
                    title=f":warning:  График света для {target_nickname}  :warning:",
                    description=(
                        "**Ошибка!** Не удалось определить статус отключения!\n\n"
                        "**График отключений на сегодня:**\n"
                        f"{light_intervals_str}\n\n"
                        f"Сейчас: `{datetime_str}`"
                    ),
                    color=ORANGE_COLOR
                )
                await message.channel.send(embed=embed)

            elif light_status:
                embed = discord.Embed(
                    title=f":white_check_mark:  График света для {target_nickname}  :white_check_mark:",
                    description=(
                        "На данный момент свет **присутствует.**\n\n"
                        "**График отключений на сегодня:**\n"
                        f"{light_intervals_str}\n\n"
                        f"Сейчас: `{datetime_str}`"
                    ),
                    color=GREEN_COLOR
                )
                await message.channel.send(embed=embed)
                logger.info("Передано сообщение: Свет присутствует.")

            else:
                embed = discord.Embed(
                    title=f":red_circle:  График света для {target_nickname}  :red_circle:",
                    description=(
                        "На данный момент свет **отсутствует.**\n\n"
                        "**График отключений на сегодня:**\n"
                        f"{light_intervals_str}\n\n"
                        f"Сейчас: `{datetime_str}`"
                    ),
                    color=RED_COLOR
                )
                await message.channel.send(embed=embed)
                logger.info("Передано сообщение: Свет отсутствует.")

        else:
            embed = discord.Embed(
                title=f":white_check_mark:  График света для {target_nickname}  :white_check_mark:",
                description="График отключений на данный момент пуст!",
                color=GREEN_COLOR
            )
            await message.channel.send(embed=embed)

    else:
        embed = discord.Embed(
            title=f":warning:  График света для {target_nickname}  :warning:",
            description=(
                "Произошла непредвиденная ошибка, при попытке выполнения команды!\n"
                "Отчёт записан в лог!"
            ),
            color=ORANGE_COLOR
        )
        await message.channel.send(embed=embed)


async def add_hello(message: discord.Message) -> None:
    """Adds a new greeting to the list of greetings."""
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
        color=GREEN_COLOR
    )
    await message.channel.send(embed=embed)


async def remove_hello(message: discord.Message) -> None:
    """Removes a greeting from the list of greetings."""
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
        color=RED_COLOR
    )
    await message.channel.send(embed=embed)


async def version(message: discord.Message) -> None:
    """Displays the bot's version and a list of new features added in the latest release in Russian."""
    embed = discord.Embed(
        title="Я А6 и я поздравляю тебя с победой!",
        description=(
            "Версия бота: 1.5.5\n"
            "Выпущена: 13.11.2026\n\n"
            "Что нового:\n"
            "> - Добавлена команда а6!light\n"
            "> - Масштабные улучшения в структуре кода\n"
        ),
        color=0xcae6c7
    )

    await message.channel.send(embed=embed)


async def pause(message: discord.Message, console_channel: discord.TextChannel) -> None:
    """Pauses most bot interactions until it is resumed."""
    global is_paused

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


async def main() -> None:
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