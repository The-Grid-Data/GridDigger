import os

import requests


def send_short_message(chat_id, text):
    if chat_id == -1:
        return

    print(text)
    if LOCAL:
        return

    try:
        YOUR_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

        if not YOUR_BOT_TOKEN:
            raise Exception('TELEGRAM_BOT_TOKEN is not set')

        TELEGRAM_API = "https://api.telegram.org/bot" + YOUR_BOT_TOKEN + "/"

        url = TELEGRAM_API + "sendMessage"

        payload = {"chat_id": chat_id, "text": f"{text}"}
        response = requests.post(url, json=payload)
        if not response.ok:
            # Print the HTTP status code
            print("Status Code:", response.status_code)

            # Print the reason phrase (associated with status code)
            print("Reason:", response.reason)

            # Print the entire HTTP response headers
            print("Headers:", response.headers)

            # Print the URL of the request
            print("URL:", response.url)

            # Attempt to print the response body as JSON, fallback to raw text if unable to parse JSON
            try:
                response_json = response.json()
                print("JSON Response:", response_json)
            except ValueError:
                print("Text Response:", response.text)

        return response.json()  # Ensure this is JSON
    except Exception as e:
        print(f"'error': {e}")


def send_message(chat_id, text):
    if len(text) < 4096:
        send_short_message(chat_id, text)
        return
    send_short_message(chat_id, text[:4096])
    send_message(chat_id, text[4096:])


DEBUG_TAGS = {
    "T": True,
    "P": True,
    "Q": True,
    "S": True,
    "W": True,
}

LOCAL = False
import re


def extract_integers(string):
    # Define the regex pattern to match integers
    pattern = r'\b\d+\b'

    # Find all matches of integers in the string
    integers = re.findall(pattern, string)

    # Convert the matched strings to integers and return
    return [int(num) for num in integers]


def debug_telegram_bot(app, tag, text):
    if DEBUG_TAGS.get(tag, True):
        DEVELOPER_TELEGRAM_IDS_STRING = os.environ.get('DEVELOPER_TELEGRAM_IDS')

        if DEVELOPER_TELEGRAM_IDS_STRING:
            developer_chat_ids = extract_integers(DEVELOPER_TELEGRAM_IDS_STRING)
            for chat_id in developer_chat_ids:
                send_message(chat_id, f"[{app}] {tag} > {text}")
        else:
            print(f"[{app}] {tag} > {text}")



def set_webhook(webhook_url):
    try:
        YOUR_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        TELEGRAM_API = "https://api.telegram.org/bot" + YOUR_BOT_TOKEN + "/"
        WEBHOOK_URL = os.environ.get("LAMBDA_WEBHOOK_URL")

        url = TELEGRAM_API + "setWebhook"
        payload = {"url": webhook_url}
        response = requests.post(url, json=payload)
        return response.json()  # Ensure this is JSON
    except Exception as e:
        return {'error': str(e)}
