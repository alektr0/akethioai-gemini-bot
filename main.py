import requests
import time
import json
import os
from datetime import datetime
import google.generativeai as genai

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = "8584526957:AAHx9BPSotN0yS7MdewRTF3kxSAe9i2ZDvc"
CHANNEL_ID = "@akethioai" 
GEMINI_API_KEY = "AIzaSyCgDz4Pq-J6JbfbhpnbBlU2ecbVYtW3YSI"

# Time to wait between posts (8 Hours = 28800 seconds)
POST_INTERVAL = 8 * 60 * 60 

# Files to store data
MEMORY_FILE = "akethio_memory.json"
STATE_FILE = "akethio_state.json"

# Topic Rotation List - Optimized for AKethioAI
TOPICS = [
    "AI EDUCATION 🧠 (Tutorial on how to use a specific tool like ChatGPT, Midjourney, or Claude)",
    "AI PRODUCTIVITY 💰 (How to use AI to save time or make money in business/work)",
    "AI NEWS 📰 (The latest global AI news translated and explained for Ethiopians)"
]

# ================= SETUP =================
genai.configure(api_key=GEMINI_API_KEY)
# Using the latest Gemini 3 Flash preview for superior reasoning and speed
model = genai.GenerativeModel("gemini-3-flash-preview") 

# ================= DATA MANAGEMENT =================

def load_json(filename, default_value):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_value
    return default_value

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_topic_index():
    state = load_json(STATE_FILE, {"topic_index": 0})
    return state["topic_index"]

def advance_topic_index():
    state = load_json(STATE_FILE, {"topic_index": 0})
    state["topic_index"] = (state["topic_index"] + 1) % len(TOPICS)
    save_json(STATE_FILE, state)

def record_post_history(post_content):
    history = load_json(MEMORY_FILE, [])
    history.append({
        "timestamp": str(datetime.now()),
        "snippet": post_content[:200] # Increased snippet length for better context
    })
    if len(history) > 15: # Keep 15 items in memory to avoid repetitive content
        history.pop(0)
    save_json(MEMORY_FILE, history)

def get_past_topics_string():
    history = load_json(MEMORY_FILE, [])
    if not history:
        return "None."
    return "\n".join([f"- {h['snippet']}..." for h in history])

# ================= AI GENERATION =================

def generate_post(topic_category):
    past_topics = get_past_topics_string()
    
    prompt = f"""
    You are 'AKethioAI', the leading AI educator for the Ethiopian community on Telegram.
    
    Task: Write ONE high-quality viral Telegram post in Amharic.
    Category: {topic_category}
    
    POST HISTORY (DO NOT REPEAT THESE TOPICS):
    {past_topics}
    
    REQUIREMENTS:
    1. Language: Amharic (Use English for technical names/tools).
    2. Style: Engaging, informative, and professional.
    3. Structure:
       - 🎯 Catchy Title with Emojis
       - 💡 The explanation/value
       - 🚀 'How to start' section
       - 📢 Call to action (Join @akethioai)
    4. Constraint: Keep it under 180 words.
    5. Output ONLY the post text.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None

# ================= TELEGRAM =================

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Simple formatting cleanup for Telegram Markdown
    clean_text = text.replace("**", "*") 
    
    data = {
        "chat_id": CHANNEL_ID,
        "text": clean_text,
        "parse_mode": "Markdown" 
    }
    
    try:
        response = requests.post(url, data=data)
        response_json = response.json()
        
        if not response_json.get("ok"):
            print(f"⚠️ Telegram Error: {response_json}")
            # Try without markdown if it fails
            if "parse_mode" in data:
                del data["parse_mode"]
                requests.post(url, data=data)
            
        return True
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

# ================= MAIN LOOP =================

print("🚀 AKethioAI Bot is now ONLINE and using Gemini 3...")

while True:
    try:
        current_index = get_next_topic_index()
        current_topic = TOPICS[current_index]
        
        print(f"🤖 Preparing post for category: {current_topic}")
        
        post_content = generate_post(current_topic)
        
        if post_content:
            print("📨 Sending to @akethioai...")
            success = send_to_telegram(post_content)
            
            if success:
                print("✅ Posted Successfully!")
                record_post_history(post_content)
                advance_topic_index()
                
                print(f"💤 Sleeping for {POST_INTERVAL/3600} hours...")
                time.sleep(POST_INTERVAL)
            else:
                print("⚠️ Telegram failed. Retrying in 10 minutes...")
                time.sleep(600) 
        else:
            print("⚠️ Gemini failed. Retrying in 2 minutes...")
            time.sleep(120)

    except KeyboardInterrupt:
        print("\n🛑 Bot shut down.")
        break
    except Exception as e:
        print(f"❌ Error in main loop: {e}")
        time.sleep(60)
