import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler
from datetime import datetime
from dotenv import load_dotenv

# Your bot token from the environment or set manually
load_dotenv()
TOKEN = os.getenv("YOUR_BOT_TOKEN")  # Replace with your actual token

# Define the file where mood data will be stored
DATA_FILE = 'mood_data.json'

# Create the mood data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump({}, file)

# Start command to greet users and show mood options
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Happy 😊", callback_data='happy')],
        [InlineKeyboardButton("Sad 😔", callback_data='sad')],
        [InlineKeyboardButton("Anxious 😟", callback_data='anxious')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Hello! How are you feeling today?', reply_markup=reply_markup)

# Handling button press (mood selection)
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Get the mood from the button clicked
    mood = query.data
    await store_mood(query.from_user.id, query.from_user.first_name, mood)

    # Acknowledge the selection
    await query.edit_message_text(text=f"You selected: {mood}")

    # Generate and send personalized response
    await generate_personalized_response(mood, query.message.chat_id, context)

# Store mood in the mood_data.json file
async def store_mood(user_id, user_name, mood):
    # Load existing data
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    # Add new mood entry for the user
    if str(user_id) not in data:
        data[str(user_id)] = {'name': user_name, 'moods': []}

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data[str(user_id)]['moods'].append({'mood': mood, 'timestamp': timestamp})

    # Save updated data
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Generate personalized responses based on mood
async def generate_personalized_response(mood, chat_id, context: CallbackContext):
    if mood == 'happy':
        await context.bot.send_message(chat_id=chat_id, text="That's great to hear! Keep spreading positivity. 🌟")
    elif mood == 'sad':
        await context.bot.send_message(chat_id=chat_id, text="I'm sorry to hear that. Maybe try a deep breathing exercise to relax. 🧘")
    elif mood == 'anxious':
        await context.bot.send_message(chat_id=chat_id, text="Feeling anxious can be tough. Here’s an article that might help: [Calm Your Mind](https://example.com)")

# Function to send scheduled check-in messages
async def send_check_in(chat_id, context):
    while True:
        await context.bot.send_message(chat_id=chat_id, text="How are you feeling right now? Please respond with your mood.")
        await asyncio.sleep(21600)  # Wait for 6 hours

# Main function to run the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Add command handler for /start
    app.add_handler(CommandHandler('start', start))

    # Add callback handler for button presses
    app.add_handler(CallbackQueryHandler(button))

    # Start the check-in task with context
    asyncio.create_task(send_check_in(1184477454, app.context))  # Replace with your actual chat ID

    # Start the bot
    app.run_polling()