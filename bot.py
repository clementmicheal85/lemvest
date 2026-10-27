import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("lemvest")

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/+O_ftPKkrKKxhNzBk")

DISCLAIMER = (
    "⚠️ Educational content only, not financial advice. "
    "Forex trading carries a high risk of loss."
)

LESSONS = {
    "pips": (
        "📘 *What is a pip?*\n\n"
        "A pip is the smallest standard price move in a currency pair. "
        "For most pairs it's the 4th decimal place (0.0001). For JPY pairs, "
        "it's the 2nd decimal place (0.01).\n\n"
        "Example: EUR/USD moving from 1.0850 to 1.0860 = 10 pips."
    ),
    "leverage": (
        "📘 *Leverage & Margin*\n\n"
        "Leverage lets you control a larger position with a smaller deposit "
        "(margin). It magnifies profits *and* losses equally. "
        "Beginners should use low leverage until they understand risk."
    ),
    "risk": (
        "📘 *Risk Management*\n\n"
        "• Risk only 1-2% of your account per trade\n"
        "• Always use a stop-loss\n"
        "• Aim for a risk:reward of at least 1:2\n"
        "• Never trade money you can't afford to lose"
    ),
    "candles": (
        "📘 *Candlestick Basics*\n\n"
        "Each candle shows open, high, low and close for a period. "
        "A green (bullish) candle closes higher than it opened; a red "
        "(bearish) one closes lower. Long wicks show rejection of a price level."
    ),
    "sessions": (
        "📘 *Trading Sessions*\n\n"
        "Forex runs 24h across four main sessions: Sydney, Tokyo, London and "
        "New York. Volatility is highest when sessions overlap, especially "
        "London/New York."
    ),
}


def channel_button() -> InlineKeyboardButton:
    return InlineKeyboardButton("🚀 Join Lemvest Channel", url=CHANNEL_URL)


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📚 Start Learning", callback_data="menu_learn")],
            [channel_button()],
        ]
    )


def learn_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Pips", callback_data="lesson_pips"),
                InlineKeyboardButton("Leverage", callback_data="lesson_leverage"),
            ],
            [
                InlineKeyboardButton("Risk", callback_data="lesson_risk"),
                InlineKeyboardButton("Candles", callback_data="lesson_candles"),
            ],
            [InlineKeyboardButton("Sessions", callback_data="lesson_sessions")],
            [channel_button()],
        ]
    )


def after_lesson_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [channel_button()],
            [InlineKeyboardButton("⬅️ More Lessons", callback_data="menu_learn")],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name if update.effective_user else "trader"
    text = (
        f"👋 Welcome to *Lemvest*, {name}!\n\n"
        "Learn forex basics here, then join our channel for daily insights, "
        "market breakdowns and community discussion.\n\n"
        f"{DISCLAIMER}"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=main_menu()
    )


async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Pick a topic to learn 👇", reply_markup=learn_menu()
    )


async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Get daily forex education and updates in our channel 👇",
        reply_markup=InlineKeyboardMarkup([[channel_button()]]),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start - Welcome\n/learn - Forex lessons\n/channel - Join our channel\n/help - This menu"
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_learn":
        await query.edit_message_text(
            "Pick a topic to learn 👇", reply_markup=learn_menu()
        )
    elif data.startswith("lesson_"):
        key = data.replace("lesson_", "")
        lesson = LESSONS.get(key, "Lesson not found.")
        await query.edit_message_text(
            f"{lesson}\n\n_Want daily lessons like this? Join the channel._\n\n{DISCLAIMER}",
            parse_mode="Markdown",
            reply_markup=after_lesson_menu(),
        )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Thanks for your message! For lessons use /learn, or join the channel "
        "for daily education and updates 👇",
        reply_markup=InlineKeyboardMarkup([[channel_button()]]),
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled error", exc_info=context.error)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("learn", learn))
    app.add_handler(CommandHandler("channel", channel))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    app.add_error_handler(on_error)

    logger.info("Lemvest bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
