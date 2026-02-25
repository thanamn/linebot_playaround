import os
import time
import sys
from datetime import datetime
import pytz
from google import genai
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, BroadcastRequest, TextMessage
)

# Config: 9:00 AM Bangkok
TARGET_HOUR = 9
TARGET_MINUTE = 0

def wait_until_target():
    # If you run this manually in GitHub, it skips the wait for instant testing
    if os.getenv('GITHUB_EVENT_NAME') == 'workflow_dispatch':
        print("Manual Test: Skipping wait.")
        return

    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    target = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
    
    if now < target:
        delay = (target - now).total_seconds()
        print(f"Waiting {delay} seconds until 09:00 AM...")
        time.sleep(delay)

def run_broadcast():
    try:
        # Get current time in Bangkok for the prompt
        tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(tz)
        current_date = now.strftime("%A, %d %B %Y")
        current_time = now.strftime("%I:%M %p")

        # 1. Generate Content with Gemini 2.5 Flash
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        prompt = (
            f"Today is {current_date} and the time is {current_time}. "
            "You are a friendly Japanese language tutor. Start by stating today's date and time in English. "
            "Then, provide a warm morning greeting in Japanese (using Kanji/Kana and Romaji), "
            "followed by the English translation. Finally, give me one 'Japanese Word of the Day' "
            "with its meaning and a simple example sentence. Keep the total message under 60 words."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        msg_text = response.text.strip()

        # 2. Broadcast to ALL followers via LINE v3 SDK
        config = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        with ApiClient(config) as api_client:
            line_api = MessagingApi(api_client)
            line_api.broadcast(BroadcastRequest(
                messages=[TextMessage(text=msg_text)]
            ))
        print(f"Success! Broadcasted: {msg_text}")
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    wait_until_target()
    run_broadcast()