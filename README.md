# Discord Bot - Message Archival & AI Assistant

A Discord bot combining AI-powered conversation with comprehensive message archival, attachment tracking, and advanced filtering. The bot automatically saves all messages, reactions, embeds, and attachments to a PostgreSQL database for later analysis and export.

## 🎯 Features

### 🤖 AI Chat
- Ask Gemini AI questions directly in Discord using `/ask` command
- File-based AI queries with `/askfile` - Ask questions about uploaded files
- Concise 5-line responses optimized for Discord

### 💾 Message Archival
- **Automatic message saving** - All user messages are automatically archived to the database
- **Reaction tracking** - Every emoji reaction is logged with user and timestamp
- **Attachment archival** - Files are downloaded and stored locally with metadata
- **Edit/Delete tracking** - Message modifications and deletions are recorded
- **Reference tracking** - Reply chains and message references are preserved
- **Batch processing** - 100 messages per database call for optimized performance

### 🔍 Advanced Message Filtering
- `/list` command with interactive filters:
  - **Channel selection** - Searchable dropdown (multi-select)
  - **Member selection** - Searchable dropdown (multi-select)
  - **Date range** - From/To date filtering
  - **Attachment filtering** - Search for specific file names
  - **Reaction filtering** - Find messages with specific emojis
  - **Sort options** - By creation date (asc/desc) or by reaction count
  - **Limit results** - Configurable result count
- Exports results as downloadable TXT file (ephemeral)
- Includes full message content, metadata, attachments, and reactions

### 📎 Attachment Management
- Downloads and stores attachments locally (organized by message ID)
- Tracks metadata: filename, size, content type, URL
- Stores both Discord URLs and local file paths
- Supports all file types

### 😊 Reaction System
- Logs all emoji reactions (custom and standard)
- Records which users reacted and when
- Tracks reaction counts and burst reactions
- Prevents duplicate entries

### ⚡ Channel Reconciliation
- `/reconcile` - Sync current channel with Discord history (ephemeral response)
- `/backfill` - Backfill older messages before the latest archived message (ephemeral response)
- Batch processes 100 messages per iteration
- Tracks reconciliation time and progress

---

## 📋 Available Commands

All commands use Discord's slash command system (`/`)

| Command | Description
|---------|-------------
| `/ask <prompt>` | Ask Gemini AI a question
| `/askfile <file> <prompt>` | Ask about an uploaded file
| `/list` | Advanced message filtering with UI
| `/reconcile` | Sync current channel with Discord history
| `/backfill` | Backfill older messages

---

## 🗂️ Project Structure

```
Discord/
├── bot/
│   ├── commands/           # Slash commands
│   │   ├── ask.py         # AI question command
│   │   ├── askfile.py     # File-based AI queries
│   │   ├── list.py        # Advanced filtering with dropdowns
│   │   ├── reconcile.py   # Channel sync command
│   │   ├── backfill.py    # Message backfill command
│   │   └── __init__.py    # Command registration
│   ├── utils/
│   │   ├── db_handler.py        # Message/reaction handlers
│   │   ├── ai.py                # Gemini AI integration
│   │   ├── file_manager.py      # Attachment download/storage
│   │   ├── file_reader.py       # File parsing utilities
│   │   └── response_time.py     # Timing utilities
│   ├── config/
│   │   └── settings.py          # Configuration (token, API keys)
│   ├── attachments/             # Downloaded files (organized by message ID)
│   └── main.py                  # Bot initialization & event handlers
├── db/
│   ├── schema.py           # SQLAlchemy models (User, Message)
│   ├── connection.py       # Async database session setup
│   ├── db_utils.py         # Database utilities
│   └── queries/
│       ├── messages.py     # Message CRUD & batch operations
│       ├── user.py         # User operations
│       ├── attachments.py  # Attachment queries
│       └── reactions.py    # Reaction queries
├── migrations/             # Alembic migration history
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
└── README.md              # This file
```

---

## 🛠️ Tech Stack

- **Discord.py** 2.6.4 - Discord bot framework with slash commands
- **SQLAlchemy** 2.0.44 - Async ORM for PostgreSQL
- **Alembic** 1.17.2 - Database migrations
- **Google Generative AI** 0.8.5 - Gemini AI integration
- **PostgreSQL** - Primary database
- **Python** 3.10+

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Discord bot token (from Discord Developer Portal)
- Google Gemini API key (from Google AI Studio)

### Setup Steps

