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
        f'Use /orders to view your orders'
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

def run_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catalog", catalog))
    application.add_handler(CommandHandler("orders", orders))
    application.add_handler(CommandHandler("admin_orders", admin_orders))
    application.add_handler(CallbackQueryHandler(buy_product, pattern="^buy_"))
    
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    run_bot()
