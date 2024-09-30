from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from pytube import YouTube
import os

# Masukkan API Key bot Anda di sini
BOT_API_KEY = '7656527709:AAEDaSgfU2fXoc7aZ_Y6R219LK6QNd_ycrI'
DOWNLOAD_PATH = './downloads'  # Path untuk menyimpan video

# Buat folder download jika belum ada
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Fungsi untuk memulai bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Halo! Kirimkan link YouTube yang ingin Anda download, dan saya akan menyediakan pilihan resolusi untuk Anda.'
    )

# Fungsi untuk menangani link YouTube yang dikirimkan oleh user
def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if 'youtube.com' not in url and 'youtu.be' not in url:
        update.message.reply_text('Harap kirimkan link YouTube yang valid.')
        return
    
    try:
        # Mengambil informasi video
        yt = YouTube(url)
        keyboard = [
            [InlineKeyboardButton("360p", callback_data=f"360p|{url}"),
             InlineKeyboardButton("480p", callback_data=f"480p|{url}"),
             InlineKeyboardButton("720p", callback_data=f"720p|{url}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            f'Pilih resolusi untuk video: {yt.title}',
            reply_markup=reply_markup
        )
    except Exception as e:
        update.message.reply_text(f'Terjadi kesalahan: {e}')

# Fungsi untuk menangani pilihan resolusi dari user
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    # Mendapatkan resolusi dan url dari data callback
    resolution, url = query.data.split('|')
    
    try:
        # Mengunduh video dengan resolusi yang dipilih
        yt = YouTube(url)
        stream = yt.streams.filter(res=resolution, progressive=True, file_extension='mp4').first()
        if not stream:
            query.edit_message_text(text=f'Resolusi {resolution} tidak tersedia untuk video ini.')
            return

        query.edit_message_text(text=f'Mengunduh video dengan resolusi {resolution}...')

        # Mengunduh video ke folder yang ditentukan
        file_path = stream.download(output_path=DOWNLOAD_PATH)
        file_name = os.path.basename(file_path)

        # Kirim video ke chat setelah berhasil di-download
        query.message.reply_video(video=open(file_path, 'rb'), caption=f"Video berhasil diunduh: {yt.title}")
        
        # Menghapus file setelah dikirim
        os.remove(file_path)
    except Exception as e:
        query.edit_message_text(text=f'Terjadi kesalahan saat mengunduh video: {e}')

# Fungsi untuk menangani error
def error(update: Update, context: CallbackContext) -> None:
    print(f'Update "{update}" menyebabkan error "{context.error}"')

# Fungsi utama untuk menjalankan bot
def main() -> None:
    # Membuat updater dan dispatcher
    updater = Updater(BOT_API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    # Handler untuk command /start
    dispatcher.add_handler(CommandHandler('start', start))

    # Handler untuk pesan text (link YouTube)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Handler untuk tombol pilihan resolusi
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Handler untuk menangani error
    dispatcher.add_error_handler(error)

    # Menjalankan bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
