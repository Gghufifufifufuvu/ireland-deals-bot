import json import os import sys import urllib.parse import urllib.request import urllib.error
TOKEN = os.environ["BOT_TOKEN"] CHANNEL_ID = os.environ["CHANNEL_ID"] ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]
API = f"https://api.telegram.org/bot{TOKEN}"
DEAL = { "name": "Soundcore P30i Wireless Earbuds", "old_price": "€49.90", "new_price": "€29.90", "discount": "40%", "url": "https://www.amazon.ie/dp/B0CRTN7C8C", }
def telegram(method, data=None): body = urllib.parse.urlencode( data or {} ).encode("utf-8")
request = urllib.request.Request(
    f"{API}/{method}",
    data=body
)

try:
    with urllib.request.urlopen(
        request, timeout=30
    ) as response:
        return json.load(response)
except Exception as error:
    print("Telegram error:", error)
    return {"ok": False}
def deal_text(): return ( f"🔥 TECH DEAL IRELAND 🇮🇪\n\n" f"🎧 {DEAL['name']}\n\n" f"❌ Old price: {DEAL['old_price']}\n" f"✅ New price: {DEAL['new_price']}\n" f"💰 Discount: {DEAL['discount']}\n\n" f"🛒 Buy here:\n{DEAL['url']}\n\n" f"⚠️ Prices may change." )
def send_for_review(): keyboard = { "inline_keyboard": [ [ { "text": "✅ Опубликовать", "callback_data": "approve" }, { "text": "❌ Отклонить", "callback_data": "reject" } ] ] }
result = telegram(
    "sendMessage",
    {
        "chat_id": ADMIN_CHAT_ID,
        "text": deal_text(),
        "reply_markup": json.dumps(keyboard)
    }
)

print("Review:", result)
def process_buttons(): result = telegram( "getUpdates", {"timeout": 0} )
if not result.get("ok"):
    return

updates = result.get("result", [])

for update in updates:
    query = update.get("callback_query")

    if not query:
        continue

    query_id = query["id"]
    action = query.get("data")
    message = query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if str(chat_id) != str(ADMIN_CHAT_ID):
        telegram(
            "answerCallbackQuery",
            {
                "callback_query_id": query_id,
                "text": "Нет доступа"
            }
        )
        continue

    if action == "approve":
        published = telegram(
            "sendMessage",
            {
                "chat_id": CHANNEL_ID,
                "text": deal_text()
            }
        )

        status = (
            "✅ Опубликовано"
            if published.get("ok")
            else "⚠️ Ошибка публикации"
        )

    elif action == "reject":
        status = "❌ Отклонено"

    else:
        continue

    telegram(
        "answerCallbackQuery",
        {
            "callback_query_id": query_id
        }
    )

    telegram(
        "editMessageReplyMarkup",
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": json.dumps(
                {"inline_keyboard": []}
            )
        }
    )

    telegram(
        "sendMessage",
        {
            "chat_id": ADMIN_CHAT_ID,
            "text": status
        }
    )

if updates:
    last_id = max(
        update["update_id"]
        for update in updates
    )

    telegram(
        "getUpdates",
        {
            "offset": last_id + 1,
            "timeout": 0
        }
    )
if name == "main": if len(sys.argv) > 1 and sys.argv[1] == "test": send_for_review() else: process_buttons()
