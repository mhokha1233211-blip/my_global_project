import os
import io
import threading
from flask import Flask, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from pypdf import PdfReader
from card_analyzer import analyze_card_text

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "engine": "Global Unified Engine v2.5", "mode": "modular"})

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("📄 تحليل اتفاقية"), KeyboardButton("💳 تحليل بطاقة"))
    keyboard.row(KeyboardButton("🏦 تحليل بنك"), KeyboardButton("🔐 تحليل SWIFT"))
    keyboard.row(KeyboardButton("📚 المصطلحات"), KeyboardButton("📊 التقرير النهائي"))
    bot.send_message(message.chat.id, "🏦 **Global Unified Engine v2.5**\n\nاختر الخدمة المطلوبة أو أرسل الملف:", parse_mode="Markdown", reply_markup=keyboard)

# التعامل مع زر تحليل بطاقة
@bot.message_handler(func=lambda message: message.text == "💳 تحليل بطاقة")
def card_button_handler(message):
    bot.send_message(message.chat.id, "💳 **النظام جاهز لتحليل البطاقات:**\n\nأرسل صورة البطاقة أو النص المقتبس منها وسيقوم الموديول بتحليل كل حرف ورقم فيها بدقة.", parse_mode="Markdown")

# استقبال المستندات أو الصور للتحليل
@bot.message_handler(content_types=['document', 'photo'])
def handle_files(message):
    try:
        if message.content_type == 'document':
            if not message.document.file_name.endswith('.pdf'):
                bot.reply_to(message, "⚠️ يرجى إرسال ملف PDF أو صورة بطاقة صحيحة.")
                return
            
            bot.reply_to(message, "⏳ جارِ استخراج وتحليل المستند...")
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            pdf_reader = PdfReader(io.BytesIO(downloaded_file))
            
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""
                
            result = analyze_card_text(extracted_text)
            
            report = (
                f"💳 **تقرير تحليل البطاقة والمستند:**\n\n"
                f"• **إجمالي الحروف المستخرجة:** {result.get('raw_length', 0)}\n"
                f"• **الأرقام البارزة:** {', '.join(result.get('card_numbers', [])) or 'لا توجد'}\n"
                f"• **تواريخ الصلاحية:** {', '.join(result.get('expiry_dates', [])) or 'غير مدرجة'}\n"
                f"• **الأسماء/الجهات المكتشفة:** {', '.join(result.get('names_or_entities', [])) or 'غير مطابقة'}\n"
                f"• **الرموز والتسلسلات:** {', '.join(result.get('codes', [])) or 'لا توجد'}\n\n"
                f"✅ **الحالة:** تم تحليل كل حقل وحرف بنجاح."
            )
            bot.send_message(message.chat.id, report, parse_mode="Markdown")
            
        elif message.content_type == 'photo':
            bot.reply_to(message, "📸 تم استلام صورة البطاقة. ميزة قراءة الصور الفورية (OCR) سيتم تفعيلها في التحديث القادم، حالياً يرجى إرسال ملفات النصوص أو الـ PDF.")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء التحليل: {str(e)}")

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    bot.send_message(message.chat.id, "📁 يرجى اختيار أحد الأزرار أو إرسال الملف المطلوب للتحليل.")

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
