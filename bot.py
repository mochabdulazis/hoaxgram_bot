import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CommandHandler

BOT_TOKEN = "8722777173:AAGtcCTsBIrIzVzbWNFsUGbmv4AQlJWTSVw"
API_URL = "https://web-production-a5b24.up.railway.app/predict"

print("Bot started...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        response = requests.post(API_URL, json={"text": text})
        result = response.json()

        label = result["label"]
        score = result["score"]

        confidence = score * 100

        if label == "hoax":
            status = "⚠️ TERINDIKASI HOAKS"
            explanation = "Konten memiliki pola yang sering ditemukan pada informasi tidak valid."
        else:
            status = "✅ TERINDIKASI FAKTA"
            explanation = "Konten sesuai dengan pola informasi yang kredibel."

        reply = f"""📊 HASIL ANALISIS BERITA

Status: {status}
Confidence: {confidence:.2f}%
{explanation}

Analisis dilakukan menggunakan model Deep Learning berbasis IndoBERT

<:>Catatan:</b>
Hasil ini merupakan prediksi otomatis dan tidak menggantikan verifikasi fakta secara langsung. Gunakan sebagai referensi awal sebelum mengambil keputusan.
    """
        
    except Exception as e:
        reply = f"❌ Terjadi kesalahan:\n{e}"

    await update.message.reply_text(reply, parse_mode="HTML")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """👋 <b>Selamat datang di Hoax Detection Bot</b>

Bot ini membantu menganalisis apakah sebuah teks berita termasuk:
⚠️ Hoaks atau ✅ Fakta

📌 Cara penggunaan:
Kirimkan teks berita langsung ke bot, lalu sistem akan menganalisisnya.

Contoh:
"Kabar pemerintah akan menghapus internet..."

<b>⚠️ Catatan:</b>
Hasil analisis berbasis AI dan tidak menggantikan verifikasi fakta resmi.
"""
    await update.message.reply_text(message, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """📖 <b>Bantuan Penggunaan Bot</b>

1. Kirim teks berita
2. Tunggu hasil analisis
3. Bot akan menampilkan:
   - Status (Hoax/Fakta)
   - Confidence
   - Penjelasan

<b>Tips:</b>
Gunakan teks lengkap agar hasil lebih akurat.
"""
    await update.message.reply_text(message, parse_mode="HTML")
  
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()