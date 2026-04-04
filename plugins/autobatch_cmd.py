# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

# Auto-Batch Command - Manual Batch Creation from Message Range
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper.font_converter import to_small_caps as sc
from helper.quality_detector import extract_quality, get_base_name, get_quality_priority
import re

# Store user states
user_batch_state = {}

@Client.on_message(filters.private & filters.command("autobatch"))
async def autobatch_command(client: Client, message: Message):
    """Start manual batch creation process"""
    
    # Check if user is admin
    if message.from_user.id not in client.admins:
        await message.reply(f"❌ {sc('only admins can use this command')}")
        return
    
    user_id = message.from_user.id
    
    # Initialize state
    user_batch_state[user_id] = {
        'step': 'waiting_first',
        'first_msg_id': None,
        'last_msg_id': None,
        'chat_id': None
    }
    
    await show_autobatch_panel(client, message, is_edit=False)

async def show_autobatch_panel(client: Client, message: Message, is_edit: bool = False):
    """Show the auto-batch configuration panel"""
    
    # Get current config
    enabled = await client.mongodb.get_bot_config('auto_batch_enabled', True)
    mode = await client.mongodb.get_bot_config('auto_batch_mode', 'episode')
    time_window = await client.mongodb.get_bot_config('auto_batch_time_window', 30)
    
    msg = f"""**📦 {sc('auto-batch configuration')}**

**{sc('current settings')}:**
• {sc('status')}: {'✅ Enabled' if enabled else '❌ Disabled'}
• {sc('mode')}: {'🎬 Episode' if mode == 'episode' else '📅 Season'}
• {sc('time window')}: {time_window}s

**{sc('manual creation')}:**
{sc('send the first message link from your db channel')}
{sc('example')}: `https://t.me/c/1234567890/123`

**{sc('actions')}:**"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"⚙️ {sc('set mode')}", callback_data="autobatch_set_mode"),
            InlineKeyboardButton(f"⏱️ {sc('set time')}", callback_data="autobatch_set_time")
        ],
        [InlineKeyboardButton(f"❌ {sc('close')}", callback_data="autobatch_close")]
    ])
    
    if is_edit:
        await message.edit_text(msg, reply_markup=buttons)
    else:
        await message.reply(msg, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r"^autobatch_"))
async def autobatch_settings(client: Client, query):
    """Handle auto-batch settings"""
    
    # Verify admin for callbacks
    if query.from_user.id not in client.admins:
        await query.answer("❌ Only admins can use this", show_alert=True)
        return

    data = query.data
    
    if data == "autobatch_close" or data == "autobatch_cancel":
        if query.from_user.id in user_batch_state:
            del user_batch_state[query.from_user.id]
        if data == "autobatch_cancel":
            await query.message.edit_text(f"❌ {sc('process cancelled')}")
        else:
            await query.message.delete()
        return
        
    elif data == "autobatch_set_mode":
        await query.message.edit_text(
            f"**🔄 {sc('select auto-batch mode')}**\n\n"
            f"**1. {sc('episode mode')}** (Default)\n"
            f"Groups qualities of same episode.\n"
            f"good for: *Movies, Weekly Episodes*\n\n"
            f"**2. {sc('season mode')}**\n"
            f"Groups episodes of same quality.\n"
            f"good for: *Full Season Uploads*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🎬 {sc('episode mode')}", callback_data="set_ab_mode_episode")],
                [InlineKeyboardButton(f"📅 {sc('season mode')}", callback_data="set_ab_mode_season")],
                [InlineKeyboardButton(f"🔙 {sc('back')}", callback_data="autobatch_main")]
            ])
        )
        
    elif data == "autobatch_main":
        await show_autobatch_panel(client, query.message, is_edit=True)
        
    elif data == "autobatch_set_time":
        await query.message.edit_text(
            f"**⏱️ {sc('select time window')}**\n\n"
            f"{sc('how long to wait for more files before creating a batch')}.\n"
            f"{sc('current')}: 30s",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("10s", callback_data="set_ab_time_10"),
                    InlineKeyboardButton("20s", callback_data="set_ab_time_20"),
                    InlineKeyboardButton("30s", callback_data="set_ab_time_30")
                ],
                [
                    InlineKeyboardButton("60s", callback_data="set_ab_time_60"),
                    InlineKeyboardButton("90s", callback_data="set_ab_time_90"),
                    InlineKeyboardButton("120s", callback_data="set_ab_time_120")
                ],
                [InlineKeyboardButton(f"🔙 {sc('back')}", callback_data="autobatch_main")]
            ])
        )

@Client.on_callback_query(filters.regex(r"^set_ab_time_"))
async def set_autobatch_time(client: Client, query):
    """Set the auto-batch time window"""
    
    # Verify admin
    if query.from_user.id not in client.admins:
        await query.answer("❌ Only admins can use this", show_alert=True)
        return
        
    seconds = int(query.data.split("_")[-1])
    
    await client.mongodb.set_bot_config('auto_batch_time_window', seconds)
    
    await query.answer(f"✅ Time set to {seconds}s", show_alert=True)
    await show_autobatch_panel(client, query.message, is_edit=True)

@Client.on_callback_query(filters.regex(r"^set_ab_mode_"))
async def set_autobatch_mode(client: Client, query):
    """Set the auto-batch mode"""
    
    # Verify admin
    if query.from_user.id not in client.admins:
        await query.answer("❌ Only admins can use this", show_alert=True)
        return
        
    mode = query.data.split("_")[-1]
    
    await client.mongodb.set_bot_config('auto_batch_mode', mode)
    
    await query.answer(f"✅ Mode set to {mode.title()}", show_alert=True)
    await show_autobatch_panel(client, query.message, is_edit=True)

    await client.mongodb.set_bot_config('auto_batch_mode', mode)
    
    await query.answer(f"✅ Mode set to {mode.title()}", show_alert=True)
    await show_autobatch_panel(client, query.message, is_edit=True)

# Custom filter to check if user is in batch mode
# This allows us to run in Group 0 (High Priority) without blocking other commands
async def check_batch_mode(_, __, message: Message):
    if not message.from_user:
        return False
    return message.from_user.id in user_batch_state

is_batch_mode = filters.create(check_batch_mode)

@Client.on_message(filters.private & (filters.text | filters.forwarded) & is_batch_mode)
async def handle_batch_links(client: Client, message: Message):
    """Handle message links or forwards for batch creation"""
    
    user_id = message.from_user.id
    
    # Debug print
    print(f"DEBUG: Handling batch link for user {user_id}: {message.text}")
    
    state = user_batch_state[user_id]
    
    # Extract message ID from link or forward
    msg_id = None
    
    # Compat: support both new Pyrogram (forward_origin) and old (forward_from_message_id)
    is_forward = False
    try:
        if hasattr(message, 'forward_origin') and message.forward_origin:
            is_forward = True
            if message.forward_origin.type == "channel":
                msg_id = message.forward_origin.message_id
        elif hasattr(message, 'forward_from_message_id') and message.forward_from_message_id:
            is_forward = True
            msg_id = message.forward_from_message_id
    except Exception:
        pass
    
    if not is_forward and message.text:
        # Message link - Handle whitespace and potential surrounding text
        # Regex looks for / followed by digits, optionally followed by non-digits
        # Example: https://t.me/c/123/456 or https://t.me/c/123/456?comment=1
        text = message.text.strip()
        
        # Try to find both chat_id and msg_id
        # For private channel links (t.me/c/123/456), 123 is chat_id, 456 is msg_id
        # For public links (t.me/channel/456), we might need to resolve 'channel'
        matches = re.findall(r'/(\d+)', text)
        if len(matches) >= 2:
            # handle cases like t.me/c/12345/678
            # The chat_id for private is usually preceded by /c/ and is positive in link, 
            # but needs -100 prefix in Pyrogram
            chat_id_val = matches[-2]
            msg_id = int(matches[-1])
            
            # If it's a private chat ID (standard for manual links)
            if "/c/" in text:
                chat_id = int(f"-100{chat_id_val}")
            else:
                # Public link or fallback
                chat_id = int(chat_id_val)
        elif matches:
            msg_id = int(matches[-1])
            chat_id = client.db # Fallback to primary DB if only one number found
    
    if not msg_id:
        # Don't reply if it's just a random message not intended for batching
        # UNLESS the user is explicitly in the waiting state
        if state['step'] in ['waiting_first', 'waiting_last']:
             await message.reply(f"❌ {sc('invalid message link')}\n{sc('make sure the link ends with the message id')}")
        return
    
    # Handle based on current step
    if state['step'] == 'waiting_first':
        state['first_msg_id'] = msg_id
        # Update chat_id if we successfully extracted it
        if 'chat_id' in locals() and chat_id:
            state['chat_id'] = chat_id
        elif is_forward:
            # Extract chat_id from forward
            try:
                if hasattr(message, 'forward_origin') and message.forward_origin:
                    if message.forward_origin.type == "channel":
                        state['chat_id'] = message.forward_origin.chat.id
                elif hasattr(message, 'forward_from_chat') and message.forward_from_chat:
                    state['chat_id'] = message.forward_from_chat.id
            except:
                pass
        
        state['step'] = 'waiting_last'
        
        chat_info = f" in `{state['chat_id']}`" if state['chat_id'] else ""
        await message.reply(
            f"✅ {sc('first message received')}: `{msg_id}`{chat_info}\n\n"
            f"{sc('now send the last message link or forward the last message')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"❌ {sc('cancel process')}", callback_data="autobatch_cancel")]
            ])
        )
    
    elif state['step'] == 'waiting_last':
        state['last_msg_id'] = msg_id
        
        # Validate range
        if msg_id <= state['first_msg_id']:
            await message.reply(f"❌ {sc('last message must be after first message')}")
            return
        
        # Ask for processing mode
        state['last_msg_id'] = msg_id
        state['step'] = 'waiting_mode'
        
        msg = f"""**🔄 {sc('select grouping method')}**

