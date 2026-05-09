import requests
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
    ChatAction,
    CommandHandler
)

from news_search import get_related_news

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://web-production-a5b24.up.railway.app/predict"

print("Bot started...")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    try:
        # =========================
        # Predict ke FastAPI
        # =========================
        response = requests.post(
            API_URL,
            json={"text": text},
            timeout=30
        )

        result = response.json()

        label = result["label"]
        score = result["score"]

        confidence = score * 100

        # =========================
        # Status
        # =========================
        if label == "hoax":
            status = "⚠️ TERINDIKASI HOAKS"
            explanation = (
                "Konten memiliki pola yang sering "
                "ditemukan pada informasi tidak valid."
            )
        else:
            status = "✅ TERINDIKASI FAKTA"
            explanation = (
                "Konten sesuai dengan pola "
                "informasi yang kredibel."
            )

        # =========================
        # Cari berita terkait
        # =========================
        related_news = get_related_news(text)

        news_text = ""

        if related_news:

            news_text += "\n📰 <b>Berita Terkait</b>\n"

            for news in related_news:

                source = news["source"]
                title = news["title"]
                link = news["link"]

                source_badge = {
                    "CNN Indonesia": "🟥 CNN",
                    "Antara": "🟦 ANTARA",
                    "Tempo": "🟩 TEMPO",
                    "Kumparan": "🟨 KUMPARAN",
                    "Tirto": "🟪 TIRTO"
                }.get(source, "📰 NEWS")

                news_text += (
                    f"\n{source_badge} "
                    f"<b>{title}</b>\n"
                    f"🔗 {link}\n"
                )

        else:
            news_text = (
                "\n📰 <b>Berita Terkait</b>\n"
                "Tidak ditemukan berita relevan "
                "dari sumber terpercaya."
            )

        # =========================
        # Final Reply
        # =========================
        reply = f"""
📊 <b>HASIL ANALISIS BERITA</b>

Status:
{status}

Confidence:
{confidence:.2f}%

🧠 <b>Penjelasan</b>
{explanation}

⚙️ <b>Sistem</b>
Analisis dilakukan menggunakan model
Deep Learning berbasis IndoBERT.

{news_text}

⚠️ <b>Catatan</b>
Hasil ini merupakan prediksi otomatis
dan tidak menggantikan verifikasi fakta resmi.
"""

    except Exception as e:

        reply = (
            "❌ Terjadi kesalahan saat "
            f"memproses permintaan.\n\n{e}"
        )

    await update.message.reply_text(
        reply,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# ===================================
# /start
# ===================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
👋 <b>Selamat datang di Hoax Detection Bot</b>

Bot ini membantu menganalisis apakah
sebuah berita termasuk:

⚠️ Hoaks
atau
✅ Fakta

📌 <b>Cara Penggunaan</b>
Kirimkan teks berita langsung ke bot.

Bot akan:
• menganalisis berita
• memberikan confidence score
• menampilkan berita terkait

⚠️ <b>Catatan</b>
Hasil analisis berbasis AI dan
tidak menggantikan verifikasi fakta resmi.
"""

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )


# ===================================
# /help
# ===================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
📖 <b>Bantuan Penggunaan Bot</b>

1. Kirim teks berita
2. Tunggu hasil analisis
3. Sistem akan menampilkan:
   • Status Hoaks/Fakta
   • Confidence score
   • Berita terkait

💡 <b>Tips</b>
Gunakan teks berita yang lengkap
agar hasil lebih akurat.
"""

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )


# ===================================
# App
# ===================================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

app.run_polling()
