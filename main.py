import requests
import time
import json
import hashlib
from datetime import datetime
import google.generativeai as genai

# ================= CONFIG =================
TELEGRAM_BOT_TOKEN = "8584526957:AAHx9BPSotN0yS7MdewRTF3kxSAe9i2ZDvc"
CHANNEL_USERNAME = "@akethioai"  # change if needed
GEMINI_API_KEY = "AIzaSyDhhSUlI7bnDjSOUzASj6K9kM9SyifQPx4"

POST_INTERVAL = 8 * 60 * 60  # 8 hours (3 posts/day)

MEMORY_FILE = "akethioai_memory.json"

# ================= GEMINI SETUP =================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ================= MEMORY SYSTEM =================
def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

memory_posts = load_memory()

def is_duplicate(text):
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    for item in memory_posts:
        if item["hash"] == h:
            return True
    memory_posts.append({"hash": h, "time": str(datetime.now())})
    save_memory(memory_posts)
    return False

# ================= YOUR MASTER PROMPT =================
MASTER_PROMPT = """
You are an expert AI content creator for an Ethiopian audience.

Your task is to generate DAILY viral Telegram posts in Amharic for a channel called "AKethioAI".

IMPORTANT RULES:
1. Never repeat ideas, examples, tools, or wording from previous posts.
2. Content must be simple, clear, and easy for beginners.
3. Posts must feel viral, modern, and exciting.
4. Use short paragraphs and emojis (but not too many).
5. Focus on real AI use cases for Ethiopians.
6. Avoid technical jargon.
7. Each post must feel new, surprising, and useful.
8. Use a strong hook at the beginning.

Create 3 different posts:

POST 1 — EDUCATION / TIP 🧠
POST 2 — VIRAL / MONEY / TOOL 💰🤖
POST 3 — AI NEWS 📰

Tone:
Friendly, confident, modern Ethiopian style.
Write in natural Amharic.
Emotionally engaging, slightly dramatic, curiosity-driven.

Output only the 3 posts in Amharic.
"""

# ================= AI GENERATOR =================
def generate_posts():
    response = model.generate_content(MASTER_PROMPT)
    return response.text.strip()

# ================= TELEGRAM SENDER =================
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_USERNAME,
        "text": text
    }
    requests.post(url, data=data)

# ================= MAIN LOOP =================
while True:
    try:
        posts = generate_posts()

        if not is_duplicate(posts):
            send_to_telegram(posts)
            print("✅ Posted successfully!")
        else:
            print("⚠️ Duplicate detected, regenerating...")

        time.sleep(POST_INTERVAL)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(60)
