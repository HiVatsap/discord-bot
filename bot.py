import asyncio
import os
import discord
from dotenv import load_dotenv

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

is_paused = False

hello_variants = ("привет",
                  "привіт",
                  "ahoj",
                  "cs",
                  "labas",
                  "здравствуйте",
                  "добрий день",
                  "добрый день",
                  "доброго дня",
                  "охайо",
                  "hallo",
                  "hello",
                  "hi",
                  "labukas",
                  "čau",
                  "sveiki",
                  "здравейте",
                  "охайошечки даттебаёшечки",
                  "дарова",
                  "hej",
                  "こんにちは",
                  "你好",
                  "nǐ hǎo",
                  "hola",
                  "ciao",
                  "udvozlet",
                  "здарова",
                  "salut",
                  "salutations",
                  "labuka",
                  "sveikas",
                  "hey",
                  "ni hao",
                  "konnichiwa",
                  "konbanwa",
                  "ohayo",
                  "шалом",
                  "שלום",
                  "салом",
                  "cau",
                  "مرحبًا",
                  "салам",
                  "салям",
                  "салом",
                  "гамарджоба",
                  "ку",
                  "саламдашуулар",
                  "สวัสดี",
                  "สวัสดีครับ",
                  "สวัสดีค่ะ",
                  "czesc",
                  "cześć",
                  "siema",
                  "elo żelo",
                  "elo",
                  "прывітанні",
                  "поздрави",
                  "маршалла хаттар",
                  "bună",
                  "гой еси"
                  )


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
                        print("ЛОГ: Имя канала 1 было обновлено")
                    except discord.HTTPException as e:
                        print(f"ОШИБКА: Имя канала 1 не было обновлено из-за лимита Дискорда ({e})")

            if channel2 and role2:
                count = len(role2.members)
                new_name = f"Гостей: {count}"

                if channel2.name != new_name:
                    try:
                        await channel2.edit(name=new_name)
                        print("ЛОГ: Имя канала 2 было обновлено")
                    except discord.HTTPException as e:
                        print(f"ОШИБКА: Имя канала 2 не было обновлено из-за лимита Дискорда ({e})")

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
    print(f'Я {client.user.name}, и я поздравляю тебя с победой!')

    client.loop.create_task(update_stats_channels())

    channel = client.get_channel(CONSOLE_CHANNEL_ID)
    if channel:
        await channel.send("**Бот запущен! (:white_check_mark:) ** \n"
                           "Щас буду побеждать, ведь я **А6**! " + "<:alhamdulilah:1542234162759475240>" * 3)
    else:
        print("ОШИБКА: Не найден путь к консоли бота, проверьте CONSOLE_CHANNEL_ID")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global is_paused

    if message.content.lower() in ("a6!continue", "а6!continue"):
        if not message.author.guild_permissions.administrator:
            await message.channel.send("🔴 !!! У вас нет права на использование данной команды !!! 🔴")
            return

        if not is_paused:
            await message.channel.send("**Бот уже работает!** :white_check_mark:")
            return

        is_paused = False

        await client.change_presence(status=discord.Status.online, activity=discord.Game(name="Играет Nebulabrasque"))

        console_channel = message.guild.get_channel(CONSOLE_CHANNEL_ID)
        if console_channel:
            await console_channel.send("✅ Бот возобновил работу! ✅")
        else:
            print("ОШИБКА: Не найден путь к консоли бота, проверьте CONSOLE_CHANNEL_ID")
        print(f"Бот возобновил работу!")

        return

    if is_paused:
        return

    if message.content.lower() in ("a6!pause", "а6!pause"):
        if not message.author.guild_permissions.administrator:
            await message.channel.send("🔴 !!! У вас нет права на использование данной команды !!! 🔴")
            return

        if is_paused:
            return

        is_paused = True

        await client.change_presence(
            status=discord.Status.dnd, activity=discord.Game(name="Бот приостановлен")
        )

        console_channel = message.guild.get_channel(CONSOLE_CHANNEL_ID)
        if console_channel:
            await console_channel.send(":warning: **Бот был приостановлен** :warning:")
        else:
            print("ОШИБКА: Не найден путь к консоли бота, проверьте CONSOLE_CHANNEL_ID")
        print(f"Бот приостановлен игроком {message.author}!")

        return

    if message.content.lower() in hello_variants:
        await message.channel.send(f"{message.content.capitalize()}, {message.author.mention}!")
    if message.content.lower() in ("ас-саляму алейкум", "السَّلَامُ عَلَيْكُمْ", "ассаляму алейкум"):
        await message.channel.send(f"Ваалейкум ассалям, {message.author.mention}!")


async def shutdown():
    print("Отключение бота...")
    async with discord.Client(intents=intents) as temp_client:

        @temp_client.event
        async def on_ready():
            try:
                channel = temp_client.get_channel(CONSOLE_CHANNEL_ID)
                if not channel:
                    channel = await temp_client.fetch_channel(CONSOLE_CHANNEL_ID)

                await channel.send("Бот отключается! (🏮)")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"ОШИБКА: При отправке сообщения получана ошибка ({e})")
            finally:
                await temp_client.close()

        try:
            await temp_client.start(TOKEN)
        except Exception:
            pass


async def main():
    async with client:
        await client.start(TOKEN)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Перехвачен приказ о завершении программы!")
        try:
            asyncio.run(shutdown())
        except Exception:
            pass