# Quick Setup Guide

## Step 1: Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send the command: `/newbot`
3. Follow the prompts to create your bot
4. Copy the bot token (it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Get Your Telegram User ID

1. Search for **@userinfobot** on Telegram
2. Start the conversation
3. The bot will show your user ID (a number like: `123456789`)
4. Copy this number

## Step 3: Set Up Environment Variables

### On Replit:
1. Click on the "Secrets" tab (🔒 icon) in the left sidebar
2. Add these secrets:

   - **Key**: `TELEGRAM_BOT_TOKEN`  
     **Value**: Paste your bot token from Step 1
   
   - **Key**: `ADMIN_TELEGRAM_ID`  
     **Value**: Paste your user ID from Step 2
   
   - **Key**: `CRYPTO_ADDRESS`  
     **Value**: Your cryptocurrency wallet address (e.g., Bitcoin, USDT address)
   
   - **Key**: `ADMIN_PASSWORD`  
     **Value**: A strong password to protect your admin panel

3. The app will automatically restart

### On Render or Other Platforms:
1. Create a `.env` file in the project root with:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ADMIN_TELEGRAM_ID=your_user_id_here
   CRYPTO_ADDRESS=your_crypto_wallet_address
   ADMIN_PASSWORD=your_strong_password_here
   ```

## Step 4: Start Using the Bot

### Admin Panel (Web Interface)
- Access the admin panel at the provided webview URL
- **Login** with the password you set in ADMIN_PASSWORD
- Add your first product with an image and description
- Monitor orders as they come in
- **Payment Verification Process**:
  1. Customer places order and receives your crypto address
  2. Order appears in your admin panel as "pending"
  3. Check your crypto wallet to verify payment received
  4. Once confirmed, click "Approve" in admin panel
  5. Customer receives automatic notification with product details

### Telegram Bot (For Your Customers)
Once configured, customers can:
1. Search for your bot on Telegram (use the username you created)
2. Send `/start` to begin
3. Send `/catalog` to see products
4. Click "Buy" to create an order
5. Send crypto to the provided address
6. Wait for your approval

### Admin Commands (Telegram)
As the admin, you can use:
- `/admin_orders` - View all pending orders in Telegram

## Step 5: Test Your Bot

1. Start a conversation with your bot on Telegram
2. Send `/start` - You should get a welcome message
3. In the admin panel, add a test product
4. Send `/catalog` to your bot - You should see the product
5. Try placing an order and approving it from the admin panel

## Troubleshooting

**Bot doesn't respond:**
- Make sure `TELEGRAM_BOT_TOKEN` is correctly set
- Check the workflow logs for errors

**Can't login to admin panel:**
- Verify `ADMIN_PASSWORD` is set in your environment variables
- The app will not start without this password set

**Can't approve orders:**
- Verify `ADMIN_TELEGRAM_ID` is your numeric user ID (not username)

**Images not showing:**
- Make sure you uploaded an image when creating the product
- Check that the image is in a supported format (PNG, JPG, JPEG, GIF, WEBP)

## Need Help?

Check the README.md for more detailed information about features and deployment options.
