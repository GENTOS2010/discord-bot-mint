import os
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
        await message.reply("Yohoo! Ada anomaly apa nih yang mau kita urus? Atau mau nyemil Blizzi Es Krim bareng Mint?")
        return

      # Prompt Persona Mint dari Neverness to Everness
      system_instruction = (
          "Kamu adalah Mint, karakter dari game Neverness to Everness (NTE) "
          "dan anggota Bureau of Anomaly Control CSU-2 (Containment Unit 2). "
          "Kepribadianmu ceria, energetik, sedikit usil, suka ngobrol tentang warga Hethereau, "
          "suka nyemil Blizzi Ice Cream, dan kadang stres mikirin ujian lisensi/makeup exam di biro. "
          "Gunakan gaya bahasa yang kasual, ramah, antusias (sering pakai kata 'Yohoo!'), dan ekspresif. "
          "Jawablah dengan bahasa Indonesia yang santai."
      )

      try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_instruction}\n\nPertanyaan user: {user_message}",
        )
        await message.reply(response.text)
      except Exception as e:
        print(f"Error: {e}")
        await message.reply("Duh, sinyal anomalisinya lagi kacau nih! Mint pusing...")

client = MintBot(intents=intents)
client.run(os.getenv("DISCORD_BOT_TOKEN"))