import os
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

# Yahan apna Naya Bot Token daal jo BotFather se mila hai
TOKEN = "8998180780:AAFPptSf0yaA4stK1m9LcWwPPEcl9v5jXXA"
ADMIN_ID = 1232238066

bot = telebot.TeleBot(TOKEN)
products = {}

# Flask server to keep Render Free Tier alive 24/7
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is alive and running 24/7!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


@bot.message_handler(commands=["start"])
def start(message):
  if message.from_user.id == ADMIN_ID:
    bot.send_message(
        message.chat.id,
        "👑 **Welcome Admin!**\nSend any software/file photo with this"
        " caption format:\n\n`100`\n`https://your-universal-link.com`",
        parse_mode="Markdown",
    )
  else:
    bot.send_message(
        message.chat.id,
        "👋 Welcome to Secure Digital Store.\nPurchase resources securely using"
        " Telegram Stars ⭐️",
    )


@bot.message_handler(content_types=["photo"])
def handle_admin_upload(message):
  if message.from_user.id != ADMIN_ID:
    bot.reply_to(message, "⛔ You are not authorized to upload products.")
    return

  caption = message.caption or ""
  lines = [line.strip() for line in caption.split("\n") if line.strip()]

  if len(lines) < 2:
    bot.reply_to(
        message,
        "⚠️ **Invalid Format!**\nCaption mein ye likh:\nLine 1: Price in Stars"
        " (e.g., 100)\nLine 2: Universal URL (Drive, Mega, etc.)",
        parse_mode="Markdown",
    )
    return

  try:
    price_amount = int(lines[0])
    file_link = lines[1]
  except ValueError:
    bot.reply_to(
        message, "⚠️ Pehli line mein sirf valid number (price) hona chahiye."
    )
    return

  if not file_link.startswith("http"):
    bot.reply_to(
        message, "⚠️ Dusri line mein valid URL (http...) daalna zaroori hai!"
    )
    return

  file_id = message.photo[-1].file_id
  payload = f"p_{message.message_id}"

  products[payload] = {"link": file_link, "price": price_amount}

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(
          f"🛒 Buy Now ({price_amount} ⭐️)", callback_data=f"buy_{payload}"
      )
  )

  bot.send_photo(
      message.chat.id,
      file_id,
      caption=(
          f"✨ **Exclusive Digital Resource**\n\n🔒 Instant secure access"
          f" delivered automatically after paying {price_amount} Telegram"
          f" Stars ⭐️."
      ),
      parse_mode="Markdown",
      reply_markup=markup,
  )
  bot.reply_to(
      message,
      "✅ **Post Ready!** Isko seedha apne channel par forward kar de.",
      parse_mode="Markdown",
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def send_invoice_callback(call):
  payload = call.data.replace("buy_", "")
  if payload not in products:
    bot.answer_callback_query(
        call.id, "⚠️ Product expired or not found!", show_alert=True
    )
    return

  prod_info = products[payload]
  price_amount = prod_info["price"]

  prices = [LabeledPrice(label="Digital Product", amount=price_amount)]

  try:
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Secure Digital Store",
        description=(
            f"Pay {price_amount} Stars to unlock instant secure access link."
        ),
        invoice_payload=payload,
        provider_token="",  # Blank for Telegram Stars (XTR)
        currency="XTR",
        prices=prices,
    )
  except Exception:
    bot.answer_callback_query(
        call.id, "⚠️ Error generating invoice. Try again.", show_alert=True
    )


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
  bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=["successful_payment"])
def got_payment(message):
  payload = message.successful_payment.invoice_payload
  prod_info = products.get(payload)

  if prod_info:
    file_link = prod_info["link"]
    bot.send_message(
        message.chat.id,
        f"🎉 **Payment Successful!**\n\nYeh raha tera secure link:\n{file_link}\n\n⚠️"
        f" *Kripya ise kisi ke sath share na karein.*",
        parse_mode="Markdown",
    )
  else:
    bot.send_message(
        message.chat.id,
        "⚠️ Payment received, but product link expired. Contact admin.",
    )


if __name__ == "__main__":
  # Start Flask server in background thread for Render Free Tier
  t = threading.Thread(target=run_flask)
  t.daemon = True
  t.start()

  # Automatically remove any old webhooks to prevent 409 conflict errors
  try:
    bot.remove_webhook()
  except Exception:
    pass

  print(
      "🚀 Universal Secure Cloud Bot is running 24/7 on Free Tier without"
      " conflicts..."
  )
  bot.infinity_polling()
  
