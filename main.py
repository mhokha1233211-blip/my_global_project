import os
import threading
from flask import Flask, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# ----------------------------------------------------
# 🌐 API Endpoint
# ----------------------------------------------------
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "success": True,
        "contract": {
            "bank": "",
            "swift": "",
            "card": "",
            "currency": "",
            "amount": "",
            "risk": "",
            "trust_score": 0
        }
    })

# ----------------------------------------------------
# 🤖 Telegram Handlers
# ----------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("📄 تحليل اتفاقية"), KeyboardButton("💳 تحليل بطاقة"))
    keyboard.row(KeyboardButton("🏦 تحليل بنك"), KeyboardButton("🔐 تحليل SWIFT"))
    keyboard.row(KeyboardButton("📚 المصطلحات"), KeyboardButton("📊 التقرير النهائي"))

    bot.send_message(
        message.chat.id,
        "🏦 **Global Unified Engine v2.0**\n\nمرحباً بك! اختر الخدمة المطلوبة من القائمة أدناه:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == "📄 تحليل اتفاقية")
def contract(message):
    bot.send_message(message.chat.id, "📄 **أرسل ملف الاتفاقية** (PDF أو DOCX أو صور) وسأبدأ تحليلها.")

@bot.message_handler(func=lambda message: message.text == "💳 تحليل بطاقة")
def card_analysis(message):
    bot.send_message(message.chat.id, "💳 **أرسل رقم البطاقة** أو أول 6 أرقام (BIN) للتحقق من المصدر.")

@bot.message_handler(func=lambda message: message.text == "🏦 تحليل بنك")
def bank_analysis(message):
    bot.send_message(message.chat.id, "🏦 **أدخل اسم البنك** أو الدولة لإجراء التحليل.")

@bot.message_handler(func=lambda message: message.text == "🔐 تحليل SWIFT")
def swift_analysis(message):
    bot.send_message(message.chat.id, "🔐 **أرسل رمز SWIFT / BIC** للتحقق من صحة الفرع.")

@bot.message_handler(func=lambda message: message.text == "📚 المصطلحات")
def terms_glossary(message):
    terms_text = (
        "📚 **قاموس المصطلحات المالي:**\n\n"
        "• **SWIFT Code:** رمز تعريفي عالمي للبنوك للمقاصات الدولية.\n"
        "• **IBAN:** رقم الحساب البنكي الدولي.\n"
        "• **LC (Letter of Credit):** خطاب اعتماد مستندي."
    )
    bot.send_message(message.chat.id, terms_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "📊 التقرير النهائي")
def final_report(message):
    bot.send_message(message.chat.id, "📊 **التقرير النهائي:**\nلا يوجد تحليل مكتمل في الجلسة الحالية.")

# ----------------------------------------------------
# 🚀 Run Bot in Background Thread & Flask Server
# ----------------------------------------------------
def start_bot():
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot error: {e}")

# تشغيل البوت في الخلفية
threading.Thread(target=start_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
