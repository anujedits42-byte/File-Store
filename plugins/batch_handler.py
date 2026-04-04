# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

# Batch Link Handler
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper.font_converter import to_small_caps as sc
from helper.quality_detector import get_quality_priority

# Use group=1 to give this handler lower priority than /start (which is in group=0 by default)
@Client.on_message(filters.private & filters.text, group=1)
async def batch_link_handler(client: Client, message: Message):
    """Handle batch link access"""
    # Only handle batch_ links
    if not message.text or not message.text.startswith("/start batch_"):
        return
    
    text = message.text
    batch_id = text.replace("/start batch_", "").strip()

    # Reuse the logic
    await process_batch(client, message, batch_id)

async def process_batch(client: Client, message: Message, batch_id: str):
    """Reusable batch processing logic"""
    # Get batch from database
    batch = await client.mongodb.get_batch(batch_id)
    
    if not batch:
        await message.reply(f"❌ {sc('batch not found or expired')}")
        return
    
    user_id = message.from_user.id
    
    # Check if user is premium
    is_premium = await client.mongodb.is_premium(user_id)
    
    # Get user credits
    from helper.enhanced_credit_db import EnhancedCreditDB
    enhanced_db = EnhancedCreditDB(client.db_uri, client.db_name)
    credit_data = await enhanced_db.get_credits(user_id)
    user_credits = credit_data.get("balance", 0)
    
    # Check if credit system is enabled
    credit_system_enabled = await client.mongodb.is_credit_system_enabled()
    if not credit_system_enabled:
        user_credits = 0 # Disable credit usage logic
    
    # Determine batch type (Season vs Episode)
    qualities = set(f['quality'] for f in batch['files'])
    is_season_batch = len(qualities) <= 1
    
    # Import helpers needed for formatting
    from helper.quality_detector import parse_episode_info, get_series_name
    import humanize
    
    # Sort files
    if is_season_batch:
        # Sort by episode number for season packs
        files = sorted(batch['files'], key=lambda f: parse_episode_info(f['filename']).get('episode', 0) or 0)
    else:
        # Sort by quality for episode packs
        files = sorted(batch['files'], key=lambda f: get_quality_priority(f['quality']))
    
    # If Season Batch -> Send Files Directly
    if is_season_batch:
        # Fetch messages
        file_ids = [int(f['file_id']) for f in files]
        from helper.helper_func import get_messages, delete_files
        
        msg_to_delete = await message.reply(f"{sc('processing')}.. ⏳")
        
        try:
            # Group files by channel_id to optimize fetching
            from collections import defaultdict
            files_by_channel = defaultdict(list)
            for f in files:
                channel_id = f.get('channel_id', int(client.db))
                channel_id = int(str(channel_id).replace("-100", ""))  # Clean ID
                files_by_channel[channel_id].append(int(f['file_id']))
            
            messages = []
            for chat_id, msg_ids in files_by_channel.items():
                # Add -100 prefix if missing
                full_chat_id = int(f"-100{chat_id}")
                msgs = await get_messages(client, msg_ids, full_chat_id)
                messages.extend(msgs)
        except Exception as e:
            await msg_to_delete.edit(f"❌ Error fetching messages: {e}")
            return
            
        if not messages:
            await msg_to_delete.edit("❌ Files not found in DB channel.")
            return
            
        await msg_to_delete.delete()
        
        sent_msgs = []
        for msg in messages:
            # Caption Logic (Mirrors start.py)
            caption = (
                client.messages.get('CAPTION', '').format(
                    previouscaption=f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption else f"<blockquote>{msg.document.file_name}</blockquote>"
                )
                if client.messages.get('CAPTION', '') and msg.document
                else (msg.caption.html if msg.caption else "")
            )
            
            try:
                copied = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    protect_content=client.protect
                )
                sent_msgs.append(copied)
            except Exception as e:
                pass
                
        # Auto-Delete Logic
        if sent_msgs and client.auto_del > 0:
            warning = await message.reply(
                f"<b>⚠️ {sc('files will be deleted in')} {humanize.naturaldelta(client.auto_del)}.</b>"
            )
            # Run delete_files in background
            import asyncio
            asyncio.create_task(delete_files(sent_msgs, client, warning, message.text))
            
        return

    # Else (Episode Pack) -> Show Menu (Existing Logic)
    
    # Build quality selection message
    msg = f"""**📦 {sc('batch download')}**

**{sc('title')}:** {batch['base_name']}
**{sc('type')}:** {sc('episode pack')}

"""
    
    buttons = []
    for file_data in files:
        quality = file_data['quality']
        filename = file_data['filename']
        file_id = file_data['file_id']
        
        # Generator Button Text
        # For Episode Packs: "480p"
        button_text = f"📥 {quality}"
            
        if is_premium or (credit_system_enabled and user_credits > 0):
            button_text += " ✅"
        
        buttons.append([InlineKeyboardButton(
            button_text,
            callback_data=f"batchfile_{batch_id}_{file_id}"
        )])
        
    msg += f"\n{sc('select file to download')}"
    
    if not is_premium and user_credits == 0 and credit_system_enabled:
        msg += f"\n\n⚠️ {sc('you need credits or premium to access files')}"
        
    # Auto-delete warning
    if client.auto_del > 0:
        msg += f"\n\n⏳ {sc('files auto-delete in')} {humanize.naturaldelta(client.auto_del)}"
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(msg, reply_markup=keyboard)

