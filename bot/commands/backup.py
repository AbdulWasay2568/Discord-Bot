"""
Backup command - Export messages to TXT format
Allowed usages (admin only):
    - `!backup all` -> backup all users in server
    - `!backup @user1 @user2` -> backup specific users
    - `!backup_stats` -> show stats for all users
    - `!backup_stats @user` -> show stats for specific user
"""
import sys
from pathlib import Path
import discord
from discord.ext import commands
from io import BytesIO
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db.db_utils import SessionLocal, get_message_attachments
from models.user import User
from models.message import Message

def format_message_content(message, attachments, include_metadata=True):
    """Format a message with all its metadata"""
    formatted = f"\n{'='*80}\n"
    if include_metadata:
        formatted += f"Author: {message.user.username}\n"
        formatted += f"Date: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        formatted += f"Channel ID: {message.channel_id}\n"
    else:
        formatted += f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.user.username}:\n"
    
    if message.content:
        formatted += f"{message.content}\n"
    
    if attachments:
        formatted += f"\n📎 Attachments ({len(attachments)}):\n"
        for i, attachment in enumerate(attachments, 1):
            size_mb = attachment.size / (1024 * 1024) if attachment.size else 0
            formatted += f"  {i}. {attachment.filename} ({size_mb:.2f} MB)\n"
            if include_metadata:
                formatted += f"     URL: {attachment.url}\n"
    
    formatted += f"{'='*80}\n"
    return formatted

def generate_txt_backup(target_users, db, ctx, compact=False):
    """Generate TXT format backup"""
    backup_content = f"DISCORD MESSAGE BACKUP\n"
    backup_content += f"{'='*80}\n"
    backup_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    backup_content += f"Server: {ctx.guild.name if ctx.guild else 'Direct Message'}\n"
    backup_content += f"Users: {', '.join(u.name for u in target_users)}\n"
    backup_content += f"Format: {'Compact' if compact else 'Detailed'}\n"
    backup_content += f"{'='*80}\n\n"
    
    total_messages = 0

    bot_db_user = db.query(User).filter(User.discord_id == str(ctx.bot.user.id)).first() if ctx and ctx.bot and ctx.bot.user else None

    for user in target_users:
        db_user = db.query(User).filter(User.discord_id == str(user.id)).first()

        if not db_user:
            backup_content += f"\n--- No messages found for {user.name} ---\n"
            continue

        user_messages = db.query(Message).filter(
            Message.user_id == db_user.id,
            Message.guild_id == ctx.guild.id
        ).order_by(Message.created_at).all()

        if not user_messages:
            backup_content += f"\n--- No messages found for {user.name} in this server ---\n"
            continue

        merged_messages = list(user_messages)
        if bot_db_user:
            channel_ids = list({m.channel_id for m in user_messages})
            if channel_ids:
                bot_messages = db.query(Message).filter(
                    Message.user_id == bot_db_user.id,
                    Message.guild_id == ctx.guild.id,
                    Message.channel_id.in_(channel_ids)
                ).order_by(Message.created_at).all()

                merged_messages.extend(bot_messages)
                merged_messages.sort(key=lambda m: m.created_at)

        backup_content += f"\n{'*'*80}\n"
        backup_content += f"USER: {user.name} (ID: {user.id})\n"
        backup_content += f"Total Messages: {len(user_messages)}\n"
        backup_content += f"Date Range: {user_messages[0].created_at.date()} to {user_messages[-1].created_at.date()}\n"
        backup_content += f"{'*'*80}\n"

        for message in merged_messages:
            attachments = get_message_attachments(db, message.id)
            backup_content += format_message_content(message, attachments, include_metadata=not compact)

        total_messages += len(user_messages)
    
    backup_content += f"\n\n{'='*80}\n"
    backup_content += f"BACKUP SUMMARY\n"
    backup_content += f"Total Users: {len(target_users)}\n"
    backup_content += f"Total Messages: {total_messages}\n"
    backup_content += f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    backup_content += f"{'='*80}\n"
    
    return backup_content, total_messages