1. **Clone and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp env\ Example.md .env
   # Edit .env with your credentials:
   # - DISCORD_TOKEN
   # - GOOGLE_API_KEY
   # - DATABASE_URL (PostgreSQL connection string)
   ```

3. **Initialize database**
   ```bash
   alembic upgrade head
   ```

4. **Run the bot**
   ```bash
   python -m bot
   ```

---

## 🗄️ Database Schema

### Users Table
- `id` (BigInteger) - Discord User ID
- `username` - Discord username
- `discriminator` - User discriminator (usually "0" for modern accounts)
- `global_name` - Display name
- `avatar` - Avatar URL
- `bot` - Is bot account
- `system` - Is system account

### Messages Table
- `id` (BigInteger) - Discord Message ID
- `channel_id` - Channel where message was sent
- `author_id` (FK) - Message author (User)
- `content` - Message text content
- `timestamp` - When message was created
- `edited_timestamp` - When message was last edited (nullable)
- `type` - Message type (DEFAULT, REPLY, etc.)
- `attachments` (JSON) - File metadata array
- `embeds` (JSON) - Embed data array
- `reactions` (JSON) - Reaction data with user IDs
- `message_reference` (JSON) - Reply reference info
- `referenced_message` (JSON) - Full reference message data

---

## ⚙️ Configuration

### Bot Settings
Located in `bot/config/settings.py`:
- Discord intents configuration
- Batch size for message operations (default: 100)
- Sleep duration between Discord history requests (default: 0.05s)

### AI Configuration
- Model: Gemini 1.5 Flash (via `bot/utils/ai.py`)
- Max response: 5 lines
- Can process text files (PDF, TXT, etc.)

### Database
- Async SQLAlchemy sessions for non-blocking operations
- Connection pooling via `db/connection.py`
- Batch operations for performance (100 messages per commit)

---

## 🚀 Performance Optimizations

1. **Batch Message Processing**
   - Inserts 100 messages per database transaction
   - Reduces database round trips by 50x compared to individual inserts
   - Reconciliation processes ~600 messages in ~2 minutes

2. **Attachment Caching**
   - Downloads stored locally to `bot/attachments/<message_id>/`
   - Prevents re-downloading same files
   - Tracks local path in database

3. **Reaction Deduplication**
   - Prevents storing duplicate reactions for same user+emoji
   - Updates count instead of duplicating entries

4. **Async Operations**
   - All I/O is non-blocking (Discord API, database, file operations)
   - Handles multiple events concurrently

---

## 📝 Usage Examples

### Archive Messages from a Channel
```
/reconcile
```
Bot will sync the current channel, downloading all messages not yet in database.

### Search Messages with Filters
```
/list
→ Select channels via dropdown
→ Select members via dropdown  
→ Set date range (optional)
→ Select reactions to filter by (optional)
→ Click "Submit"
→ Download results as TXT file
```

### Ask AI a Question
```
/ask What is machine learning?
```
Bot replies with concise answer (max 5 lines).

### Ask AI About a File
```
/askfile [attach PDF] Summarize this document
```
Bot analyzes the file and responds.

---

## 🔒 Privacy & Permissions

- Bot only processes messages it can read (requires channel access)
- No message filtering based on user roles
- Stores all message data including content and attachments
- Recommendation: Run in private servers or with appropriate data governance

---

## 🐛 Known Issues & Limitations

1. **Discord Discriminators** - Modern Discord accounts have discriminator "0" (this is expected)
2. **Dropdown Limit** - Max 25 channels/members per dropdown (Discord API limit). Large guilds need pagination
3. **Ephemeral Messages** - Slash command interactions don't appear in message history (by design)
4. **File Size** - Large attachments may take time to download; stored locally with full paths

---

## 📊 Database Migrations

Managed with Alembic. Key migrations include:
- Initial schema with cascade delete
- Message reference and reply tracking
- Message type enums
- JSON field optimization for reactions/embeds/attachments

Create new migration after schema changes:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 🤝 Contributing

When adding new commands:
1. Create file in `bot/commands/`
2. Define async function with `@app_commands.command()` decorator
3. Register in `bot/commands/__init__.py`
4. Add to `setup_commands()` function

When modifying database:
1. Update models in `db/schema.py`
2. Create Alembic migration
3. Add corresponding query function in `db/queries/`

---

## 📄 License

[Add your license here]

---

## 👥 Support

For issues or questions, please check:
- Discord Developer Portal docs: https://discord.com/developers/docs
- Discord.py documentation: https://discordpy.readthedocs.io
- SQLAlchemy async guide: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

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

## Privacy & Data

⚠️ **Important:** This bot stores all messages and attachments in a local database.

- Messages are stored indefinitely until manually deleted
- Only admins should run `!backup all` command

---

## Support & Issues

Found a bug or need help?
- Open an issue on [GitHub](https://github.com/AbdulWasay2568/Discord-Bot/issues)
- Contact: Your contact info here

---

## License

This project is open source. See LICENSE file for details.

---
