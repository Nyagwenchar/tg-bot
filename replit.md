# Telegram Crypto Payment Bot - Replit Project

## Overview
A Telegram bot with crypto payment processing and web-based admin panel for managing and selling products.

## Project Status
Complete implementation with:
- Telegram bot for customer interactions
- Flask admin panel for product and order management
- SQLite database for data persistence
- Support for deployment on Replit and Render

## Tech Stack
- **Backend**: Python 3.11
- **Bot Framework**: python-telegram-bot
- **Web Framework**: Flask
- **Database**: SQLite
- **Frontend**: HTML/CSS (no external dependencies)

## Environment Variables Required
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `ADMIN_TELEGRAM_ID`: Your Telegram user ID (numeric)
- `CRYPTO_ADDRESS`: Your cryptocurrency wallet address for payments
- `SESSION_SECRET`: Used for Flask session security (auto-generated on Replit)

## Key Features
1. Product catalog with images in Telegram
2. Order creation and crypto payment instructions
3. Admin notifications for new orders
4. Web-based admin panel for managing products
5. Order approval/rejection with automatic customer notifications
6. Order tracking for both customers and admin

## Architecture
- **main.py**: Runs both bot and admin panel in parallel threads
- **bot.py**: Handles all Telegram interactions
- **admin.py**: Flask web server for admin interface
- **database.py**: SQLite database layer
- **templates/**: HTML templates for admin panel

## Recent Changes
- Initial project setup (Oct 23, 2025)
- Complete bot implementation with order workflow
- Admin panel with product management
- Integrated notification system
- Deployment configuration for multiple platforms
