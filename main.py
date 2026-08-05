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

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "engine": "Global Unified Engine v2.1", "pdf_parser": "smart_active"})

# ----------------------------------------------------
# 🧠 Smart PDF Parser Function (المحرك الذكي)
# ----------------------------------------------------
def analyze_pdf_text(text):
    # أنماط دقيقة جداً لعدم التقاط نصوص عشوائية
    dates = re.findall(r'\b(?:0[1-9]|[12][0-9]|3[01])[-/.](?:0[1-9]|1[012])[-/.](?:19|20)\d\d\b', text)
    swift_codes = re.findall(r'\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b', text)
    # تصفية الكلمات الإنجليزية الشائعة التي قد تتشابه مع السويفت
    swift_codes = [s for s in swift_codes if not s in ['TION', 'MENT', 'PAGE', 'DATE']]
    
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    amounts = re.findall(r'(?:USD|EUR|AED|\$|€|£)\s?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b', text)
    ibans = re.findall(r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b', text)

    return {
        "text_length": len(text),
        "dates": list(set(dates))[:3], # Set لمنع التكرار
        "swift": list(set(swift_codes))[:2],
        "emails": list(set(emails))[:2],
        "amounts": list(set(amounts))[:3],
        "ibans": list(set(ibans))[:2]
    }

# ----------------------------------------------------
# 🤖 Telegram Handlers
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("📄 تحليل اتفاقية"), KeyboardButton("💳 تحليل بطاقة"))
    keyboard.row(KeyboardButton("🏦 تحليل بنك"), KeyboardButton("🔐 تحليل SWIFT"))
    keyboard.row(KeyboardButton("📚 المصطلحات"), KeyboardButton("📊 التقرير النهائي"))
    bot.send_message(message.chat.id, "🏦 **Global Unified Engine v2.1**\n\nمرحباً بك! أرسل ملف PDF مباشرة لتحليله بدقة عالية:", parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        if not message.document.file_name.endswith('.pdf'):
            bot.reply_to(message, "⚠️ يرجى إرسال ملف بصيغة **PDF** فقط.")
            return
        
        bot.reply_to(message, "⏳ جارِ التحليل العميق واستخراج البيانات المالية...")
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
        
        report = (
            f"📄 **التقرير المالي والقانوني:**\n\n"
            f"• **اسم المستند:** `{message.document.file_name}`\n"
            f"• **التواريخ الموثقة:** {', '.join(result['dates']) if result['dates'] else 'لم يتم العثور على صيغة تاريخ واضحة'}\n"
            f"• **المبالغ المالية (القيم):** {', '.join(result['amounts']) if result['amounts'] else 'غير مدرجة'}\n"
            f"• **الحسابات (IBAN):** {', '.join(result['ibans']) if result['ibans'] else 'غير مدرجة'}\n"
            f"• **رموز البنوك (SWIFT):** {', '.join(result['swift']) if result['swift'] else 'غير موجودة'}\n"
            f"• **التواصل (إيميل):** {', '.join(result['emails']) if result['emails'] else 'غير موجود'}\n\n"
            f"✅ **الحالة:** اكتمل التحليل الذكي."
        )
        bot.send_message(message.chat.id, report, parse_mode="Markdown")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ: {str(e)}")

@bot.message_handler(func=lambda message: message.text in ["📄 تحليل اتفاقية", "💳 تحليل بطاقة", "🏦 تحليل بنك", "🔐 تحليل SWIFT", "📚 المصطلحات", "📊 التقرير النهائي"])
def buttons_handler(message):
    bot.send_message(message.chat.id, "🛠️ جارِ برمجة هذه الميزة.. برجاء إرسال ملف PDF مباشرة للتحليل.")

# ----------------------------------------------------
# 🚀 Background Thread & Server
# ----------------------------------------------------
def start_bot():
    try:
        bot.remove_webhook()
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot error: {e}")

threading.Thread(target=start_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
