import json
import os
import requests
import discord

# ==========================
# ตั้งค่า
# ==========================
TOKEN = "MTUyMjA1OTgzMTI1MzQwNTg1OA.Gfx6kv.eDy27swjzd-m81kb1Fx9pJH8CQPWtGSt6GyVeU"
GEMINI_API_KEY = "AIzaSyB8OD-iMTryzSxr4RCZIbCinTq5un6e4tM"
CHANNEL_ID = 1522049146054250587

MEM = "memory.json"

# ==========================
# Discord
# ==========================
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# ==========================
# Memory
# ==========================
def load():
    if os.path.exists(MEM):
        with open(MEM, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save(data):
    with open(MEM, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

memory = load()

# ==========================
# Gemini API
# ==========================
def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    r = requests.post(url, json=payload, timeout=60)

    if r.status_code != 200:
        raise Exception(r.text)

    data = r.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]

# ==========================
# Bot Ready
# ==========================
@bot.event
async def on_ready():
    print(f"✅ Login : {bot.user}")

# ==========================
# รับข้อความ
# ==========================
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    memory.append({
        "role": "user",
        "content": f"{message.author.display_name}: {message.content}"
    })

    memory[:] = memory[-40:]
    save(memory)

    history = ""

    for m in memory:
        if m["role"] == "user":
            history += "ผู้ใช้: " + m["content"] + "\n"
        else:
            history += "AI: " + m["content"] + "\n"

    prompt = f"""
คุณคือ AI ประจำห้อง Discord

ตอบเป็นภาษาไทย
จำบทสนทนาได้
ตอบสุภาพและเป็นธรรมชาติ

{history}
"""

    try:

        async with message.channel.typing():

            answer = ask_gemini(prompt)

            memory.append({
                "role": "assistant",
                "content": answer
            })

            memory[:] = memory[-40:]
            save(memory)

            if len(answer) <= 2000:
                await message.channel.send(answer)
            else:
                for i in range(0, len(answer), 1900):
                    await message.channel.send(answer[i:i+1900])

    except Exception as e:
        await message.channel.send(f"❌ Error\n```{e}```")

bot.run(TOKEN)