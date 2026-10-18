import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]

DEAL = {
    "name": "Soundcore P30i Wireless Earbuds",
    "old_price": "€49.90",
    "new_price": "€29.90",
    "discount": "40%",
    "saving": "€20",
    "url": "https://www.amazon.ie/dp/B0CRTN7C8C",
    "features": [
        "Active Noise Cancelling",
        "Up to 45 hours battery life",
        "Charging case with phone stand",
    ],
    # Add a permitted, direct HTTPS image URL here later.
    "photo": "",
}

def telegram(method, data=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    body = urllib.parse.urlencode(data or {}).encode("utf-8")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, data=body), timeout=30
        ) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        try:
            result = json.load(error)
        except ValueError:
            result = {"ok": False, "description": str(error)}
        print("Telegram error:", method, result.get("description"))
        return result

def caption(deal):
    details = "\n".join("✅ " + item for item in deal["features"])
    return (
        "🇮🇪 IRELAND TECH DEALS\n\n"
        f"🔥 {deal['discount']} OFF — LIMITED-TIME DEAL\n\n"
        f"🎧 {deal['name']}\n\n"
        f"💶 NOW: {deal['new_price']}\n"
        f"🏷️ WAS: {deal['old_price']}\n"
        f"💰 SAVE: {deal['saving']}\n\n"
        f"{details}\n\n"
        "📦 Amazon Ireland\n"
        "⏳ Price and availability may change.\n"
        "#IrelandTechDeals #AmazonDeals"
    )

def buttons(rows):
    return json.dumps({"inline_keyboard": rows})

def send_deal_for_review(deal):
    data = {
        "chat_id": ADMIN_CHAT_ID,
        "reply_markup": buttons([[
            {"text": "✅ Опубликовать", "callback_data": "approve"},
            {"text": "❌ Отклонить", "callback_data": "reject"},
        ]]),
    }
    if deal["photo"]:
        data.update(photo=deal["photo"], caption=caption(deal))
        method = "sendPhoto"
    else:
        data.update(text=caption(deal))
        method = "sendMessage"
    result = telegram(method, data)
    print("Review sent:", result.get("ok"))

def handle_button(query):
    telegram("answerCallbackQuery", {"callback_query_id": query["id"]})
    message = query.get("message") or {}
    if str(query["from"]["id"]) != str(ADMIN_CHAT_ID):
        return
    if query.get("data") not in ("approve", "reject"):
        return
    if not message.get("chat"):
        return

    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    # Remove buttons first to avoid repeated taps.
    telegram("editMessageReplyMarkup", {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": buttons([]),
    })

    if query["data"] == "reject":
        status = "❌ Отклонено"
    else:
        post = {
            "chat_id": CHANNEL_ID,
            "reply_markup": buttons([[
                {"text": f"🛒 BUY NOW — {DEAL['new_price']}", "url": DEAL["url"]}
            ]]),
        }
        if message.get("photo"):
            post.update(
                photo=message["photo"][-1]["file_id"],
                caption=message.get("caption", caption(DEAL)),
            )
            method = "sendPhoto"
        else:
            post["text"] = message.get("text", caption(DEAL))
            method = "sendMessage"
        result = telegram(method, post)
        status = "✅ Опубликовано" if result.get("ok") else "⚠️ Ошибка публикации"
    telegram("sendMessage", {"chat_id": ADMIN_CHAT_ID, "text": status})

def process_buttons():
    result = telegram("getUpdates", {"timeout": 0})
    if not result.get("ok"):
        return
    updates = result.get("result", [])
    for update in updates:
        if "callback_query" in update:
            try:
                handle_button(update["callback_query"])
            except Exception as error:
                print("Button error:", error)
    if updates:
        last_id = max(update["update_id"] for update in updates)
        telegram("getUpdates", {"offset": last_id + 1, "timeout": 0})

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        send_deal_for_review(DEAL)
    process_buttons()
