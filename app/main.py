import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import telebot
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GlobalEngine")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("RENDER_EXTERNAL_URL", "")

if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is missing!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML") if BOT_TOKEN else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    if bot and APP_URL:
        webhook_url = f"{APP_URL}/webhook"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        logger.info(f"Telegram Webhook set to: {webhook_url}")
    elif bot:
        asyncio.create_task(asyncio.to_thread(bot.infinity_polling, skip_pending=True))
        logger.info("Telegram Bot Polling started in background thread.")
    
    yield
    
    if bot and APP_URL:
        bot.remove_webhook()
        logger.info("Telegram Webhook removed.")

app = FastAPI(
    title="Global Unified Engine API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "system": "Global Unified Engine", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze", tags=["API"])
async def analyze_text(payload: AnalyzeRequest):
    try:
        result = {"input": payload.text, "status": "processed", "trust_score": 98.5}
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/webhook", tags=["Telegram"])
async def telegram_webhook(update: dict, background_tasks: BackgroundTasks):
    if bot:
        update_obj = telebot.types.Update.de_json(update)
        background_tasks.add_task(bot.process_new_updates, [update_obj])
    return {"status": "ok"}

if bot:
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "<b>مرحباً بك في المنظومة العالمية الموحدة!</b>\nأرسل أي نص لتحليله ومعالجته فوراً.")

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        text = message.text
        bot.reply_to(message, f"تم استقبال طلبك بنجاح:\n<code>{text}</code>\n\nجارٍ المعالجة...")
