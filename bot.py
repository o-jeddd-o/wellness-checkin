import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler, JobQueue
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("YOUR_BOT_TOKEN")  # Replace with your actual token

DATA_FILE = 'mood_data.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump({}, file)

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Happy 😊", callback_data='happy')],
        [InlineKeyboardButton("Sad 😔", callback_data='sad')],
        [InlineKeyboardButton("Anxious 😟", callback_data='anxious')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Hello! How are you feeling today?', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    mood = query.data
    await store_mood(query.from_user.id, query.from_user.first_name, mood)

    await query.edit_message_text(text=f"You selected: {mood}")
    await generate_personalized_response(mood, query.message.chat_id, context)

async def store_mood(user_id, user_name, mood):
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    if str(user_id) not in data:
        data[str(user_id)] = {'name': user_name, 'moods': []}

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data[str(user_id)]['moods'].append({'mood': mood, 'timestamp': timestamp})

    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

async def generate_personalized_response(mood, chat_id, context: CallbackContext):
    if mood == 'happy':
        await context.bot.send_message(chat_id=chat_id, text="That's great to hear! Keep spreading positivity. 🌟")
    elif mood == 'sad':
        await context.bot.send_message(chat_id=chat_id, text="I'm sorry to hear that. Maybe try a deep breathing exercise to relax. 🧘")
    elif mood == 'anxious':
        await context.bot.send_message(chat_id=chat_id, text="Feeling anxious can be tough. Here’s an article that might help: [Calm Your Mind](https://example.com)")

async def send_check_in(context: CallbackContext):
    chat_id = context.job.context
    await context.bot.send_message(chat_id=chat_id, text="How are you feeling right now? Please respond with your mood.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Initialize and attach JobQueue to the bot
    job_queue = JobQueue()
    job_queue.set_application(app)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button))

    # Set up periodic check-ins
    job_queue.run_repeating(send_check_in, interval=21600, first=10, context=1184477454)  # Replace with actual chat ID

    # Start the bot
    app.run_polling()