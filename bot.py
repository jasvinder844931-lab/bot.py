import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openpyxl import load_workbook
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Excel Matching Bot 🤖\n"
        "Upload your demo Excel file."
    )

async def upload_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    data = await file.download_as_bytearray()

    workbook = load_workbook(BytesIO(data))
    sheet = workbook.active

    context.user_data["accounts"] = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:
            context.user_data["accounts"].append(
                (str(row[0]), str(row[1]).upper())
            )

    await update.message.reply_text(
        "Excel uploaded successfully!\n"
        "Send last 4 digits and IFSC."
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = context.user_data.get("accounts", [])

    parts = update.message.text.split()

    if len(parts) != 2:
        await update.message.reply_text("Format: 1234 ABCD0123456")
        return

    last4, ifsc = parts

    if len(last4) != 4:
        await update.message.reply_text("Enter exactly 4 digits.")
        return

    matches = [
        acc for acc in accounts
        if acc[0].endswith(last4)
        and acc[1] == ifsc.upper()
    ]

    if matches:
        await update.message.reply_text("✅ MATCH FOUND")
    else:
        await update.message.reply_text("❌ NO MATCH FOUND")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, upload_excel))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check))

app.run_polling()
