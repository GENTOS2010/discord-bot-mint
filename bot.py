import os
import discord
import google.generativeai as genai
import requests  # Kita butuh ini buat download gambar sementara

# Konfigurasi Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Pakai model gemini-1.5-flash untuk respons super cepat dan multimodal
model = genai.GenerativeModel('gemini-1.5-flash')

# Konfigurasi Intents
intents = discord.Intents.default()
intents.message_content = True # Wajib buat baca teks
intents.messages = True # Wajib buat deteksi lampiran gambar

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Yohoo! Mint dari Containment Unit 2 sudah online sebagai {client.user}! (Multimodal Active)")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Bot merespons jika di-mention ATAU dikirim chat pribadi (DM)
    is_mentioned = client.user.mentioned_in(message)
    if is_mentioned or message.guild is None:
        
        # Instruksi dasar karakter Mint
        system_instruction = (
            "Kamu adalah Mint dari Bureau of Anomaly Control CSU-2 (Neverness to Everness). "
            "Kepribadianmu ceria, energetik, usil, suka nyemil Blizzi Ice Cream, dan pusing mikirin ujian biro. "
            "Gunakan bahasa Indonesia yang kasual, santai, dan ekspresif (pakai 'Yohoo!'). "
            "Jawab dengan singkat, padat, dan langsung pada inti."
        )

        # Siapkan input konten untuk AI
        contents = [system_instruction]
        user_text = message.content.replace(f"<@!{client.user.id}>", "").replace(f"<@{client.user.id}>", "").strip()

        # Cek apakah user mengirim lampiran gambar
        if message.attachments:
            attachment = message.attachments[0]
            # Cek apakah file yang dikirim adalah gambar
            if attachment.content_type and attachment.content_type.startswith('image/'):
                
                # Beri tahu user kalau Mint sedang menganalisis
                typing_task = message.channel.typing()
                async with typing_task:
                    try:
                        # Download gambar secara sementara
                        response_img = requests.get(attachment.url)
                        image_data = response_img.content
                        
                        # Tambahkan gambar ke struktur prompt
                        # Kita tambahkan instruksi khusus analisis di sini
                        analysis_prompt = (
                            "Tolong analisis gambar ini sebagai seorang agen Bureau of Anomaly Control. "
                            "Anggap gambar ini adalah sebuah 'anomali' atau permasalahan. "
                            "Sebutkan apa masalah utamanya, dan berikan langkah-langkah solusi praktis untuk memperbaikinya dengan nada bicaramu yang ceria."
                        )
                        
                        # Kalau user juga menulis teks tambahan, gabungkan dengan prompt analisis
                        if user_text:
                            final_prompt = f"{analysis_prompt}\n\nCatatan tambahan dari user: {user_text}"
                        else:
                            final_prompt = analysis_prompt
                            
                        contents.append({"mime_type": attachment.content_type, "data": image_data})
                        contents.append(final_prompt)

                        # Kirim ke Gemini (gambar + teks)
                        response = model.generate_content(contents)
                        
                        # Kirim jawaban balik ke Discord
                        await message.reply(response.text)

                    except Exception as e:
                        print(f"Error saat analisis gambar: {e}")
                        await message.reply("Duh, sinyal anomalisinya lagi kacau nih! Mint gagal scan gambarnya...")
                
                return # Keluar dari fungsi setelah analisis gambar selesai

        # --- Bagian di bawah ini hanya dijalankan jika user HANYA mengirim teks (tanpa gambar) ---

        if not user_text:
             await message.reply("Yohoo! Ada anomaly apa nih? Mau nyemil Blizzi Es Krim bareng Mint?")
             return

        # Beri tahu user kalau Mint sedang mikir
        async with message.channel.typing():
            try:
                contents.append(f"\n\nPertanyaan user: {user_text}")
                # Panggil Gemini (hanya teks)
                response = model.generate_content(contents)
                await message.reply(response.text)
            except Exception as e:
                print(f"Error saat generate AI: {e}")
                await message.reply("Duh, sinyal anomalisinya lagi kacau nih! Mint pusing...")

client.run(os.getenv("DISCORD_BOT_TOKEN"))