**1. {sc('group by episode')}**
• Creates one link per episode
• Contains all qualities (480p, 720p...)
• Example: *Ep 1 [All Qualities]*

**2. {sc('group by quality')}** ({sc('season pack')})
• Creates one link per quality
• Contains all episodes (Ep 1-24...)
• Example: *Season 1 [720p Only]*

{sc('select an option below')}:"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🎬 {sc('group by episode')}", callback_data="batchmode_episode")],
            [InlineKeyboardButton(f"📚 {sc('group by quality')}", callback_data="batchmode_season")],
            [InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="batchmode_cancel")]
        ])
        
        await message.reply(msg, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r"^batchmode_"))
async def handle_batch_mode(client: Client, query):
    """Handle batch mode selection"""
    
    user_id = query.from_user.id
    if user_id not in user_batch_state:
        await query.answer("Session expired", show_alert=True)
        return
    
    state = user_batch_state[user_id]
    mode = query.data.split("_")[1]
    
    if mode == "cancel":
        del user_batch_state[user_id]
        await query.message.edit_text(f"❌ {sc('batch creation cancelled')}")
        return
    
    await query.message.edit_text(f"🔄 {sc('processing messages')}...")
    
    try:
        await process_batch_range(client, query.message, state['first_msg_id'], state['last_msg_id'], mode, state['chat_id'])
    finally:
        if user_id in user_batch_state:
            del user_batch_state[user_id]

