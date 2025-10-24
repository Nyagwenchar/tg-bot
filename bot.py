import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import Database
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
ADMIN_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '0'))
CRYPTO_ADDRESS = os.getenv('CRYPTO_ADDRESS', 'YOUR_CRYPTO_WALLET_ADDRESS')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f'👋 Welcome to our Crypto Store, {user.first_name}!\n\n'
        f'Use /catalog to browse products\n'
        f'Use /orders to view your orders\n'
        f'Use /help for more commands.'
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = db.get_all_products()
    
    if not products:
        await update.message.reply_text('📦 No products available at the moment.')
        return
    
    for product in products:
        keyboard = [[InlineKeyboardButton(
            f"💳 Buy for {product['price']} crypto", 
            callback_data=f"buy_{product['id']}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"🛍️ **{product['name']}**\n\n{product['description']}\n\n💰 Price: {product['price']} crypto"
        
        if product['image_path'] and os.path.exists(product['image_path']):
            try:
                with open(product['image_path'], 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split('_')[1])
    product = db.get_product(product_id)
    
    if not product:
        await query.edit_message_caption(caption='❌ Product not found.')
        return
    
    user = query.from_user
    order_id = db.create_order(user.id, user.username, product_id, CRYPTO_ADDRESS)
    
    payment_text = (
        f"✅ Order #{order_id} created!\n\n"
        f"📦 Product: {product['name']}\n"
        f"💰 Amount: {product['price']} crypto\n\n"
        f"📍 Send payment to:\n`{CRYPTO_ADDRESS}`\n\n"
        f"⚠️ After sending payment, please wait for admin approval.\n"
        f"You will be notified once your order is approved.\n\n"
        f"Order ID: {order_id}"
    )
    
    await query.message.reply_text(payment_text, parse_mode='Markdown')
    
    if ADMIN_ID:
        try:
            admin_text = (
                f"🔔 NEW ORDER RECEIVED\n\n"
                f"Order ID: {order_id}\n"
                f"User: @{user.username} (ID: {user.id})\n"
                f"Product: {product['name']}\n"
                f"Amount: {product['price']} crypto\n"
                f"Payment Address: {CRYPTO_ADDRESS}\n\n"
                f"Use admin panel to approve/reject this order."
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")

async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_orders = db.get_all_orders()
    user_orders = [o for o in all_orders if o['user_id'] == user_id]
    
    if not user_orders:
        await update.message.reply_text('📭 You have no orders yet.')
        return
    
    text = "📋 **Your Orders:**\n\n"
    for order in user_orders:
        status_emoji = {
            'pending': '⏳',
            'payment_received': '💵',
            'approved': '✅',
            'rejected': '❌'
        }.get(order['status'], '❓')
        
        text += (
            f"{status_emoji} Order #{order['id']}\n"
            f"Product: {order['product_name']}\n"
            f"Price: {order['price']} crypto\n"
            f"Status: {order['status']}\n"
            f"Date: {order['created_at']}\n\n"
        )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('❌ Admin only command.')
        return
    
    pending = db.get_pending_orders()
    
    if not pending:
        await update.message.reply_text('✅ No pending orders.')
        return
    
    text = "📋 **Pending Orders:**\n\n"
    for order in pending:
        text += (
            f"Order #{order['id']}\n"
            f"User: @{order['username']} (ID: {order['user_id']})\n"
            f"Product: {order['product_name']}\n"
            f"Price: {order['price']} crypto\n\n"
        )
    
    await update.message.reply_text(text, parse_mode='Markdown')

# --- NEW FUNCTIONS START ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a help message."""
    await update.message.reply_text(
        "Welcome to our Crypto Store!\n\n"
        "Here are the available commands:\n"
        "/start - Start the bot\n"
        "/catalog - Browse our products\n"
        "/orders - View your order history\n"
        "/cancel - Cancel a pending order\n"
        "/help - Show this help message"
    )

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows a user to cancel a pending order."""
    user_id = update.effective_user.id
    all_orders = db.get_all_orders()
    
    # Find orders that are 'pending'
    user_pending_orders = [
        o for o in all_orders 
        if o['user_id'] == user_id and o['status'] == 'pending'
    ]
    
    if not user_pending_orders:
        await update.message.reply_text('📭 You have no pending orders to cancel.')
        return

    keyboard = []
    for order in user_pending_orders:
        keyboard.append([
            InlineKeyboardButton(
                f"❌ Cancel Order #{order['id']} ({order['product_name']})", 
                callback_data=f"cancel_{order['id']}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👇 Select a pending order to cancel:", 
        reply_markup=reply_markup
    )

async def cancel_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the callback for canceling an order."""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split('_')[1])
    order = db.get_order(order_id)
    
    if not order:
        await query.edit_message_text(text='❌ Order not found.')
        return
    
    if order['user_id'] != query.from_user.id:
        await query.edit_message_text(text='❌ This is not your order.')
        return
        
    if order['status'] != 'pending':
        await query.edit_message_text(text=f"This order can no longer be canceled. (Status: {order['status']})")
        return
    
    # Use the existing reject_order function from database.py
    db.reject_order(order_id) 
    
    await query.edit_message_text(
        text=f"✅ Order #{order_id} has been canceled."
    )
    
    # Notify admin
    if ADMIN_ID:
        try:
            admin_text = (
                f"🔔 ORDER CANCELED BY USER\n\n"
                f"Order ID: {order_id}\n"
                f"User: @{query.from_user.username} (ID: {query.from_user.id})\n"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        except Exception as e:
            logger.error(f"Error sending admin notification for cancel: {e}")

# --- NEW FUNCTIONS END ---


async def run_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catalog", catalog))
    application.add_handler(CommandHandler("orders", orders))
    application.add_handler(CommandHandler("admin_orders", admin_orders))
    
    # --- HANDLER MODIFICATIONS START ---
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel_order))
    application.add_handler(CallbackQueryHandler(cancel_order_callback, pattern="^cancel_"))
    # --- HANDLER MODIFICATIONS END ---
    
    application.add_handler(CallbackQueryHandler(buy_product, pattern="^buy_"))
    
    logger.info("Bot started!")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_bot())