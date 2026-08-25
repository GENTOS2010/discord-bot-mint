import os
import asyncio
import discord
from google import genai

# Inisialisasi klien Gemini dengan API Key dari Environment Variable
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Konfigurasi Discord Intents
intents = discord.Intents.default()
intents.message_content = True

class MintBot(discord.Client):

  async def on_ready(self):
    print(f"Yohoo! Mint dari Containment Unit 2 sudah online sebagai {self.user}!")

  async def on_message(self, message):
    if message.author == self.user:
      return

    # Bot merespons jika di-mention atau dikirim chat pribadi (DM)
    if self.user.mentioned_in(message) or message.guild is None:
      # Bersihkan mention dari text prompt
      user_message = message.content.replace(f"<@!{self.user.id}>", "").replace(f"<@{self.user.id}>", "").strip()
      
      if not user_message:
        await message.reply("Yohoo! Ada anomaly apa nih? Mau nyemil Blizzi Es Krim bareng Mint?")
        return

      # Tampilkan indikator 'typing' biar user tahu bot sedang memproses
      async with message.channel.typing():
        system_instruction = (
            "Kamu adalah Mint dari Bureau of Anomaly Control CSU-2 (Neverness to Everness). "
            "Kepribadianmu ceria, energetik, usil, suka nyemil Blizzi Ice Cream, dan pusing mikirin ujian biro. "
            "Gunakan bahasa Indonesia yang kasual, santai, dan ekspresif (pakai 'Yohoo!'). "
            "Jawab dengan singkat, padat, dan langsung pada inti."
        )

        try:
          # Bungkus dengan asyncio.wait_for agar kalau API lama/hang, tidak diam selamanya
          loop = asyncio.get_running_loop()
          response = await asyncio.wait_for(
              loop.run_in_executor(
                  None, 
                  lambda: gemini_client.models.generate_content(
                      model="gemini-3.6-flash",
                      contents=f"{system_instruction}\n\nPertanyaan user: {user_message}",
                  )
              ),
              timeout=10.0 # Batas waktu maksimal 10 detik
          )
          await message.reply(response.text)
          
        except asyncio.TimeoutError:
          await message.reply("Duh, koneksi ke biro lagi lemot banget! Coba ulangin lagi ya, hehee...")
        except Exception as e:
          print(f"Error: {e}")
          await message.reply("Duh, sinyal anomalisinya lagi kacau nih! Mint pusing...")

client = MintBot(intents=intents)
client.run(os.getenv("DISCORD_BOT_TOKEN"))
