import json

import os

import urllib.parse

import urllib.request

TOKEN = os.environ["BOT_TOKEN"]

ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]

def telegram(method, data):

    url = f"https://api.telegram.org/bot{TOKEN}/{method}"

    body = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(url, data=body)

    with urllib.request.urlopen(request, timeout=20) as response:

        return json.load(response)

def send_deal():

    message = (

        "🧪 TEST DEAL — NOT A REAL OFFER\n\n"

        "📱 Samsung Galaxy\n"

        "💶 Old price: €500\n"

        "💚 New price: €350\n"

        "🔥 Discount: 30%\n\n"

        "Publish this deal?"

    )

    buttons = {

        "inline_keyboard": [

            [

                {

                    "text": "✅ Publish",

                    "callback_data": "approve_test"

                },

                {

                    "text": "❌ Reject",

                    "callback_data": "reject_test"

                }

            ]

        ]

    }

    result = telegram("sendMessage", {

        "chat_id": ADMIN_CHAT_ID,

        "text": message,

        "reply_markup": json.dumps(buttons)

    })

    print("Test deal sent:", result["ok"])

if name == "__main__":

    send_deal()
