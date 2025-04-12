import os
import logging
import subprocess
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)

# Gunakan token dari environment variable
TOKEN = os.getenv("BOT_TOKEN")

LINK, RESOLUTION, DURATION = range(3)

main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("Mulai Rekaman")],
    [KeyboardButton("Bantuan")]
], resize_keyboard=True)

res_keyboard = ReplyKeyboardMarkup([
    ["240p", "360p"],
    ["480p", "720p"],
    ["1080p"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name or "pengguna"
    await update.message.reply_text(
        f"Hi {username}! Selamat datang di bot rekaman.\nPilih opsi di bawah.",
        reply_markup=main_keyboard
    )
    return ConversationHandler.END

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg = (
        "Cara menggunakan bot ini:\n\n"
        "1. Tekan 'Mulai Rekaman'.\n"
        "2. Masukkan link RTMP dari MX Player.\n"
        "3. Pilih resolusi video (240p - 1080p).\n"
        "4. Masukkan durasi rekaman (dalam menit).\n\n"
        "Bot akan memproses rekaman dan mengirim hasilnya ke sini."
    )
    await update.message.reply_text(help_msg)
    return ConversationHandler.END

async def mulai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Silakan kirimkan link RTMP dari MX Player.")
    return LINK

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link"] = update.message.text
    await update.message.reply_text("Pilih resolusi video:", reply_markup=res_keyboard)
    return RESOLUTION

async def get_resolution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resolution_map = {
        "240p": "400k",
        "360p": "800k",
        "480p": "1M",
        "720p": "2M",
        "1080p": "3M"
    }
    res = update.message.text
    if res not in resolution_map:
        await update.message.reply_text("Resolusi tidak valid. Pilih dari tombol yang tersedia.")
        return RESOLUTION
    context.user_data["bitrate"] = resolution_map[res]
    await update.message.reply_text("Masukkan durasi rekaman dalam menit:")
    return DURATION

async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        durasi_menit = int(update.message.text)
        durasi_detik = durasi_menit * 60
        context.user_data["duration"] = durasi_detik
    except ValueError:
        await update.message.reply_text("Durasi tidak valid. Harap masukkan angka.")
        return DURATION

    link = context.user_data["link"]
    bitrate = context.user_data["bitrate"]
    duration = context.user_data["duration"]

    await update.message.reply_text("Memulai rekaman, mohon tunggu...")

    try:
        command = [
            "ffmpeg",
            "-y",
            "-i", link,
            "-t", f"{duration}",
            "-c:v", "libx264",
            "-b:v", bitrate,
            "-c:a", "aac",
            "-strict", "experimental",
            "output.mp4"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Link bermasalah")
        with open("output.mp4", "rb") as video:
            await update.message.reply_video(video)
        os.remove("output.mp4")
    except Exception:
        await update.message.reply_text("Host sedang tidak aktif atau link bermasalah.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dibatalkan.")
    return ConversationHandler.END

def main():
    import nest_asyncio
    nest_asyncio.apply()

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Mulai Rekaman$"), mulai)],
        states={
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
            RESOLUTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_resolution)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Bantuan$"), bantuan))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