@Client.on_callback_query(filters.regex(r"^batchfile_"))
async def batch_file_callback(client: Client, query):
    """Handle batch file selection — directly send the chosen file"""

    # Format: batchfile_{batch_id}_{file_id}
    # batch_id is hex (no underscores), file_id is a plain message number
    # Use rsplit on '_' with maxsplit=1 to safely extract the file_id from the end
    raw = query.data  # e.g. "batchfile_a1b2c3d4e5f6_642"
    prefix_with_batch = raw.rsplit("_", 1)  # ["batchfile_a1b2c3d4e5f6", "642"]
    if len(prefix_with_batch) != 2:
        await query.answer("❌ Invalid batch data", show_alert=True)
        return

    file_id_str = prefix_with_batch[1]  # "642"
    batch_id = prefix_with_batch[0].replace("batchfile_", "", 1)  # "a1b2c3d4e5f6"

    user_id = query.from_user.id

    batch = await client.mongodb.get_batch(batch_id)
    if not batch:
        await query.answer("❌ Batch expired or not found", show_alert=True)
        return

    file_data = next((f for f in batch['files'] if str(f['file_id']) == file_id_str), None)
    if not file_data:
        await query.answer("❌ File not found in batch", show_alert=True)
        return

    await query.answer()

    msg_id = int(file_id_str)
    channel_id = file_data.get('channel_id', client.db)

    # Normalize channel_id to full negative int
    try:
        channel_id = int(channel_id)
        if channel_id > 0:
            channel_id = int(f"-100{channel_id}")
    except Exception:
        channel_id = int(client.db)

    processing = await query.message.reply(f"⏳ {sc('sending your file')}...")

    try:
        msg = await client.get_messages(channel_id, msg_id)
        if not msg or msg.empty:
            await processing.edit(f"❌ {sc('file not found in database')}")
            return

        caption = (
            client.messages.get('CAPTION', '').format(
                previouscaption=(
                    f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption
                    else f"<blockquote>{msg.document.file_name if msg.document else ''}</blockquote>"
                )
            )
            if client.messages.get('CAPTION', '') and msg.document
            else (msg.caption.html if msg.caption else "")
        )

        sent = await msg.copy(
            chat_id=user_id,
            caption=caption,
            protect_content=client.protect
        )

        await processing.delete()

        if client.auto_del > 0:
            import humanize
            from helper.helper_func import delete_files
            import asyncio
            warning = await query.message.reply(
                f"<b>⚠️ {sc('file will be deleted in')} {humanize.naturaldelta(client.auto_del)}.</b>"
            )
            asyncio.create_task(delete_files([sent], client, warning, ""))

    except Exception as e:
        await processing.edit(f"❌ {sc('error')}: {e}")

