import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from database import Database
from dotenv import load_dotenv
import asyncio
from telegram import Bot

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production'))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = Database()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    products = db.get_all_products(active_only=False)
    orders = db.get_all_orders()
    pending_orders = [o for o in orders if o['status'] == 'pending' or o['status'] == 'payment_received']
    return render_template('index.html', products=products, orders=orders, pending_orders=pending_orders)

@app.route('/products')
def products():
    all_products = db.get_all_products(active_only=False)
    return render_template('products.html', products=all_products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        
        if not name or not price:
            flash('Name and price are required!', 'error')
            return redirect(url_for('add_product'))
        
        try:
            price = float(price)
        except ValueError:
            flash('Invalid price!', 'error')
            return redirect(url_for('add_product'))
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_path = filepath
        
        product_id = db.add_product(name, description, price, image_path)
        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('add_product.html')

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = db.get_product(product_id)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        
        if not name or not price:
            flash('Name and price are required!', 'error')
            return redirect(url_for('edit_product', product_id=product_id))
        
        try:
            price = float(price)
        except ValueError:
            flash('Invalid price!', 'error')
            return redirect(url_for('edit_product', product_id=product_id))
        
        image_path = product['image_path']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_path = filepath
        
        db.update_product(product_id, name, description, price, image_path)
        flash(f'Product "{name}" updated successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = db.get_product(product_id)
    if product:
        db.delete_product(product_id)
        flash(f'Product "{product["name"]}" deleted successfully!', 'success')
    else:
        flash('Product not found!', 'error')
    return redirect(url_for('products'))

@app.route('/orders')
def orders_page():
    all_orders = db.get_all_orders()
    return render_template('orders.html', orders=all_orders)

@app.route('/orders/approve/<int:order_id>', methods=['POST'])
def approve_order(order_id):
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    db.approve_order(order_id)
    
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if bot_token:
            async def send_notification():
                bot = Bot(token=bot_token)
                product = db.get_product(order['product_id'])
                message = (
                    f"✅ Your order #{order_id} has been approved!\n\n"
                    f"📦 Product: {order['product_name']}\n"
                    f"💰 Amount: {order['price']} crypto\n\n"
                    f"Thank you for your purchase!"
                )
                
                if product and product['description']:
                    message += f"\n\n📋 Product Details:\n{product['description']}"
                
                await bot.send_message(chat_id=order['user_id'], text=message)
            
            asyncio.run(send_notification())
    except Exception as e:
        print(f"Error sending notification: {e}")
    
    flash(f'Order #{order_id} approved and customer notified!', 'success')
    return redirect(url_for('orders_page'))

@app.route('/orders/reject/<int:order_id>', methods=['POST'])
def reject_order(order_id):
    order = db.get_order(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    db.reject_order(order_id)
    
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if bot_token:
            async def send_notification():
                bot = Bot(token=bot_token)
                message = (
                    f"❌ Your order #{order_id} has been rejected.\n\n"
                    f"📦 Product: {order['product_name']}\n"
                    f"Please contact support if you have questions."
                )
                await bot.send_message(chat_id=order['user_id'], text=message)
            
            asyncio.run(send_notification())
    except Exception as e:
        print(f"Error sending notification: {e}")
    
    flash(f'Order #{order_id} rejected and customer notified.', 'warning')
    return redirect(url_for('orders_page'))

def run_admin():
    port = int(os.getenv('ADMIN_PANEL_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_admin()
