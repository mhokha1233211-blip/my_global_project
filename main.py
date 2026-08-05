import os
import re
import io
import threading
from flask import Flask, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from pypdf import PdfReader

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# ----------------------------------------------------
# 🌐 API Endpoint
# ----------------------------------------------------
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "engine": "Global Unified Engine v2.0", "pdf_parser": "active"})

# ----------------------------------------------------
# 🔍 PDF Parser Function
# ----------------------------------------------------
def analyze_pdf_text(text):
    dates = re.findall(r'\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b', text)
    swift_codes = re.findall(r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b', text)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    amounts = re.findall(r'(\$|\bUSD|\bEUR|\bAED)\s?[\d,]+(?:\.\d{2})?', text)
    return {"text_length": len(text), "dates": dates[:3], "swift": swift_codes[:2], "emails": emails[:2], "amounts": amounts[:3]}

# ----------------------------------------------------
# 🤖 Telegram Handlers
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("📄 تحليل اتفاقية"), KeyboardButton("💳 تحليل بطاقة"))
    keyboard.row(KeyboardButton("🏦 تحليل بنك"), KeyboardButton("🔐 تحليل SWIFT"))
    keyboard.row(KeyboardButton("📚 المصطلحات"), KeyboardButton("📊 التقرير النهائي"))
    bot.send_message(message.chat.id, "🏦 **Global Unified Engine v2.0**\n\nمرحباً بك! اختر الخدمة أو أرسل ملف PDF مباشرة لتحليله:", parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        if not message.document.file_name.endswith('.pdf'):
            bot.reply_to(message, "⚠️ يرجى إرسال ملف بصيغة **PDF** فقط.")
            return
        bot.reply_to(message, "⏳ جارِ تحميل الملف وتحليل البيانات...")
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        pdf_reader = PdfReader(io.BytesIO(downloaded_file))
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""
        if not extracted_text.strip():
            bot.send_message(message.chat.id, "❌ لم يتم العثور على نص قابل للقراءة.")
            return
        result = analyze_pdf_text(extracted_text)
        report = (f"📄 **تقرير تحليل المستند:**\n\n• **اسم الملف:** `{message.document.file_name}`\n• **حجم النص:** {result['text_length']} حرف\n• **التواريخ:** {', '.join(result['dates']) if result['dates'] else 'لم تحدد'}\n• **SWIFT:** {', '.join(result['swift']) if result['swift'] else 'غير موجودة'}\n• **إيميلات:** {', '.join(result['emails']) if result['emails'] else 'غير موجود'}\n\n✅ **الحالة:** تم التحليل.")
        bot.send_message(message.chat.id, report, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "📄 تحليل اتفاقية")
def contract(message): bot.send_message(message.chat.id, "📄 **أرسل ملف الاتفاقية (PDF)**.")

@bot.message_handler(func=lambda message: message.text == "💳 تحليل بطاقة")
def card_analysis(message): bot.send_message(message.chat.id, "💳 **أرسل رقم البطاقة** للتحقق.")

@bot.message_handler(func=lambda message: message.text == "🏦 تحليل بنك")
def bank_analysis(message): bot.send_message(message.chat.id, "🏦 **أدخل اسم البنك**.")

@bot.message_handler(func=lambda message: message.text == "🔐 تحليل SWIFT")
def swift_analysis(message): bot.send_message(message.chat.id, "🔐 **أرسل رمز SWIFT**.")

@bot.message_handler(func=lambda message: message.text == "📚 المصطلحات")
def terms_glossary(message): bot.send_message(message.chat.id, "📚 **قاموس المصطلحات**...")

@bot.message_handler(func=lambda message: message.text == "📊 التقرير النهائي")
def final_report(message): bot.send_message(message.chat.id, "📊 أرسل ملف PDF أولاً.")

# ----------------------------------------------------
# 🚀 Background Thread & Server
# ----------------------------------------------------
def start_bot():
    try:
        bot.remove_webhook() # <-- سطر مسح التعارض مع تليجرام
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot error: {e}")

threading.Thread(target=start_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
