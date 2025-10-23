# Telegram Crypto Payment Bot

A Telegram bot with crypto payment processing and an admin panel for selling products.

## Features

- **Telegram Bot**: Browse products, place orders, and receive payment instructions
- **Admin Panel**: Web interface to manage products and orders
- **Product Management**: Add/edit/delete products with images and descriptions
- **Order Management**: Track orders, approve/reject payments, and notify customers
- **Crypto Payments**: Display payment addresses and track order status

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token you receive

### 2. Get Your Telegram User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start the bot to see your user ID
3. Copy your numeric user ID

### 3. Configure Environment Variables

Create a `.env` file in the project root with the following:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_TELEGRAM_ID=your_telegram_user_id_here
CRYPTO_ADDRESS=your_crypto_wallet_address_here
ADMIN_PASSWORD=your_strong_admin_password_here
ADMIN_PANEL_PORT=5000
```

### 4. Run the Application

The bot and admin panel will start automatically. Access the admin panel at:
- **Replit**: Use the webview URL provided
- **Local/Render**: http://localhost:5000

## Usage

### For Customers (Telegram)

1. Start the bot: `/start`
2. Browse products: `/catalog`
3. Click "Buy" to place an order
4. Send crypto to the provided address
5. Wait for admin approval
6. Check order status: `/orders`

### For Admins (Web Panel)

1. Open the admin panel in your browser
2. Login with your admin password
3. Add products with images and descriptions
4. Monitor pending orders on the dashboard
5. **Payment Verification**:
   - Check your crypto wallet for incoming payments
   - Match payment amount with order price
   - Approve order once payment confirmed
6. Orders can be approved or rejected (customers are notified automatically)
7. View all orders and products history

## Deployment

### Deploying to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. Add environment variables in Render settings:
   - `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather
   - `ADMIN_TELEGRAM_ID` - Your Telegram user ID
   - `CRYPTO_ADDRESS` - Your crypto wallet address
   - `ADMIN_PASSWORD` - A strong password for admin panel
   - `ADMIN_PANEL_PORT` - Set to `5000`
5. Deploy!

**Note**: The `render.yaml` file is included for easy deployment, but you'll still need to add the secret environment variables manually in Render's dashboard.

### Deploying on Replit

1. The project is already configured for Replit
2. Add your environment variables in the Secrets tab
3. Run the project

## Project Structure

```
.
├── main.py              # Main application entry point
├── bot.py               # Telegram bot implementation
├── admin.py             # Flask admin panel
├── database.py          # SQLite database models
├── templates/           # HTML templates for admin panel
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── add_product.html
│   ├── edit_product.html
│   └── orders.html
├── uploads/             # Product images
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not in git)
```

## Database

The application uses SQLite with two main tables:
- **products**: Store product information (name, description, price, image)
- **orders**: Track customer orders and payment status

## Security Notes

- Never commit your `.env` file
- Keep your bot token and API keys secret
- Use a strong password for ADMIN_PASSWORD
- For production, use environment variables
- Admin panel requires password authentication
- Payment verification is manual - always verify crypto wallet before approving orders

## Support

For issues or questions, please contact the admin.
