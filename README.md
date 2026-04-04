# Made by @Awakeners_Bots
# Telegram File Sharing Bot

A powerful Telegram bot for file sharing with advanced features including batch processing, premium memberships, multi-database channel support, URL shortening with token verification, and comprehensive admin controls.

## ✨ Features

### Core Features
- 📁 **File Sharing** - Share files via unique links with automatic link generation
- 📦 **Batch Processing** - Create batches for episodes/seasons with cancel functionality
- 🤖 **Auto Batch** - Automatic batch creation with quality detection and configurable time windows
- 💎 **Premium System** - Full subscription management with pricing tiers and expiry tracking
- 🗄️ **Multi-DB Channels** - Round-robin file distribution across multiple database channels
- 🔗 **URL Shortening** - Integrated URL shortener with multiple provider support
- 🔐 **Hybrid Token System** - Secure, random 12-16 char token links with full backward compatibility for legacy Base64 links.


### Admin Features
- 👥 **Premium User Management** - Control panel to add/remove premium users with expiry dates
- 📊 **Statistics Dashboard** - Track bot usage, user stats, and premium subscriptions
- 🔒 **Force Subscribe** - Require channel subscription for file access
- 💳 **Credit System** - Token-based access control with package management
- 🔐 **Security Panel** - Token verification, anti-bypass protection, and bypass logs
- 📢 **Broadcast System** - Send messages to all users or specific groups

### User Experience
- 🎨 **Modern UI** - Small caps font styling with blockquotes for premium look
- ⚡ **Fast Performance** - Optimized file delivery and caching
- 🔔 **Notifications** - Auto-notify users on premium status changes
- 📱 **Mobile Friendly** - Responsive design for all devices

## 📋 Requirements

- Python 3.8+
- MongoDB
- Telegram Bot Token (from @BotFather)
- Telegram API ID and Hash (from my.telegram.org)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Awakener_Bots/file-sharing-bot
cd file-sharing-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a `config.py` file based on `.env.example`:

```python
# Bot Configuration
API_ID = 12345678  # Get from my.telegram.org
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

# Database
DATABASE_URI = "mongodb://localhost:27017"
DATABASE_NAME = "file_sharing_bot"

# Channels
DB_CHANNEL = -1001234567890  # Main database channel ID
FORCE_SUB_CHANNELS = []  # List of channel IDs for force subscribe

# Admin
OWNER_ID = 123456789  # Your Telegram user ID
ADMINS = [123456789]  # List of admin user IDs

# Optional
PORT = 8080
WEBHOOK = False
```

### 4. Run the Bot

```bash
python bot.py
```

## 📝 Commands

### User Commands
- `/start` - Start the bot
- `/about` - About the bot
- `/premium` - View premium plans
- `/mypremium` - Check your premium status

### Admin Commands
- `/batch` - Create manual batch
- `/genlink` - Generate link for single file
- `/autobatch` - Configure auto-batch settings
- `/broadcast` - Broadcast message to all users
- `/stats` - View bot statistics
- `/addpremium <user_id> [days]` - Add premium to user
- `/removepremium <user_id>` - Remove premium from user
- `/settings` - Access bot settings panel

## ⚙️ Features Configuration

### Multi-DB Channel System
1. Go to Settings → 🗄️ DB Channels
2. Toggle **Enable Multi-DB**
3. Add extra database channels
4. Files will be distributed automatically using round-robin

### Premium System
- Configure pricing tiers in `plugins/premium.py`
- Users can view plans with `/premium` command
- Admins manage subscriptions with `/addpremium` and `/removepremium`

### Auto Batch
- Automatically groups files by episode or season
- Configurable time window and grouping mode
- Toggle on/off from Settings → 🤖 Auto Batch

### URL Shortener
- Supports multiple shortener providers
- Token verification system
- Anti-bypass protection
- Configure in Settings → URL Shorteners

## 🗂️ Project Structure

```
file-sharing-bot/
├── bot.py                 # Main bot file
├── config.py             # Configuration (create from .env.example)
├── requirements.txt      # Python dependencies
├── plugins/              # Bot plugins
│   ├── start.py         # Start command and file serving
│   ├── batch_handler.py # Batch processing
│   ├── premium.py       # Premium system
│   ├── settings.py      # Settings panel
│   ├── credit.py        # Credit system
│   └── ...
├── helper/              # Helper modules
│   ├── database.py     # MongoDB operations
│   ├── font_converter.py # Small caps conversion
│   └── ...
└── README.md           # This file
```

## 🎨 UI Customization

All user-facing text uses small caps font with blockquote styling for a premium look:

```python
from helper.font_converter import to_small_caps as sc

msg = f"""<blockquote>**{sc('title')}:**</blockquote>

**{sc('field')}:** value
"""
```

## 🔧 Advanced Configuration

### Force Subscribe
Add channel IDs to `FORCE_SUB_CHANNELS` in config.py. Users must join these channels to access files.

### Credit System
- Configure credit costs per file
- Users earn credits through URL shorteners
- Admins can add/remove credits

### Security
- Token verification prevents bypassing shorteners
- Configurable bypass detection timer
- Admin-only sensitive commands

## 📊 Database Schema

The bot uses MongoDB with the following collections:
- `users` - User data and statistics
- `bot_config` - Bot configuration
- `batches` - Batch information
- `credits` - User credit balances

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

**Made by [@Awakeners_Bots](https://t.me/Awakeners_Bots)**

For support and updates, join our channel!

## ⚠️ Disclaimer

This bot is for educational purposes. Ensure you comply with Telegram's Terms of Service and local laws when using this bot.

---

**Star ⭐ this repository if you find it helpful!**
