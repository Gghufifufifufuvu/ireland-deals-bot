import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]

SEPARATOR = "➖➖➖➖➖➖"
QUESTION = "Опубликовать эту скидку?"

TEST_DEAL = (
    "📱 Samsung Galaxy\n"
    "💶 Old price: €500\n"
    "💚 New price: €350\n"
    "🔥 Discount: 30%"
)


def telegram(method, data=None):
    """Отправляет запрос в Telegram и возвращает ответ."""
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    body = urllib.parse.urlencode(data or {}).encode("utf-8")
    request = urllib.request.Request(url, data=body)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        result = json.load(error)
        print(f"Telegram error in {method}:", result.get("description"))
        return result


def send_deal_for_review(deal_text):
    """Присылает скидку тебе в личку с кнопками."""
    text = f"{deal_text}\n\n{SEPARATOR}\n{QUESTION}"
    buttons = {
        "inline_keyboard": [[
            {"text": "✅ Опубликовать", "callback_data": "approve"},
            {"text": "❌ Отклонить", "callback_data": "reject"},
        ]]
    }
    result = telegram("sendMessage", {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "reply_markup": json.dumps(buttons),
    })
    print("Deal sent for review:", result.get("ok"))


def handle_button(query, done_messages):
    """Обрабатывает одно нажатие кнопки."""
    user_id = str(query["from"]["id"])
    message = query.get("message")
    action = query.get("data")

    if user_id != str(ADMIN_CHAT_ID) or not message:
        print("Ignored: button pressed by someone else")
        return
    if action not in ("approve", "reject"):
        print("Ignored: old button", action)
        return

    message_key = (message["chat"]["id"], message["message_id"])
    if message_key in done_messages:
        print("Ignored: repeated press on the same deal")
        return
    done_messages.add(message_key)

    deal_text = message.get("text", "").split(SEPARATOR)[0].strip()

    if action == "approve":
        result = telegram("sendMessage", {"chat_id": CHANNEL_ID, "text": deal_text})
        status = "✅ Опубликовано в канале" if result.get("ok") else "⚠️ Ошибка публикации"
    else:
        status = "❌ Отклонено"

    telegram("editMessageText", {
        "chat_id": message["chat"]["id"],
        "message_id": message["message_id"],
        "text": f"{deal_text}\n\n{SEPARATOR}\n{status}",
    })
    print(status)


def process_buttons():
    """Забирает все нажатия кнопок, накопленные с прошлого запуска."""
    result = telegram("getUpdates", {"timeout": 0})
    if not result.get("ok"):
        print("Could not get updates")
        return

    updates = result.get("result", [])
    print("New updates:", len(updates))

    done_messages = set()
    for update in updates:
        if "callback_query" in update:
            try:
                handle_button(update["callback_query"], done_messages)
            except Exception as error:
                print("Error while handling button:", error)

    if updates:
    last_id = max(update["update_id"] for update in updates)
    telegram("getUpdates", {"offset": last_id + 1, "timeout": 0})
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        send_deal_for_review(TEST_DEAL)
    process_buttons()
