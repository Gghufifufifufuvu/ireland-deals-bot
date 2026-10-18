method = "sendPhoto"

        else:

            publish_data["text"] = caption

            method = "sendMessage"

        result = telegram(

            method,

            publish_data

        )

        if result.get("ok"):

            status = "✅ Опубликовано в канале"

        else:

            status = "⚠️ Ошибка публикации"

    else:

        status = "❌ Отклонено"

    telegram("editMessageReplyMarkup", {

        "chat_id": message["chat"]["id"],

        "message_id": message["message_id"],

        "reply_markup": json.dumps(

            {"inline_keyboard": []}

        )

    })

    telegram("sendMessage", {

        "chat_id": ADMIN_CHAT_ID,

        "text": status

    })

    print(status)

def process_buttons():

    """Обрабатывает нажатия кнопок."""

    result = telegram(

        "getUpdates",

        {"timeout": 0}

    )

    if not result.get("ok"):

        print("Could not get updates")

        return

    updates = result.get("result", [])

    print("New updates:", len(updates))

    done_messages = set()

    for update in updates:

        if "callback_query" in update:

            try:

                handle_button(

                    update["callback_query"],

                    done_messages

                )

            except Exception as error:

                print(

                    "Error while handling button:",

                    error

                )

    if updates:

        last_id = max(

            update["update_id"]

            for update in updates

        )

        telegram("getUpdates", {

            "offset": last_id + 1,

            "timeout": 0

        })

if name == "__main__":

    if (

        len(sys.argv) > 1

        and sys.argv[1] == "test"

    ):

        send_deal_for_review(TEST_DEAL)

    process_buttons()
