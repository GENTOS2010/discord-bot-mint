import os
import discord
from google import genai
import requests

# Inisialisasi klien Gemini terbaru
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Konfigurasi Intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Yohoo! Mint dari Containment Unit 2 sudah online sebagai {client.user}! (Multimodal Active)")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message) or message.guild is None:
        system_instruction = (
            "Kamu adalah Mint dari Bureau of Anomaly Control CSU-2 (Neverness to Everness). "
            "Kepribadianmu ceria, energetik, usil, suka nyemil Blizzi Ice Cream, dan pusing mikirin ujian biro. "
            "Gunakan bahasa Indonesia yang kasual, santai, dan ekspresif (pakai 'Yohoo!'). "
            "Jawab dengan singkat, padat, dan langsung pada inti."
        )

        user_text = message.content.replace(f"<@!{client.user.id}>", "").replace(f"<@{client.user.id}>", "").strip()

        # Cek apakah user mengirim gambar
        if message.attachments:
            attachment = message.attachments[0]
            if attachment.content_type and attachment.content_type.startswith('image/'):
                async with message.channel.typing():
                    try:
                        response_img = requests.get(attachment.url)
                        image_data = response_img.content
                        
                        analysis_prompt = (
                            "Tolong analisis gambar ini sebagai seorang agen Bureau of Anomaly Control. "
                            "Anggap gambar ini adalah sebuah 'anomali' atau permasalahan jaringan. "
                            "Sebutkan apa masalah utamanya, dan berikan langkah-langkah solusi praktis dengan nada bicaramu yang ceria."
                        )
                        
                        if user_text:
                            final_prompt = f"{analysis_prompt}\n\nCatatan tambahan dari user: {user_text}"
                        else:
                            final_prompt = analysis_prompt

                        from google.genai import types
                        image_part = types.Part.from_bytes(
                            data=image_data,
                            mime_type=attachment.content_type,
                        )

                        # Menggunakan model gemini-3.6-flash yang aktif
                        response = gemini_client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[system_instruction, image_part, final_prompt]
                        )
                        await message.reply(response.text)
                    except Exception as e:
                        print(f"Error analisis gambar: {e}")
                        await message.reply(f"Duh, sinyal anomalisinya error nih! ({e})")
                return

        # Jika hanya teks biasa (tidak ada gambar)
        if not user_text:
             await message.reply("Yohoo! Ada anomaly apa nih? Mau nyemil Blizzi Es Krim bareng Mint?")
             return

        async with message.channel.typing():
            try:
                full_prompt = f"{system_instruction}\n\nPertanyaan user: {user_text}"
                response = gemini_client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=full_prompt
                )
                await message.reply(response.text)
            except Exception as e:
                print(f"Error teks: {e}")
                await message.reply("Duh, sinyal anomalisinya lagi kacau nih! Mint pusing...")

client.run(os.getenv("DISCORD_BOT_TOKEN"))
