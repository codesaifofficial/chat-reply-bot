from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

TOKEN = 'YOUR_BOT_API_TOKEN'
ADMIN_CHAT_ID = 'YOUR_ADMIN_CHAT_ID'

# Function to read chat_ids from data.txt and return them as a list
def get_chat_ids():
    try:
        with open("data.txt", "r") as file:
            chat_ids = file.readlines()
            chat_ids = [chat_id.strip() for chat_id in chat_ids]  # Remove extra spaces or new lines
    except FileNotFoundError:
        chat_ids = []  # If file doesn't exist, return an empty list
    return chat_ids

# Function to write new chat_id to data.txt (if not already present)
def store_chat_id(chat_id):
    chat_ids = get_chat_ids()
    if str(chat_id) not in chat_ids:  # Avoid storing duplicate chat_ids
        with open("data.txt", "a") as file:
            file.write(f"{chat_id}\n")  # Store chat_id in a new line
        print(f"Stored chat_id: {chat_id}")
    else:
        print(f"Chat_id {chat_id} is already in the list.")

# Function to send welcome message and start options
def start(update, context):
    user_id = update.message.chat_id
    username = update.message.from_user.username
    
    # Store chat_id if it's the user's first time
    store_chat_id(user_id)

    keyboard = [
        [InlineKeyboardButton("Join my channel", url="https://t.me/mychannel123")],
        [InlineKeyboardButton("Chat with Admin", callback_data='chat_admin')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Hey @{username}! 👋 Welcome to our bot! How can I assist you today? 😊", reply_markup=reply_markup)

# Function to handle user messages and forward to admin
def handle_message(update, context):
    user_message = update.message.text
    user_id = update.message.chat_id
    username = update.message.from_user.username

    # Forward message to admin chat
    message_to_admin = f"New message from @{username} (User ID: {user_id}):\n{user_message}"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin)

    # Acknowledge user message with a friendly response
    update.message.reply_text(f"Thank you for reaching out, @{username}! 😊 Your message: '{user_message}' has been recorded. Admin will reply soon. 🕒")

# Function to initiate chat with admin
def chat_with_admin(update, context):
    update.message.reply_text("You are now chatting with the admin. Please wait for a reply. 🤝")

# Function to reply to a user (admin only)
def reply_to_user(update, context):
    # Check if the command is from admin
    if update.message.chat_id != int(ADMIN_CHAT_ID):
        return update.message.reply_text("You are not authorized to reply. 🙅‍♂️")
    
    # Extract user_id and message from the command
    try:
        user_id = int(context.args[0])  # First argument is the user_id
        reply_message = ' '.join(context.args[1:])  # Rest is the reply message
        
        # Send the reply message to the user
        context.bot.send_message(chat_id=user_id, text=reply_message)
        update.message.reply_text(f"Replied to user {user_id}: {reply_message} ✅")
    
    except (IndexError, ValueError):
        update.message.reply_text("Please use the correct format: /reply <user_id> <message>. 📝")

# Function to send broadcast message to all users
def broadcast(update, context):
    # Only admin can send broadcast
    if update.message.chat_id != int(ADMIN_CHAT_ID):
        return update.message.reply_text("You are not authorized to send a broadcast. 🙅‍♂️")
    
    # Get the message from the command args
    message = ' '.join(context.args)  # All args after command will be the message to broadcast
    
    if not message:
        return update.message.reply_text("Please provide a message to broadcast.")
    
    # Read all chat_ids from data.txt
    chat_ids = get_chat_ids()

    # Send the message to all users
    for chat_id in chat_ids:
        try:
            context.bot.send_message(chat_id=chat_id, text=message)
            print(f"Sent message to {chat_id}")
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

    update.message.reply_text(f"Broadcast message sent to {len(chat_ids)} users! 🎉")

# Function to start the bot and handle updates
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(chat_with_admin, pattern='chat_admin'))
    dp.add_handler(CommandHandler('reply', reply_to_user, pass_args=True))  # Admin reply functionality
    dp.add_handler(CommandHandler('broadcast', broadcast, pass_args=True))  # Admin broadcast functionality

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