@commands.command(name="backup", aliases=["bak", "export"])
async def backup(ctx, *args):
    """
    Admin-only backup command.

    Usage:
      !backup all                -> Backup all users in server (admin only)
      !backup @user1 @user2 ...  -> Backup specific users (admin only)
    """
    db = SessionLocal()

    try:
        # Only administrators can run backups
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("⚠️ Only administrators can run backups.")
            return

        if not args:
            await ctx.reply("⚠️ Usage: `!backup all` or `!backup @user1 @user2 ...` (admin only)")
            return

        target_users = []

        if len(args) == 1 and args[0].lower() == "all":
            db_messages = db.query(Message).filter(Message.guild_id == ctx.guild.id).all()
            seen_user_ids = set(msg.user_id for msg in db_messages)

            if not seen_user_ids:
                await ctx.reply("⚠️ No messages found in database for this server.")
                return

            db_users = db.query(User).filter(User.id.in_(seen_user_ids)).all()
            for db_user in db_users:
                try:
                    target_users.append(await ctx.bot.fetch_user(int(db_user.discord_id)))
                except:
                    pass

        else:
            mentions = []
            for arg in args:
                if arg.startswith('<@') and arg.endswith('>'):
                    try:
                        user_id = int(arg.strip('<@!>'))
                        user = await ctx.bot.fetch_user(user_id)
                        mentions.append(user)
                    except:
                        pass

            if not mentions:
                await ctx.reply("⚠️ You must specify one or more user mentions, or use `all`.")
                return

            target_users = mentions

        if not target_users:
            await ctx.reply("⚠️ No valid users found to backup.")
            return

        backup_content, total_messages = generate_txt_backup(target_users, db, ctx)

        backup_bytes = backup_content.encode('utf-8')
        backup_file = BytesIO(backup_bytes)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if len(target_users) == 1:
            filename = f"backup_{target_users[0].name}_{timestamp}.txt"
        else:
            filename = f"backup_multiple_{timestamp}.txt"

        await ctx.reply(
            f"✅ Backup created! ({total_messages} messages from {len(target_users)} user(s))",
            file=discord.File(backup_file, filename)
        )

    except Exception as e:
        await ctx.reply(f"⚠️ Error creating backup: {str(e)}")

    finally:
        db.close()

@commands.command(name="backup_stats", aliases=["bak_stats"])
async def backup_stats(ctx, user: discord.User = None):
    db = SessionLocal()

    try:
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("⚠️ Only administrators can view backup stats.")
            return

        target_user = user

        if target_user:
            db_user = db.query(User).filter(User.discord_id == str(target_user.id)).first()

            if not db_user:
                await ctx.reply(f"⚠️ No messages found for {target_user.name}")
                return

            total_messages = db.query(Message).filter(Message.user_id == db_user.id).count()
            guild_messages = db.query(Message).filter(
                Message.user_id == db_user.id,
                Message.guild_id == ctx.guild.id
            ).count()

            from sqlalchemy import func
            from models.attachment import Attachment
            
            user_messages = db.query(Message.id).filter(Message.user_id == db_user.id).subquery()
            total_attachments = db.query(func.count(Attachment.id)).filter(
                Attachment.message_id.in_(user_messages)
            ).scalar()

            embed = discord.Embed(
                title=f"Backup Stats for {target_user.name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Total Messages (All Servers)", value=total_messages, inline=False)
            embed.add_field(name="Messages (This Server)", value=guild_messages, inline=False)
            embed.add_field(name="Total Attachments", value=total_attachments or 0, inline=False)
            embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else None)

            await ctx.reply(embed=embed)
            return

        total_messages = db.query(Message).filter(Message.guild_id == ctx.guild.id).count()
        from sqlalchemy import func
        from models.attachment import Attachment
        user_messages = db.query(Message.id).filter(Message.guild_id == ctx.guild.id).subquery()
        total_attachments = db.query(func.count(Attachment.id)).filter(
            Attachment.message_id.in_(user_messages)
        ).scalar()

        embed = discord.Embed(
            title=f"Server Backup Stats for {ctx.guild.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Messages (This Server)", value=total_messages, inline=False)
        embed.add_field(name="Total Attachments (This Server)", value=total_attachments or 0, inline=False)
        await ctx.reply(embed=embed)
    except Exception as e:
        await ctx.reply(f"⚠️ Error fetching stats: {str(e)}")

    finally:
        db.close()