async def process_batch_range(client: Client, message: Message, first_id: int, last_id: int, mode: str = "episode", chat_id: int = None):
    """Process message range and create batch"""
    
    # Get DB channel ID from state or default config
    db_channel_id = chat_id or client.db_channel_id
    
    files_by_group = {}
    total_files = 0
    
    # Imports inside function to avoid circular imports if any
    from helper.quality_detector import get_series_name
    
    try:
        # Iterate through message range
        for msg_id in range(first_id, last_id + 1):
            try:
                msg = await client.get_messages(db_channel_id, msg_id)
                
                if not msg or not msg.document:
                    continue
                
                filename = msg.document.file_name
                if not filename:
                    continue
                
                # Extract quality
                quality = extract_quality(filename)
                if not quality:
                    continue
                
                # Determine Group Key based on Mode
                if mode == "episode":
                    # Group by Base Name (includes Episode info)
                    # Key: "Show S01 E01"
                    group_key = get_base_name(filename)
                else:
                    # Group by Series Name + Quality
                    # Key: "Show S01 [720p]"
                    series_name = get_series_name(filename)
                    group_key = f"{series_name} [{quality}]"
                
                if not group_key:
                    continue
                
                # Add to group
                if group_key not in files_by_group:
                    files_by_group[group_key] = []
                
                # For Season Batching, we want to check if file already exists in group
                # to avoid duplicates if multiple quality variants exist (though in season batching we group BY quality)
                
                files_by_group[group_key].append({
                    'file_id': str(msg_id),
                    'filename': filename,
                    'quality': quality,
                    'channel_id': db_channel_id
                })
                
                total_files += 1
                
            except Exception as e:
                continue
        
        # Create batches
        batches_created = 0
        batch_links = []
        
        for group_name, files in files_by_group.items():
            # For Mode 1 (Episode): Need 2+ qualities to group
            # For Mode 2 (Season): Need 2+ files to group (e.g. Ep 1 and Ep 2)
            
            if len(files) >= 2:
                # Sort files
                # Mode 1: Sort by Quality (480p, 720p...)
                # Mode 2: Sort by Filename (Ep 1, Ep 2...)
                if mode == "episode":
                    files.sort(key=lambda f: get_quality_priority(f['quality']))
                else:
                    files.sort(key=lambda f: f['filename'])
                
                # Create batch
                # Use group_name as the Batch Name
                batch_id = await client.mongodb.create_batch(group_name, files)
                
                # Determine display text
                if mode == "episode":
                    qualities = " | ".join([f['quality'] for f in files])
                    display_info = qualities
                else:
                    display_info = f"{len(files)} Episodes"
                
                batch_link = f"https://t.me/{client.username}?start=batch_{batch_id}"
                
                batch_links.append({
                    'name': group_name,
                    'info': display_info,
                    'link': batch_link,
                    'count': len(files)
                })
                
                batches_created += 1
        
        # Send results
        if batches_created == 0:
            await message.reply(
                f"⚠️ {sc('no batches created')}\n\n"
                f"{sc('found')} {total_files} {sc('files but no matching groups')}"
            )
        else:
            result_msg = f"**✅ {sc('batch creation complete')}**\n"
            result_msg += f"**{sc('mode')}:** {sc(mode + ' batching')}\n"
            result_msg += f"**{sc('files scanned')}:** {total_files}\n"
            result_msg += f"**{sc('batches created')}:** {batches_created}\n"
            
            if client.auto_del > 0:
                import humanize
                result_msg += f"**⏳ {sc('auto delete')}:** {humanize.naturaldelta(client.auto_del)}\n"
            
            result_msg += "\n"
            
            for batch in batch_links[:10]:  # Show first 10
                result_msg += f"**📦 {batch['name'][:40]}**\n"
                result_msg += f"└ {batch['info']}\n"
                result_msg += f"└ `{batch['link']}`\n\n"
            
            if len(batch_links) > 10:
                result_msg += f"\n{sc('and')} {len(batch_links) - 10} {sc('more batches')}..."
            
            await message.reply(result_msg)
    
    except Exception as e:
        await message.reply(f"❌ {sc('error processing range')}: {str(e)}")

@Client.on_message(filters.private & filters.command("cancelbatch"))
async def cancel_batch(client: Client, message: Message):
    """Cancel batch creation"""
    user_id = message.from_user.id
    
    if user_id in user_batch_state:
        del user_batch_state[user_id]
        await message.reply(f"✅ {sc('batch creation cancelled')}")
    else:
        await message.reply(f"ℹ️ {sc('no active batch creation')}")
