import json
import os
import urllib.parse
import urllib.request


def send_message(text):
    token = os.environ["BOT_TOKEN"]
    channel_id = os.environ["CHANNEL_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": channel_id,
        "text": text,
    }).encode("utf-8")
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


if __name__ == "__main__":
    message = (
        "🇮🇪 Welcome to Ireland Best Deals!\n\n"
        "🔥 Best discounts and special offers in Ireland!\n\n"
        "🛍 Follow us for new deals!"
    )
    result = send_message(message)
    print("Message sent successfully!", result["ok"])
