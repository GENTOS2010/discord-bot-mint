import os
import discord
from google import genai

# Inisialisasi klien Gemini dengan API Key dari Environment Variable
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Konfigurasi Discord Intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Yohoo! Mint dari Containment Unit 2 sudah online sebagai {client.user}!")

@client.event
async def on_message(message):
    # Abaikan pesan dari bot sendiri agar tidak looping
    if message.author == client.user:
        return

    # Bot merespons jika di-mention atau dikirim chat pribadi (DM)
    if client.user.mentioned_in(message) or message.guild is None:
        # Bersihkan mention dari text prompt
        user_message = message.content.replace(f"<@!{client.user.id}>", "").replace(f"<@{client.user.id}>", "").strip()
        
        if not user_message:
            await message.reply("Yohoo! Ada anomaly apa nih? Mau nyemil Blizzi Es Krim bareng Mint?")
            return

        system_instruction = (
            "Kamu adalah Mint dari Bureau of Anomaly Control CSU-2 (Neverness to Everness). "
            "Kepribadianmu ceria, energetik, usil, suka nyemil Blizzi Ice Cream, dan pusing mikirin ujian biro. "
            "Gunakan bahasa Indonesia yang kasual, santai, dan ekspresif (pakai 'Yohoo!'). "
            "Jawab dengan singkat, padat, dan langsung pada inti."
        )

        try:
            # Panggil Gemini API secara langsung
            response = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"{system_instruction}\n\nPertanyaan user: {user_message}",
            )
            await message.reply(response.text)
        except Exception as e:
            print(f"Error saat generate AI: {e}")
            await message.reply("Duh, sinyal anomalisinya lagi kacau nih! Mint pusing...")

client.run(os.getenv("DISCORD_BOT_TOKEN"))
