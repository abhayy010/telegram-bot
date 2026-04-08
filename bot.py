import json
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ===== CONFIG =====
BOT_TOKEN = "8345406600:AAHPzjbozPStB8aswBG4Gml2mtADE_nXFnk"
ADMIN_IDS = [7217854836]
DATA_FILE = "sam.json"

# ===== CHANNELS =====

# 👉 PUBLIC CHANNELS
PUBLIC_CHANNELS = [
    "@abhay7474",
    "@abhay09900"
]

# 👉 PRIVATE CHANNELS
PRIVATE_CHANNELS = [
    ("https://t.me/+zL_LV9LVODFlYjll", -1003897928700),
    ("https://t.me/+rnFBeRM2BaNkODI1", -1003874932393),
    ("https://t.me/+bKKuw90xS7A1YzNl", -1003771373631),
    ("https://t.me/+4RZZ8gT4iag1YzJl", -1003825957146),
]

# ==================
logging.basicConfig(level=logging.INFO)

# ===== DATA =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ===== JOIN CHECK =====
async def is_user_member(user_id, context):

    for username in PUBLIC_CHANNELS:
        try:
            member = await context.bot.get_chat_member(username, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    for _, chat_id in PRIVATE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    return True

# ===== KEYBOARD =====
def join_keyboard():
    buttons = []
    row = []

    all_channels = []

    # Public channels
    for username in PUBLIC_CHANNELS:
        all_channels.append(f"https://t.me/{username.replace('@','')}")

    # Private channels
    for link, _ in PRIVATE_CHANNELS:
        all_channels.append(link)

    # Buttons (2 per row)
    for link in all_channels:
        row.append(InlineKeyboardButton("📢 JOIN CHANNEL", url=link))

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # Final button
    buttons.append([
        InlineKeyboardButton("✅ JOINED ALL", callback_data="check")
    ])

    return InlineKeyboardMarkup(buttons)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 Pehle sab channels join karo 👇",
        reply_markup=join_keyboard()
    )

# ===== SET VIDEO =====
async def setvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("❌ Not allowed")
    await update.message.reply_text("📤 Video bhejo")

# ===== SET FILE =====
async def setfile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("❌ Not allowed")
    await update.message.reply_text("📤 File bhejo")

# ===== SAVE VIDEO =====
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    data = load_data()
    data["video_id"] = update.message.video.file_id
    save_data(data)

    await update.message.reply_text("✅ Video saved")

# ===== SAVE FILE =====
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not update.message.document:
        return

    data = load_data()
    data["file_id"] = update.message.document.file_id
    save_data(data)

    await update.message.reply_text("✅ File saved")

# ===== BUTTON =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await is_user_member(user_id, context):

        data = load_data()

        if data.get("video_id"):
            await context.bot.send_video(user_id, data["video_id"], caption="🎬 Video Ready")

        if data.get("file_id"):
            await context.bot.send_document(
                user_id,
                data["file_id"],
                caption="📂 File Ready"
            )

        await query.edit_message_text("✅ Access Granted")

    else:
        await query.edit_message_text(
            "❌ Pehle sab channels join karo",
            reply_markup=join_keyboard()
        )

# ===== MAIN =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setvideo", setvideo))
    app.add_handler(CommandHandler("setfile", setfile))

    app.add_handler(MessageHandler(filters.VIDEO, save_video))
    app.add_handler(MessageHandler(filters.Document.ALL, save_file))

    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
