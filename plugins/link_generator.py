# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.helper_func import encode, get_message_id
from helper.font_converter import to_small_caps as sc

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")]])
    
    # Step 1: First Message
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward the')} **{sc('first message')}** {sc('from db channel (with quotes)')}..\n\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            first_response = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
            
        if isinstance(first_response, CallbackQuery):
            if first_response.data == 'cancel_batch_process':
                await first_response.answer(sc("cancelled"), show_alert=True)
                await first_response.message.delete()
                await message.reply(f"❌ **{sc('batch process cancelled.')}**")
                return
            else:
                # Ignore other callbacks or handle them?
                await first_response.answer(sc("wrong button"), show_alert=True)
                continue
            
        f_msg_id = await get_message_id(client, first_response)
        if f_msg_id:
            # Extract channel ID for extra DB support
            channel_id = client.db_channel.id
            if first_response.forward_from_chat:
                channel_id = first_response.forward_from_chat.id
            elif first_response.text and "https://t.me/" in first_response.text:
                import re
                match = re.search(r"https://t.me/(?:c/)?([^/]+)/\d+", first_response.text)
                if match:
                    ch_str = match.group(1)
                    if ch_str.isdigit():
                        channel_id = int(f"-100{ch_str}")
                    else:
                        try:
                            chat = await client.get_chat(ch_str)
                            channel_id = chat.id
                        except:
                            pass
            
            await ask_msg.delete() 
            break
        else:
            await first_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote = True)
            continue

    # Step 2: Last Message
    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward the')} **{sc('last message')}** {sc('from db channel (with quotes)')}..\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            second_response = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except Exception:
            return
        
        if isinstance(second_response, CallbackQuery):
            if second_response.data == 'cancel_batch_process':
                await second_response.answer(sc("cancelled"), show_alert=True)
                await second_response.message.delete()
                await message.reply(f"❌ **{sc('batch process cancelled.')}**")
                return
            else:
                await second_response.answer(sc("wrong button"), show_alert=True)
                continue

        s_msg_id = await get_message_id(client, second_response)
        if s_msg_id:
            await ask_msg.delete()
            break
        else:
            await second_response.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is taken from db channel')}", quote = True)
            continue


    # Calculate IDs
    # batch command generates a RANGE. Hybrid token system is for SINGLE files.
    # We stick to base64 for ranges for now, but we add INFO to the message.
    
    # Fetch first message to get a name
    try:
        first_msg = await client.get_messages(channel_id, f_msg_id)
        batch_name = ""
        if first_msg:
             if first_msg.document:
                 batch_name = first_msg.document.file_name
             elif first_msg.caption:
                 batch_name = first_msg.caption.split("\n")[0][:50] + "..."
        
        info_text = f"<blockquote><b>📦 {sc('batch create')}</b>\n"
        if batch_name:
             info_text += f"📄 {batch_name}\n"
        info_text += f"🔢 {sc('range')}: {f_msg_id} - {s_msg_id}\n"
        
        # Add Auto-Delete Info
        if client.auto_del > 0:
            import humanize
            info_text += f"⏳ {sc('auto delete')}: {humanize.naturaldelta(client.auto_del)}"
            
        info_text += "</blockquote>\n\n"
        
    except:
        info_text = ""

    # Hybrid Token for Batch Range
    try:
        token = await client.mongodb.create_file_token(channel_id, f_msg_id, end_msg_id=s_msg_id)
        link = f"https://t.me/{client.username}?start={token}"
    except Exception as e:
        print(f"Token creation failed for batch: {e}")
        string = f"get-{f_msg_id * abs(channel_id)}-{s_msg_id * abs(channel_id)}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
    await second_response.reply_text(f"{info_text}<b>{sc('here is your link')}</b>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    main_channel = getattr(client, 'db_channel_id', client.db)

    # ── SHORTCUT: If /genlink is used as a reply, copy that message to DB and link it ──
    if message.reply_to_message:
        replied = message.reply_to_message
        processing_msg = await message.reply(f"🔄 {sc('processing')}...")

        try:
            # Check if the replied message is already from one of our DB channels
            channel_id = main_channel
            msg_id = None

            try:
                _fwd_chat_id = None
                _fwd_msg_id = None
                if hasattr(replied, 'forward_origin') and replied.forward_origin:
                    if replied.forward_origin.type == "channel":
                        _fwd_chat_id = replied.forward_origin.chat.id
                        _fwd_msg_id = replied.forward_origin.message_id
                elif hasattr(replied, 'forward_from_chat') and replied.forward_from_chat:
                    _fwd_chat_id = replied.forward_from_chat.id
                    _fwd_msg_id = getattr(replied, 'forward_from_message_id', None)

                if _fwd_chat_id:
                    extra_channels = await client.mongodb.get_db_channels()
                    all_db_channels = [main_channel] + extra_channels
                    if _fwd_chat_id in all_db_channels and _fwd_msg_id:
                        msg_id = _fwd_msg_id
                        channel_id = _fwd_chat_id
            except Exception:
                pass

            if not msg_id:
                # Copy the replied message to the main DB channel
                post = await replied.copy(chat_id=main_channel, caption=replied.caption)
                msg_id = post.id
                channel_id = main_channel

            # Extract filename for display
            file_name = ""
            if replied.document:
                file_name = replied.document.file_name or ""
            elif replied.caption:
                file_name = replied.caption.split("\n")[0][:50]
            elif replied.text:
                file_name = replied.text[:50]

            # Generate link
            try:
                token = await client.mongodb.create_file_token(channel_id, msg_id)
                link = f"https://t.me/{client.username}?start={token}"
            except Exception:
                base64_string = await encode(f"get-{msg_id * abs(channel_id)}")
                link = f"https://t.me/{client.username}?start={base64_string}"

            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])

            text = "<blockquote>"
            if file_name:
                text += f"<b>📂 {file_name}</b>\n"
            if client.auto_del > 0:
                import humanize
                text += f"⏳ {sc('auto delete')}: {humanize.naturaldelta(client.auto_del)}"
            if text == "<blockquote>":
                text = ""
            else:
                text += "</blockquote>\n\n"
            text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"

            await processing_msg.edit_text(text, reply_markup=reply_markup)

        except Exception as e:
            await processing_msg.edit_text(f"❌ {sc('error')}: {e}")
        return

    # ── INTERACTIVE FLOW: No reply, ask admin to forward/link ──
    cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ {sc('cancel')}", callback_data="cancel_batch_process")]])

    while True:
        try:
            ask_msg = await message.reply(f"{sc('forward message from the db channel (with quotes)')}..\\n{sc('or send the db channel post link')}", reply_markup=cancel_btn)
            channel_message = await client.listen(chat_id=message.from_user.id, filters=filters.user(message.from_user.id), timeout=60)
        except:
            return

        if isinstance(channel_message, CallbackQuery):
            if channel_message.data == 'cancel_batch_process':
                await channel_message.answer(sc("cancelled"), show_alert=True)
                await channel_message.message.delete()
                await message.reply(f"❌ **{sc('process cancelled.')}**")
                return
            else:
                await channel_message.answer(sc("wrong button"), show_alert=True)
                continue

        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            await ask_msg.delete()
            break
        else:
            await channel_message.reply(f"❌ {sc('error')}\n\n{sc('this forwarded post is not from my db channel or this link is not taken from db channel')}", quote=True)
            continue

    channel_id = getattr(client, 'db_channel_id', client.db)

    # Fetch content name
    file_name = ""
    try:
        f_msg = await client.get_messages(channel_id, msg_id)
        if f_msg:
            if f_msg.document:
                file_name = f_msg.document.file_name
            elif f_msg.caption:
                file_name = f_msg.caption.split("\n")[0][:50]
    except:
        pass

    # Hybrid Token
    try:
        token = await client.mongodb.create_file_token(channel_id, msg_id)
        link = f"https://t.me/{client.username}?start={token}"
    except:
        base64_string = await encode(f"get-{msg_id * abs(channel_id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])

    text = "<blockquote>"
    if file_name:
        text += f"<b>📂 {file_name}</b>\n"
    if client.auto_del > 0:
        import humanize
        text += f"⏳ {sc('auto delete')}: {humanize.naturaldelta(client.auto_del)}"
    if text == "<blockquote>":
        text = ""
    else:
        text += "</blockquote>\n\n"
    text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"

    await channel_message.reply_text(text, quote=True, reply_markup=reply_markup)


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.command(["start", "batch", "genlink"]))
async def single_file_gen_handler(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return

    # Skip if message is a command (handled by other handlers)
    if message.text and message.text.startswith("/"):
        return

    try:
        msg = await message.reply(f"🔄 {sc('processing')}...", quote=True)
        
        main_channel = getattr(client, 'db_channel_id', client.db)
        
        # If message is forwarded from DB Channel, use existing ID
        channel_id = main_channel
        msg_id = None
        
        # Compat: support both new Pyrogram (forward_origin) and old (forward_from_chat)
        try:
            _fwd_chat_id = None
            _fwd_msg_id = None
            if hasattr(message, 'forward_origin') and message.forward_origin:
                if message.forward_origin.type == "channel":
                    _fwd_chat_id = message.forward_origin.chat.id
                    _fwd_msg_id = message.forward_origin.message_id
            elif hasattr(message, 'forward_from_chat') and message.forward_from_chat:
                _fwd_chat_id = message.forward_from_chat.id
                _fwd_msg_id = getattr(message, 'forward_from_message_id', None)
            
            if _fwd_chat_id:
                extra_channels = await client.mongodb.get_db_channels()
                all_db_channels = [main_channel] + extra_channels
                if _fwd_chat_id in all_db_channels and _fwd_msg_id:
                    msg_id = _fwd_msg_id
                    channel_id = _fwd_chat_id
        except Exception:
            pass
        
        if not msg_id:
             # Not from our DB or clean upload, copy to selected channel
             channel_id = await client.mongodb.get_next_db_channel(main_channel)
             post = await message.copy(chat_id=channel_id, caption=message.caption)
             msg_id = post.id
             
        # Extract filename for display
        file_name = message.document.file_name if message.document else ""
        if not file_name and message.caption:
             file_name = message.caption.split("\n")[0][:50]
            
        # 🔐 Generate hybrid token (stored in MongoDB)
        try:
            token = await client.mongodb.create_file_token(channel_id, msg_id)
            link = f"https://t.me/{client.username}?start={token}"
        except Exception as e:
            print(f"Token creation failed: {e}")
            # Fallback to Base64
            base64_string = await encode(f"get-{msg_id * abs(channel_id)}")
            link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"🔁 {sc('share url')}", url=f'https://telegram.me/share/url?url={link}')]])
        
        text = ""
        # Header Info
        text += "<blockquote>"
        if file_name:
            text += f"<b>📂 {file_name}</b>\n"
        
        if client.auto_del > 0:
            import humanize
            text += f"⏳ {sc('auto delete')}: {humanize.naturaldelta(client.auto_del)}"
        
        if text == "<blockquote>":
            text = ""
        else:
            text += "</blockquote>\n\n"

        text += f"<b>{sc('here is your link')}</b>\n\n<code>{link}</code>"
        
        await msg.edit_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        print(f"Error in single_file_gen: {e}")
        await message.reply(f"❌ {sc('error')}: {e}")


