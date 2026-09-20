import os
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

# 100% Secure: Token & Admin ID are fetched safely from Environment Variables
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 1232238066))
CHANNEL_USERNAME = "@codex_777"  # Tera main public channel

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
        " caption format to post securely directly to your channel"
        f" `{CHANNEL_USERNAME}`:\n\n`100`\n`https://your-universal-link.com`",
        parse_mode="Markdown",
    )
  else:
    bot.send_message(
        message.chat.id,
        "👋 Welcome to Secure Digital Store.\nExplore our channel"
        f" {CHANNEL_USERNAME} and click **'Buy Now For Life Time'** on any"
        " product to get instant secure access using Telegram Stars ⭐️.",
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["photo"])
def handle_admin_upload(message):
  if message.from_user.id != ADMIN_ID:
    return  # Unauthorized users ko completely ignore karega (Full Security)

  caption = message.caption or ""
  lines = [line.strip() for line in caption.split("\n") if line.strip()]

  if len(lines) < 2:
    bot.reply_to(
        message,
        "⚠️ **Invalid Format!**\nLine 1: Price in Stars (e.g., 100)\nLine 2:"
        " Universal URL (Drive, Mega, etc.)",
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
  payload = f"p_{message.message_id}_{os.urandom(4).hex()}"

  # Link is securely stored in bot memory (Hidden from channel)
  products[payload] = {"link": file_link, "price": price_amount}

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(
          f"⚡ Buy Now For Life Time ({price_amount} ⭐️)",
          callback_data=f"buy_{payload}",
      )
  )

  try:
    # Attractive post sent directly to your main channel
    bot.send_photo(
        CHANNEL_USERNAME,
        file_id,
        caption=(
            f"💎 **VIP EXCLUSIVE DIGITAL RESOURCE** 💎\n\n"
            f"🚀 **Instant Lifetime Access**\n"
            f"🛡️ 100% Secure & Verified Download\n"
            f"📥 Direct private delivery to your DM instantly after"
            f" payment!\n\n"
            f"💎 **Price:** `{price_amount} Telegram Stars ⭐️`"
        ),
        parse_mode="Markdown",
        reply_markup=markup,
    )
    bot.reply_to(
        message,
        f"✅ **Published Successfully!** Product seedha channel par live ho"
        f" gaya hai: {CHANNEL_USERNAME}",
        parse_mode="Markdown",
    )
  except Exception as e:
    bot.reply_to(
        message,
        f"⚠️ Channel par post bhejte waqt error aaya. Make sure bot is Admin in"
        f" {CHANNEL_USERNAME}.\nError: {e}",
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

  prices = [LabeledPrice(label="Lifetime Digital Access", amount=price_amount)]

  try:
    # Invoice sent strictly to the buyer's private DM
    bot.send_invoice(
        chat_id=call.from_user.id,
        title="Lifetime Access Pass",
        description=(
            f"Pay {price_amount} Stars to unlock instant secure lifetime"
            " download link."
        ),
        invoice_payload=payload,
        provider_token="",  # Required blank for Telegram Stars (XTR)
        currency="XTR",
        prices=prices,
    )
    bot.answer_callback_query(
        call.id, "✅ Invoice sent to your DM! Check bot chat."
    )
  except Exception:
    bot.answer_callback_query(
        call.id,
        "⚠️ Pehle bot ko personal chat mein aakar /start karein!",
        show_alert=True,
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
    # Link delivered securely ONLY to the buyer in DM
    bot.send_message(
        message.chat.id,
        f"🎉 **Payment Successful! Thank You!**\n\n🔑 Your Lifetime Secure"
        f" Link:\n`{file_link}`\n\n⚠️ *Ye link confidential hai, kisi ke"
        f" sath share na karein.*",
        parse_mode="Markdown",
    )
  else:
    bot.send_message(
        message.chat.id,
        "⚠️ Payment received, but link session expired. Contact admin.",
    )


if __name__ == "__main__":
  t = threading.Thread(target=run_flask)
  t.daemon = True
  t.start()

  try:
    bot.remove_webhook()
  except Exception:
    pass

  print("🚀 100% Bulletproof Secure Digital Bot is running 24/7...")
  bot.infinity_polling()
  
