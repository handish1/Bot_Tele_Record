import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

# Ambil token dari environment variable di Replit
TOKEN = os.environ.get("BOT_TOKEN")

# Handler untuk perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Bot kamu berhasil dijalankan di Replit.")

# Handler untuk perintah /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Perintah yang tersedia:\n/start - Mulai bot\n/help - Bantuan")

# Fungsi utama
if __name__ == '__main__':
    keep_alive()  # Menjaga Replit tetap hidup dengan server Flask

    # Bangun aplikasi bot Telegram
    app = ApplicationBuilder().token(TOKEN).build()

    # Tambahkan handler ke aplikasi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot berjalan di Replit...")

    # Jalankan polling bot
    app.run_polling()
