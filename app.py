import os
import logging
import asyncio
import glob
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup log untuk memantau jika ada error
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token Bot Telegram Kamu
TOKEN = "8730634422:AAEIEV7qamz1OzRTUolh-cTmqimUz1TmfxM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo bro! Kirimkan link TikTok (video/slideshow foto), nanti langsung gw download-in.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "tiktok.com" not in url:
        await update.message.reply_text("Kirim link TikTok yang valid dong bro.")
        return

    status_msg = await update.message.reply_text("Sabar ya bro, lagi gw tarik datanya...")

    # Buat folder sementara untuk menampung hasil download
    os.makedirs("downloads", exist_ok=True)
    
    try:
        # Jalankan perintah gallery-dl lewat background mesin
        process = await asyncio.create_subprocess_exec(
            "gallery-dl", "-D", "downloads", url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        # Cari semua file yang berhasil didownload di dalam folder downloads
        files = glob.glob("downloads/*")
        
        if not files:
            await status_msg.edit_text("Gagal download nih bro, atau link tidak didukung.")
            return

        # Kirim balik semua file yang ketemu ke Telegram
        for file_path in files:
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        await update.message.reply_photo(photo=f)
                    else:
                        await update.message.reply_video(video=f)
                # Hapus file setelah dikirim agar server gak kepenuhan
                os.remove(file_path)
                
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("Aduh bro, ada error pas lagi download. Coba lagi nanti ya.")

def main():
    # Nyalakan bot Telegram
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Render butuh port web biar gak dianggap mati, kita akali dengan jalankan dummy web server jika diperlukan
    # Tapi untuk tipe polling sederhana, ini sudah cukup untuk awal pengujian
    print("Bot sudah stand-by...")
    app.run_polling()

if __name__ == '__main__':
    main()
