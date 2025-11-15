# Discord Bot - Message Backup & AI Assistant

A Discord bot that combines AI-powered chat with comprehensive message backup and archival capabilities. The bot saves all messages, attachments, and reactions to a database for future reference and export.

## Features

### 🤖 AI Chat
- Ask questions to Gemini AI directly in Discord
- Mention the bot to get AI responses
- Concise 5-line responses by default

### 💾 Message Backup
- **Single-user backup** - Export your own messages
- **Multi-user backup** - Export multiple users' messages
- **Server-wide backup** - Export all messages (admin only)
- **Compact & Detailed formats** - Choose your preferred format
- **Automatic archival** - All messages automatically saved to database

### 📎 Attachment Tracking
- Stores file metadata (name, size, type, URL)
- Tracks download links for later access
- Supports all file types

### 😊 Reaction Logging
- Tracks all emoji reactions on messages
- Records user who reacted and timestamp
- Prevents duplicate reactions

### 📊 Statistics
- View your message count
- Track attachments uploaded
- See statistics across all servers or per-server

---

## Installation

### Prerequisites
- Python 3.10+
- Discord Bot Token
- Google Gemini API Key
- Database URL (SQLite, PostgreSQL, MySQL, etc.)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AbdulWasay2568/Discord-Bot.git
   cd Discord-Bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate     # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   GEMINI_KEY=your_google_gemini_api_key_here
   DATABASE_URL=sqlite:///discord_bot.db
   # For PostgreSQL: postgresql://user:password@localhost/dbname
   # For MySQL: mysql+pymysql://user:password@localhost/dbname
   ```

5. **Initialize database** (automatically done on first run)
   ```bash
   python bot/main.py
   ```

6. **Run the bot**
   ```bash
   python bot/main.py
   ```

---

## Commands

### AI Commands

#### `!ask <question>`
Ask a question to Gemini AI and get a concise answer (max 5 lines).

**Example:**
```
!ask What is the capital of France?
```

#### `!askfile <question>`
Ask a question about an uploaded file (PDF, Image, Excel, CSV, TXT).

**Example:**
```
!askfile Summarize this document
[Attach a PDF or image]
```

---

### Backup Commands

#### `!backup`
Export your own messages to a TXT file.

**Example:**
```
!backup
```

**Output:** Creates `backup_yourname_YYYYMMDD_HHMMSS.txt`

---

#### `!backup @user1 @user2 @user3`
Export messages from multiple specific users.

**Example:**
```
!backup @Alice @Bob @Charlie
```

**Output:** Creates `backup_multiple_YYYYMMDD_HHMMSS.txt`

---

#### `!backup all`
Export all messages from the entire server (admin only).

**Requirements:** You must have administrator permissions

**Example:**
```
!backup all
```

**Output:** Creates `backup_multiple_YYYYMMDD_HHMMSS.txt` with all server messages

---

#### `!backup compact`
Export your messages in compact format (minimal metadata).

**Example:**
```
!backup compact
```

---

#### `!backup @user1 @user2 compact`
Export specific users' messages in compact format.

**Example:**
```
!backup @Alice @Bob compact
```

---

#### `!backup_stats` (or `!bak_stats`)
View your message statistics.

**Example:**
```
!backup_stats
```

**Shows:**
- Total messages (all servers)
- Messages in current server
- Total attachments uploaded

---

#### `!backup_stats @user`
View a specific user's statistics.

**Example:**
```
!backup_stats @Alice
```

---

## How to Download Backup TXT Files

### Method 1: Direct Download from Discord (Recommended)

1. **Run the backup command**
   ```
   !backup
   ```

2. **Bot sends the file** - The bot will reply with a TXT file as an attachment

3. **Download the file**
   - On Desktop: Right-click the file → Download
   - On Mobile: Tap and hold the file → Download

4. **Find your file**
   - Windows: Check your Downloads folder (usually `C:\Users\YourName\Downloads\`)
   - Mac: Check your Downloads folder
   - Mobile: Check your Files app or Downloads folder

---

### Method 2: Export from Discord (Web/Mobile)

1. After the bot sends the backup file, click on the filename
2. Select **Download** from the menu
3. The file will be saved to your default downloads location

---

### Method 3: Copy File from Server Hosting (If self-hosted)

If you're hosting the bot on a server, you can access backups via:
- SSH/SFTP connection to your server
- Web hosting file manager
- Direct server download

---

## Backup File Format

### Detailed Format (Default)
```
================================================================================
DISCORD MESSAGE BACKUP
================================================================================
Generated: 2025-11-15 14:30:45
Server: My Discord Server
Users: alice, bob
Format: Detailed
================================================================================

================================================================================
USER: alice (ID: 123456789)
Total Messages: 45
Date Range: 2025-10-01 to 2025-11-15
================================================================================

