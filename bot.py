from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = '7620234949:AAESoN1w-ClJKfNIlxInqmZuI6uj_K-t8Ns'

async def start(update: Update, context):
    await update.message.reply_text('Hello! I am your wellness check-in bot.')

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as file:
        json.dump({}, file)

async def start(update: Update, context):
    await update.message.reply_text('Hello! How are you feeling today?')

async def log_mood(update: Update, context):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    mood = update.message.text

    # Load existing data
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    # Add new mood entry for the user
    if str(user_id) not in data:
        data[str(user_id)] = {'name': user_name, 'moods': []}
    
    data[str(user_id)]['moods'].append({'mood': mood, 'timestamp': update.message.date.isoformat()})

    # Save the updated data back to the file
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

    await update.message.reply_text(f"Got it! I've logged your mood as '{mood}'.")
    
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    app.run_polling()