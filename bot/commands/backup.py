"""
Backup command - Export messages to TXT format
Supports single user and multi-user backups with multiple export formats
"""
import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from db.db_utils import SessionLocal, get_user_messages, get_message_attachments
from models.user import User
from models.message import Message
from io import BytesIO
from datetime import datetime

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
    
    # Get messages for each user
    for user in target_users:
        db_user = db.query(User).filter(User.discord_id == str(user.id)).first()
        
        if not db_user:
            backup_content += f"\n--- No messages found for {user.name} ---\n"
            continue
        
        # Get user's messages
        user_messages = db.query(Message).filter(
            Message.user_id == db_user.id,
            Message.guild_id == ctx.guild.id
        ).order_by(Message.created_at).all()
        
        if not user_messages:
            backup_content += f"\n--- No messages found for {user.name} in this server ---\n"
            continue
        
        backup_content += f"\n{'*'*80}\n"
        backup_content += f"USER: {user.name} (ID: {user.id})\n"
        backup_content += f"Total Messages: {len(user_messages)}\n"
        backup_content += f"Date Range: {user_messages[0].created_at.date()} to {user_messages[-1].created_at.date()}\n"
        backup_content += f"{'*'*80}\n"
        
        for message in user_messages:
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
    Backup messages from user(s) to a TXT file.
    Usage:
      !backup - Backup your own messages
      !backup @user1 @user2 - Backup specific users
      !backup all - Backup all users in server (admin only)
      !backup compact - Compact format (less metadata)
      !backup @user1 @user2 compact - Specific users in compact format
    """
    db = SessionLocal()
    
    try:
        # Parse arguments
        target_users = []
        compact = False
        
        # Check if last argument is "compact"
        if args and args[-1].lower() == "compact":
            compact = True
            args = args[:-1]
        
        # Convert string mentions to User objects
        mentions = []
        for arg in args:
            if arg.startswith('<@') and arg.endswith('>'):
                # Handle mention format
                try:
                    user_id = int(arg.strip('<@!>'))
                    user = await ctx.bot.fetch_user(user_id)
                    mentions.append(user)
                except:
                    pass
        
        if not mentions and not args:
            # Backup requesting user's messages
            target_users = [ctx.author]
        elif mentions:
            target_users = mentions
        elif args and args[0].lower() == "all":
            # Backup all users (admin only)
            if not ctx.author.guild_permissions.administrator:
                await ctx.reply("⚠️ Only administrators can backup all users.")
                return
            
            # Get all unique users from database in this guild
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
        
        if not target_users:
            await ctx.reply("⚠️ No valid users found to backup.")
            return
        
        # Generate backup content
        backup_content, total_messages = generate_txt_backup(target_users, db, ctx, compact)
        
        # Convert to file
        backup_bytes = backup_content.encode('utf-8')
        backup_file = BytesIO(backup_bytes)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if len(target_users) == 1:
            filename = f"backup_{target_users[0].name}_{timestamp}.txt"
        else:
            filename = f"backup_multiple_{timestamp}.txt"
        
        # Send file
        format_type = "compact" if compact else "detailed"
        await ctx.reply(
            f"✅ Backup created! ({total_messages} messages from {len(target_users)} user(s)) [{format_type}]",
            file=discord.File(backup_file, filename)
        )
        
    except Exception as e:
        await ctx.reply(f"⚠️ Error creating backup: {str(e)}")
    
    finally:
        db.close()

@commands.command(name="backup_stats", aliases=["bak_stats"])
async def backup_stats(ctx, user: discord.User = None):
    """
    Show message statistics for a user
    Usage:
      !backup_stats - Show your stats
      !backup_stats @user - Show specific user's stats
    """
    db = SessionLocal()
    
    try:
        target_user = user or ctx.author
        db_user = db.query(User).filter(User.discord_id == str(target_user.id)).first()
        
        if not db_user:
            await ctx.reply(f"⚠️ No messages found for {target_user.name}")
            return
        
        # Get statistics
        total_messages = db.query(Message).filter(Message.user_id == db_user.id).count()
        guild_messages = db.query(Message).filter(
            Message.user_id == db_user.id,
            Message.guild_id == ctx.guild.id
        ).count()
        
        # Get attachment count
        from sqlalchemy import func
        from models.attachment import Attachment
        
        user_messages = db.query(Message.id).filter(Message.user_id == db_user.id).subquery()
        total_attachments = db.query(func.count(Attachment.id)).filter(
            Attachment.message_id.in_(user_messages)
        ).scalar()
        
        # Create embed
        embed = discord.Embed(
            title=f"Backup Stats for {target_user.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Messages (All Servers)", value=total_messages, inline=False)
        embed.add_field(name="Messages (This Server)", value=guild_messages, inline=False)
        embed.add_field(name="Total Attachments", value=total_attachments or 0, inline=False)
        embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else None)
        
        await ctx.reply(embed=embed)
        
    except Exception as e:
        await ctx.reply(f"⚠️ Error fetching stats: {str(e)}")
    
    finally:
        db.close()
