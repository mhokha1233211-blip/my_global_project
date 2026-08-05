import os
from flask import Flask, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# 1. إعداد خادم Flask للبوت والـ API
app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# ----------------------------------------------------
# 🌐 واجهة الـ API المعُدلة (JSON Structure)
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
# 🤖 معالجات البوت (Telegram Handlers v2.0)
# ----------------------------------------------------

# أمر /start - إنشاء قائمة الأزرار التفاعلية
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(
        KeyboardButton("📄 تحليل اتفاقية"),
        KeyboardButton("💳 تحليل بطاقة")
    )

    keyboard.row(
        KeyboardButton("🏦 تحليل بنك"),
        KeyboardButton("🔐 تحليل SWIFT")
    )

    keyboard.row(
        KeyboardButton("📚 المصطلحات"),
        KeyboardButton("📊 التقرير النهائي")
    )

    bot.send_message(
        message.chat.id,
        "🏦 **Global Unified Engine v2.0**\n\nمرحباً بك! اختر الخدمة المطلوبة من القائمة أدناه:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# 📄 معالج تحليل اتفاقية
@bot.message_handler(func=lambda message: message.text == "📄 تحليل اتفاقية")
def contract(message):
    bot.send_message(
        message.chat.id,
        "📄 **أرسل ملف الاتفاقية** (PDF أو DOCX أو صور) وسأبدأ تحليلها واستخراج البيانات فوراً."
    )

# 💳 معالج تحليل بطاقة
@bot.message_handler(func=lambda message: message.text == "💳 تحليل بطاقة")
def card_analysis(message):
    bot.send_message(
        message.chat.id,
        "💳 **أرسل رقم البطاقة** أو أول 6 أرقام (BIN) للتحقق من المصدر والتفاصيل."
    )

# 🏦 معالج تحليل بنك
@bot.message_handler(func=lambda message: message.text == "🏦 تحليل بنك")
def bank_analysis(message):
    bot.send_message(
        message.chat.id,
        "🏦 **أدخل اسم البنك** أو الدولة لإجراء التحليل والتحقق من الموثوقية."
    )

# 🔐 معالج تحليل SWIFT
@bot.message_handler(func=lambda message: message.text == "🔐 تحليل SWIFT")
def swift_analysis(message):
    bot.send_message(
        message.chat.id,
        "🔐 **أرسل رمز SWIFT / BIC** المطلي للتحقق من صحة الفرع والدولة."
    )

# 📚 معالج المصطلحات
@bot.message_handler(func=lambda message: message.text == "📚 المصطلحات")
def terms_glossary(message):
    terms_text = (
        "📚 **قاموس المصطلحات المالي:**\n\n"
        "• **SWIFT Code:** رمز تعريفي عالمي للبنوك للمقاصات الدولية.\n"
        "• **IBAN:** رقم الحساب البنكي الدولي.\n"
        "• **LC (Letter of Credit):** خطاب اعتماد مستندي لضمان عمليات التجارة."
    )
    bot.send_message(message.chat.id, terms_text, parse_mode="Markdown")

# 📊 معالج التقرير النهائي
@bot.message_handler(func=lambda message: message.text == "📊 التقرير النهائي")
def final_report(message):
    bot.send_message(
        message.chat.id,
        "📊 **التقرير النهائي:**\nلا يوجد تحليل مكتمل في الجلسة الحالية. قم بإرسال مستند لإنشاء التقرير."
    )

# ----------------------------------------------------
# 🚀 تشغيل خادم Flask مع البوت
# ----------------------------------------------------
if __name__ == '__main__':
    # تشغيل البوت في الخلفية أو عبر Webhook حسب إعدادك
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
