import asyncio
import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

CONSOLE_CHANNEL_ID = 1568958721428815912
COUNT_CHANNEL_1_ID = 1558849614369521826
COUNT_CHANNEL_2_ID = 1558850421613797517
ROLE_1_ID = 1525602964968833257
ROLE_2_ID = 1479964252675768432

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
                  "namaste",
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
async def on_ready():
    print(f'Я {client.user.name}, и я поздравляю тебя с победой!')

    client.loop.create_task(update_stats_channels())

    channel = client.get_channel(CONSOLE_CHANNEL_ID)
    if channel:
        await channel.send("**Бот запущен! (:white_check_mark:) ** \n"
                           "Щас буду побеждать, ведь я **А6**! " + "<:alhamdulilah:1542234162759475240>" * 3)
    else:
        print("ОШИБКА: Не найден путь к консоли бота, проверьте CHANNEL_ID")


@client.event
async def on_message(message):
    if message.author == client.user:
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