================================================================================
Author: alice
Date: 2025-11-15 10:30:22
Channel ID: 987654321
Hi everyone, how's it going?

================================================================================

[More messages...]

================================================================================
BACKUP SUMMARY
Total Users: 2
Total Messages: 127
Export Date: 2025-11-15 14:30:45
================================================================================
```

### Compact Format
```
[2025-11-15 10:30:22] alice:
Hi everyone, how's it going?

[2025-11-15 11:15:45] bob:
All good here!
```

---

## File Naming Convention

- **Single user:** `backup_username_YYYYMMDD_HHMMSS.txt`
  - Example: `backup_alice_20251115_143045.txt`

- **Multiple users:** `backup_multiple_YYYYMMDD_HHMMSS.txt`
  - Example: `backup_multiple_20251115_143045.txt`

---

## Database Schema

### Users Table
Stores Discord user information with unique Discord IDs

**Fields:**
- `discord_id` - Unique Discord user ID
- `username` - User's Discord username
- `discriminator` - User discriminator (e.g., #1234)
- `avatar_url` - Avatar image URL
- `is_bot` - Boolean flag for bot accounts
- `created_at` - Record creation timestamp
- `updated_at` - Last update timestamp

### Messages Table
Stores all messages with metadata

**Fields:**
- `discord_message_id` - Unique message ID
- `user_id` - Foreign key to Users
- `channel_id` - Discord channel ID
- `guild_id` - Discord server/guild ID
- `content` - Message text
- `is_bot_message` - Flag for bot messages
- `created_at` - Message timestamp
- `updated_at` - Last update timestamp

### Attachments Table
Tracks all file attachments

**Fields:**
- `discord_attachment_id` - Unique attachment ID
- `message_id` - Foreign key to Messages
- `filename` - File name
- `url` - Discord CDN download URL
- `content_type` - MIME type
- `size` - File size in bytes
- `created_at` - Upload timestamp

### Reactions Table
Records all emoji reactions

**Fields:**
- `message_id` - Foreign key to Messages
- `user_id` - Foreign key to Users
- `emoji` - Emoji character
- `created_at` - Reaction timestamp
- Unique constraint on (message_id, user_id, emoji)

---

## Requirements

```
discord.py==2.6.4
python-dotenv==1.2.1
google-generativeai==0.8.5
sqlalchemy==2.0+
PyPDF2==3.0.1
pillow==12.0.0
pytesseract==0.3.13
openpyxl==3.1.5
```

See `requirements.txt` for complete list.

---

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | `your-token-here` |
| `GEMINI_KEY` | Google Gemini API key | `your-gemini-key` |
| `DATABASE_URL` | Database connection string | `sqlite:///discord_bot.db` |

### Database URLs

**SQLite (Local, recommended for testing):**
```env
DATABASE_URL=sqlite:///discord_bot.db
```

**PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/discord_bot
```

**MySQL:**
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/discord_bot
```

---

## Permissions Required

### Bot Discord Permissions
- Read Messages/View Channels
- Send Messages
- Read Message History
- Manage Messages
- Add Reactions
- Read Reactions
- Attach Files

### Command Permissions
- `!ask`, `!askfile`, `!backup_stats` - All users
- `!backup (single/multi user)` - All users
- `!backup all` - Administrators only

---

## Troubleshooting

### Bot doesn't respond to commands
- Ensure bot has `Send Messages` permission
- Check that `MESSAGE_CONTENT` intent is enabled
- Verify Discord token is correct in `.env`

### Database errors
- Check `DATABASE_URL` is correct in `.env`
- Ensure database server is running (if using PostgreSQL/MySQL)
- For SQLite, ensure the directory is writable

### Gemini API errors
- Verify API key is valid in `.env`
- Check API quotas on Google Cloud Console
- Ensure API is enabled for your project

### File download issues
- Check Discord client is updated
- Ensure sufficient disk space
- Try a different device or web browser

### Message not saved to database
- Bot wasn't running when message was sent
- Check database connection
- Verify bot has message history permissions

---

## Privacy & Data

⚠️ **Important:** This bot stores all messages and attachments in a local database.

- Messages are stored indefinitely until manually deleted
- Attachment URLs are Discord CDN links (may expire)
- Only admins should run `!backup all` command
- Users can backup and delete their own data

---

## Support & Issues

Found a bug or need help?
- Open an issue on [GitHub](https://github.com/AbdulWasay2568/Discord-Bot/issues)
- Contact: Your contact info here

---

## License

This project is open source. See LICENSE file for details.

---

## Contributors

- **Abdul Wasay** - Main Developer

---

## Changelog

### Version 1.0.0
- ✅ Initial release
- ✅ AI chat with Gemini
- ✅ Single & multi-user backup
- ✅ Message/attachment/reaction tracking
- ✅ Database integration
- ✅ TXT export functionality
- ✅ Statistics command

---

**Last Updated:** November 15, 2025
