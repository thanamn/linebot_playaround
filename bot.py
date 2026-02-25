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
        # 1. Generate Content with Gemini 2.0/3.0 SDK
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents="Write a short, warm, and unique morning greeting for today."
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