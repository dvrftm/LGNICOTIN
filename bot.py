import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

FIELDS = [
    ("name", "⛓️ اسم خودت چیه؟", "اسم"),
    ("age", "⛓️ چند سالته؟", "سن"),
    ("city", "⛓️ اهل کدوم شهری؟", "شهر"),
    ("orientation", "⛓️ گرایشت چیه؟", "گرایش"),
    ("relationship_status", "⛓️ وضعیت تأهلت چیه؟", "وضعیت تأهل"),
]

ASKING = 0
CANCEL_KEY = "لغو فرم"

FORM_TEMPLATE = """𓆩 🩸 ʟɢ ɴɪᴄᴏᴛɪɴ 🐊 𓆪
━━━━━━━━━━━━━━━━━━━━
⛓️ ɴᴀᴍᴇ 〢 اسم :
↳ 🩸 {name}
⛓️ ᴀɢᴇ 〢 سن :
↳ 🩸 {age}
⛓️ ᴄɪᴛʏ 〢 شهر :
↳ 🩸 {city}
⛓️ ᴏʀɪᴇɴᴛᴀᴛɪᴏɴ 〢 گرایش :
↳ 🩸 {orientation}
⛓️ ʀᴇʟᴀᴛɪᴏɴsʜɪᴘ sᴛᴀᴛᴜs 〢 وضعیت تاهل :
↳ 🩸 {relationship_status}
━━━━━━━━━━━━━━━━━━━━
🖤 ᴡᴇ ᴀʀᴇ ᴛʜᴇ ᴅᴀʀᴋ sɪᴅᴇ 🩸
𓆩 🐊 ʟɢ ɴɪᴄᴏᴛɪɴ 🐊 𓆪"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["form_answers"] = {}
    context.user_data["field_index"] = 0

    keyboard = ReplyKeyboardMarkup(
        [[CANCEL_KEY]], resize_keyboard=True
    )

    await update.effective_message.reply_text(
        "سلام! 🩸🐊\n"
        "برای تکمیل فرم ʟɢ ɴɪᴄᴏᴛɪɴ به سؤال‌ها پاسخ بده.\n\n"
        f"سؤال اول:\n{FIELDS[0][1]}",
        reply_markup=keyboard,
    )
    return ASKING


async def collect_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    message = update.effective_message
    answer = (message.text or "").strip()

    if answer == CANCEL_KEY:
        return await cancel(update, context)

    if not answer:
        await message.reply_text("لطفاً پاسخت رو به‌صورت متن بفرست.")
        return ASKING

    index = context.user_data.get("field_index", 0)

    if index >= len(FIELDS):
        return ConversationHandler.END

    key, question, label = FIELDS[index]
    context.user_data["form_answers"][key] = answer

    next_index = index + 1

    if next_index < len(FIELDS):
        context.user_data["field_index"] = next_index
        await message.reply_text(FIELDS[next_index][1])
        return ASKING

    answers = context.user_data["form_answers"]
    completed_form = FORM_TEMPLATE.format(
        name=answers.get("name", "—"),
        age=answers.get("age", "—"),
        city=answers.get("city", "—"),
        orientation=answers.get("orientation", "—"),
        relationship_status=answers.get("relationship_status", "—"),
    )

    await message.reply_text(
        completed_form,
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.reply_text(
        "✅ فرم با موفقیت تکمیل شد!\n"
        "برای پر کردن فرم جدید، دستور /start رو بزن."
    )

    context.user_data.pop("form_answers", None)
    context.user_data.pop("field_index", None)
    return ConversationHandler.END


async def cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.pop("form_answers", None)
    context.user_data.pop("field_index", None)

    await update.effective_message.reply_text(
        "فرم لغو شد. برای شروع دوباره /start رو بزن.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "توکن ربات پیدا نشد. متغیر محیطی BOT_TOKEN رو تنظیم کن."
        )

    app = Application.builder().token(token).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    collect_answer,
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("cancel", cancel))

    print("ربات فرم‌ساز روشن شد.")
    app.run_polling()


if __name__ == "__main__":
    main()
