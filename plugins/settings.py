# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.pyromod import ListenerTimeout
from config import OWNER_ID, URL_SHORTENERS
import humanize
from helper.font_converter import to_small_caps as sc

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    msg = f"""<blockquote>**{sc(f'Settings of @{client.username}')}:**</blockquote>
**{sc('Force Sub Channels')}:** `{len(client.fsub_dict)}`
**{sc('Auto Delete Timer')}:** `{client.auto_del}`
**{sc('Protect Content')}:** `{"True" if client.protect else "False"}`
**{sc('Disable Button')}:** `{"True" if client.disable_btn else "False"}`
**{sc('Reply Text')}:** `{client.reply_text if client.reply_text else 'None'}`
**{sc('Admins')}:** `{len(client.admins)}`
**{sc('Start Message')}:**
<pre>{client.messages.get('START', 'Empty')}</pre>
**{sc('Start Image')}:** `{bool(client.messages.get('START_PHOTO', ''))}`
**{sc('Force Sub Message')}:**
<pre>{client.messages.get('FSUB', 'Empty')}</pre>
**{sc('Force Sub Image')}:** `{bool(client.messages.get('FSUB_PHOTO', ''))}`
**{sc('About Message')}:**
<pre>{client.messages.get('ABOUT', 'Empty')}</pre>
**{sc('Reply Message')}:**
<pre>{client.reply_text}</pre>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ', 'fsub'), InlineKeyboardButton('ᴀᴅᴍɪɴꜱ', 'admins')],
        [InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del'), InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect')],
        [InlineKeyboardButton('ᴜʀʟ ꜱʜᴏʀᴛᴇɴᴇʀꜱ', 'url_shorteners'), InlineKeyboardButton('ᴘʜᴏᴛᴏꜱ', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛꜱ', 'texts'), InlineKeyboardButton('💳 ᴄʀᴇᴅɪᴛ ꜱʏꜱᴛᴇᴍ', 'credit_system')],
        [InlineKeyboardButton('🗄️ ᴅʙ ᴄʜᴀɴɴᴇʟꜱ', 'db_channels'), InlineKeyboardButton('🔒 ꜱᴇᴄᴜʀɪᴛʏ (Tokens)', 'security_panel')],
        [InlineKeyboardButton('🤖 ᴀᴜᴛᴏ ʙᴀᴛᴄʜ', 'auto_batch_settings'), InlineKeyboardButton('💎 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ', 'premium_users_settings')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    header = f"<blockquote><b>⚡ {sc('force-sub channel list')}:</b></blockquote>\n\n"
    
    if not client.fsub_dict:
        body = f"_{sc('no force-sub channels configured')}_"
    else:
        body = ""
        for channel_id, info in client.fsub_dict.items():
            name = info[0] if info else sc("unknown")
            try:
                join_count = await client.mongodb.get_channel_join_count(channel_id)
            except Exception:
                join_count = 0
            body += (
                f"<blockquote>"
                f"<b>{sc('name')}:</b> {name}\n"
                f"<b>({sc('id')}:</b> <code>{channel_id}</code>)\n"
                f"<b>{sc('joined via bot')}:</b> <code>{join_count}</code>"
                f"</blockquote>\n"
            )

    msg = header + body
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_callback_query(filters.regex("^add_fsub$"))
async def add_fsub_cb(client, query):
    await query.answer()
    msg = f"""<blockquote><b>➕ {sc('add force-sub channel')}:</b></blockquote>

{sc('forward a message from the channel or send the channel id')}
{sc('make sure the bot is admin in that channel')}!

_{sc('timeout')}: 60s_
"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text | filters.forwarded, timeout=60)
        channel_id = None
        try:
            if hasattr(res, 'forward_origin') and res.forward_origin:
                if res.forward_origin.type == "channel":
                    channel_id = res.forward_origin.chat.id
            elif hasattr(res, 'forward_from_chat') and res.forward_from_chat:
                channel_id = res.forward_from_chat.id
        except Exception:
            pass
        if not channel_id and res.text:
            try:
                parts = res.text.strip().split()
                channel_id = int(parts[0])
                request = False
                timer = 0
                
                if len(parts) >= 2:
                    if parts[1].lower() in ('true', 'on', 'yes'):
                        request = True
                        
                if len(parts) >= 3:
                    if parts[2].isdigit():
                        timer = int(parts[2])
            except:
                pass
                
        if not channel_id:
            return await query.message.edit_text("**❌ Invalid Channel ID!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
            
        if channel_id in client.fsub_dict:
            return await query.message.edit_text(f"**⚠️ Already in force-sub list!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
            
        try:
            chat = await client.get_chat(channel_id)
            name = chat.title
            
            # For request type fsub, we set invite link to None (bot will generate it later with timer)
            if request:
                invite_link = None
            else:
                try:
                    invite_link = chat.invite_link or (await client.create_chat_invite_link(channel_id)).invite_link
                except:
                    invite_link = None
                    
        except Exception as e:
            return await query.message.edit_text(f"**❌ Cannot access channel!**\n`{e}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
            
        client.fsub_dict[channel_id] = [name, invite_link, request, timer]
        await client.mongodb.save_fsub_channels(client.fsub_dict)  # 💾 Persist
        
        req_status = "✅ Request-Mode" if request else "❌ Standard"
        timer_status = f"⏱️ {timer}m" if timer > 0 else "♾️ Permanent"
        
        msg = f"**✅ {name}** `({channel_id})` {sc('added to force-sub')}!\n\n"
        msg += f"• **Type:** `{req_status}`\n"
        msg += f"• **Timer:** `{timer_status}`"
        
        await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⌚ Timeout!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))

@Client.on_callback_query(filters.regex("^rm_fsub$"))
async def rm_fsub_cb(client, query):
    await query.answer()
    if not client.fsub_dict:
        return await query.answer(f"❌ {sc('no channels configured')}", show_alert=True)
    channel_list = "\n".join(f"• <code>{cid}</code> — {info[0]}" for cid, info in client.fsub_dict.items())
    msg = f"""<blockquote><b>➖ {sc('remove force-sub channel')}:</b></blockquote>

{sc('current channels')}:
{channel_list}

{sc('send the channel id to remove')}:
_{sc('timeout')}: 60s_
"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        try:
            channel_id = int(res.text.strip())
        except:
            return await query.message.edit_text("**❌ Invalid ID!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
        if channel_id not in client.fsub_dict:
            return await query.message.edit_text(f"**❌ Channel not in force-sub list!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
        name = client.fsub_dict[channel_id][0]
        del client.fsub_dict[channel_id]
        await client.mongodb.save_fsub_channels(client.fsub_dict)  # 💾 Persist
        await query.message.edit_text(f"**✅ {name}** {sc('removed from force-sub')}!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⌚ Timeout!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'fsub')]]))

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels(client, query):
    channels = await client.mongodb.get_db_channels()
    multi_db_enabled = await client.mongodb.is_multi_db_enabled()
    
    status = f"✅ {sc('enabled')}" if multi_db_enabled else f"❌ {sc('disabled')}"
    
    msg = f"""<blockquote>**🗄️ {sc('multi-db channel settings')}:**</blockquote>

**{sc('system status')}:** {status}
**{sc('primary main db')}:** `{client.db.id if hasattr(client.db, 'id') else client.db}`
**{sc('extra db channels')}:**
"""
    if channels:
        for ch in channels:
            msg += f"• `{ch}`\n"
    else:
        msg += f"• _{sc('none')}_\n"

    msg += f"\n__{sc('add extra channels to store files in multiple places')}!__"
    
    toggle_text = f"🔴 {sc('disable multi-db')}" if multi_db_enabled else f"🟢 {sc('enable multi-db')}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, 'toggle_multi_db')],
        [InlineKeyboardButton(f'➕ {sc("add db")}', 'add_db_channel'), InlineKeyboardButton(f'➖ {sc("remove db")}', 'rm_db_channel')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^add_db_channel$"))
async def add_db_channel_cb(client, query):
    msg = f"""<blockquote>**➕ Add DB Channel:**</blockquote>
    
__Forward a message from the channel OR send the Channel ID.__
__Make sure the bot is ADMIN in that channel!__

_Timeout: 60s_
"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text | filters.forwarded, timeout=60)
        
        channel_id = None
        # Support both newer Pyrogram (forward_origin) and older versions (forward_from_chat)
        try:
            if hasattr(res, 'forward_origin') and res.forward_origin:
                if res.forward_origin.type == "channel":
                    channel_id = res.forward_origin.chat.id
            elif hasattr(res, 'forward_from_chat') and res.forward_from_chat:
                channel_id = res.forward_from_chat.id
        except Exception:
            pass
        
        if not channel_id and res.text:
            try:
                channel_id = int(res.text.strip())
            except:
                pass
        
        if not channel_id:
             return await query.message.edit_text("**❌ Invalid Channel ID!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

        # Verify bot access
        try:
            chat = await client.get_chat(channel_id)
            # await chat.get_member(client.me.id) # Check if admin? (Optional)
        except Exception as e:
             return await query.message.edit_text(f"**❌ Bot cannot access that channel!**\nError: {e}\n\nMake sure bot is added as Admin.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

        await client.mongodb.add_db_channel(channel_id)
        await query.message.edit_text(f"**✅ Channel `{channel_id}` added to Multi-DB!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

    except ListenerTimeout:
        await query.message.edit_text("**⌚ Timeout!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

@Client.on_callback_query(filters.regex("^rm_db_channel$"))
async def rm_db_channel_cb(client, query):
    msg = f"""<blockquote>**➖ Remove DB Channel:**</blockquote>
    
__Send the Channel ID to remove.__

_Timeout: 60s_
"""
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        try:
             channel_id = int(res.text.strip())
        except:
             return await query.message.edit_text("**❌ Invalid ID!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

        await client.mongodb.remove_db_channel(channel_id)
        await query.message.edit_text(f"**✅ Channel `{channel_id}` removed!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

    except ListenerTimeout:
        await query.message.edit_text("**⌚ Timeout!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

@Client.on_callback_query(filters.regex("^toggle_multi_db$"))
async def toggle_multi_db_cb(client, query):
    new_status = await client.mongodb.toggle_multi_db()
    status_text = sc('enabled') if new_status else sc('disabled')
    await query.answer(f"✅ {sc('multi-db system')} {status_text}!", show_alert=True)
    return await db_channels(client, query)

@Client.on_callback_query(filters.regex("^premium_users_settings$"))
async def premium_users_settings(client, query):
    """Premium users management panel"""
    users = await client.mongodb.get_premium_users()
    
    msg = f"""<blockquote>**💎 {sc('premium users management')}:**</blockquote>

**{sc('total premium users')}:** `{len(users)}`

"""
    
    if users:
        from datetime import datetime
        now = datetime.now()
        
        msg += f"**{sc('active premium users')}:**\n"
        for i, uid in enumerate(users[:10], 1):  # Show first 10
            data = await client.mongodb.user_data.find_one({"_id": uid})
            exp = data.get("premium_expire") if data else None
            
            if exp:
                left = (exp - now).days
                status = f"{left} {sc('days left')}" if left > 0 else sc('expired')
            else:
                status = "∞ " + sc('lifetime')
            
            msg += f"**{i}.** `{uid}` — {status}\n"
        
        if len(users) > 10:
            msg += f"\n_+{len(users) - 10} {sc('more users')}_"
    else:
        msg += f"_{sc('no premium users found')}_"
    
    msg += f"\n\n__{sc('use buttons below to manage premium users')}__"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'➕ {sc("add premium")}', 'add_premium_user'), InlineKeyboardButton(f'➖ {sc("remove premium")}', 'remove_premium_user')],
        [InlineKeyboardButton(f'📋 {sc("view all")}', 'view_all_premium')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'settings')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^view_all_premium$"))
async def view_all_premium(client, query):
    """View all premium users"""
    users = await client.mongodb.get_premium_users()
    
    if not users:
        await query.answer(f"📭 {sc('no premium users found')}", show_alert=True)
        return
    
    from datetime import datetime
    now = datetime.now()
    
    msg = f"""<blockquote>**💎 {sc('all premium users')} ({len(users)}):**</blockquote>

"""
    
    for i, uid in enumerate(users, 1):
        data = await client.mongodb.user_data.find_one({"_id": uid})
        exp = data.get("premium_expire") if data else None
        
        if exp:
            left = (exp - now).days
            status = f"{left}d" if left > 0 else sc('exp')
        else:
            status = "∞"
        
        msg += f"`{i}.` `{uid}` — {status}\n"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^add_premium_user$"))
async def add_premium_user_cb(client, query):
    """Add premium user via settings"""
    msg = f"""<blockquote>**➕ {sc('add premium user')}:**</blockquote>

{sc('send user id and days separated by space')}

**{sc('format')}:** `user_id days`
**{sc('example')}:** `123456789 30`

__{sc('for lifetime premium, use')} 0 {sc('days')}__

_{sc('timeout')}: 60s_
"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("cancel")}', 'premium_users_settings')]]))
    
    try:

        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        
        parts = res.text.strip().split()
        if len(parts) < 2:
            await query.message.edit_text(f"❌ {sc('invalid format')}!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))
            return
        
        try:
            user_id = int(parts[0])
            days = int(parts[1])
        except:
            await query.message.edit_text(f"❌ {sc('invalid user id or days')}!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))
            return
        
        from datetime import datetime, timedelta
        expire_date = None if days == 0 else datetime.now() + timedelta(days=days)
        
        await client.mongodb.add_premium(user_id, expire_date)
        
        duration = sc('lifetime') if days == 0 else f"{days} {sc('days')}"
        await query.message.edit_text(
            f"✅ **{sc('premium added')}!**\n\n"
            f"**{sc('user id')}:** `{user_id}`\n"
            f"**{sc('duration')}:** {duration}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]])
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                f"🎉 **{sc('you are now premium')}!**\n\n"
                f"**{sc('duration')}:** {duration}"
            )
        except:
            pass
            
    except ListenerTimeout:
        await query.message.edit_text(f"**⌚ {sc('timeout')}!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))

@Client.on_callback_query(filters.regex("^remove_premium_user$"))
async def remove_premium_user_cb(client, query):
    """Remove premium user via settings"""
    msg = f"""<blockquote>**➖ {sc('remove premium user')}:**</blockquote>

{sc('send user id to remove premium')}

**{sc('format')}:** `user_id`
**{sc('example')}:** `123456789`

_{sc('timeout')}: 60s_
"""
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("cancel")}', 'premium_users_settings')]]))
    
    try:

        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        
        try:
            user_id = int(res.text.strip())
        except:
            await query.message.edit_text(f"❌ {sc('invalid user id')}!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))
            return
        
        await client.mongodb.remove_premium(user_id)
        
        await query.message.edit_text(
            f"✅ **{sc('premium removed')}!**\n\n"
            f"**{sc('user id')}:** `{user_id}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]])
        )
        
        # Notify user
        try:
            await client.send_message(
                user_id,
                f"⚠️ **{sc('your premium was removed')}**"
            )
        except:
            pass
            
    except ListenerTimeout:
        await query.message.edit_text(f"**⌚ {sc('timeout')}!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'premium_users_settings')]]))


@Client.on_callback_query(filters.regex("^auto_batch_settings$"))
async def auto_batch_settings(client, query):
    enabled = await client.mongodb.get_bot_config('auto_batch_enabled', False) # Default FALSE now
    mode = await client.mongodb.get_bot_config('auto_batch_mode', 'episode')
    window = await client.mongodb.get_bot_config('auto_batch_time_window', 30)

    status = f"✅ {sc('Enabled')}" if enabled else f"❌ {sc('Disabled')}"
    mode_text = "📺 Episodes (S01 E01)" if mode == 'episode' else "🎬 Series/Movie (Name [Quality])"
    
    msg = f"""<blockquote>**🤖 {sc('Auto-Batch Settings')}:**</blockquote>
**Status:** {status}
**Mode:** `{mode_text}`
**Time Window:** `{window}s`

__{sc('Automatically groups files sent to the channel into batches.')}__
__{sc('Turning this OFF will stop those annoying messages!')}__
"""
    toggle_text = f"🔴 {sc('Disable')}" if enabled else f"🟢 {sc('Enable')}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, 'toggle_auto_batch')],
        [InlineKeyboardButton(f'🔄 {sc("switch mode")}', 'toggle_batch_mode')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^toggle_auto_batch$"))
async def toggle_auto_batch(client, query):
    current = await client.mongodb.get_bot_config('auto_batch_enabled', False)
    await client.mongodb.set_bot_config('auto_batch_enabled', not current)
    await query.answer(f"Auto-Batch {'Disabled' if current else 'Enabled'}!")
    return await auto_batch_settings(client, query)

@Client.on_callback_query(filters.regex("^toggle_batch_mode$"))
async def toggle_batch_mode(client, query):
    current = await client.mongodb.get_bot_config('auto_batch_mode', 'episode')
    new_mode = 'season' if current == 'episode' else 'episode'
    await client.mongodb.set_bot_config('auto_batch_mode', new_mode)
    await query.answer(f"Switched to {new_mode.title()} Mode!")
    return await auto_batch_settings(client, query)

@Client.on_callback_query(filters.regex("^admins$"))
async def admins(client, query):
    if not (query.from_user.id==OWNER_ID):
        return await query.answer('This can only be used by owner.')
    msg = f"""<blockquote>**Admin Settings:**</blockquote>
**Admin User IDs:** {", ".join(f"`{a}`" for a in client.admins)}

__Use the appropriate button below to add or remove an admin based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_callback_query(filters.regex("^photos$"))
async def photos(client, query):
    msg = f"""<blockquote>**Force Subscription Settings:**</blockquote>
**Start Photo:** `{client.messages.get("START_PHOTO", "None")}`
**Force Sub Photo:** `{client.messages.get('FSUB_PHOTO', 'None')}`

__Use the appropriate button below to add or remove any admin based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if client.messages.get("START_PHOTO", "") == "" else 'ᴄʜᴀɴɢᴇ') + '\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', 
            callback_data='add_start_photo'
        ),
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if client.messages.get("FSUB_PHOTO", "") == "" else 'ᴄʜᴀɴɢᴇ') + '\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', 
            callback_data='add_fsub_photo'
        )
    ],
    [
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', callback_data='rm_start_photo'),
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', callback_data='rm_fsub_photo')
    ],
    [InlineKeyboardButton('◂ ʙᴀᴄᴋ', callback_data='settings')]

    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_callback_query(filters.regex("^protect$"))
async def protect(client, query):
    client.protect = False if client.protect else True
    return await settings(client, query)

@Client.on_callback_query(filters.regex("^url_shorteners$"))
async def url_shorteners(client, query):
    msg = f"""<blockquote>**URL Shortener Settings:**</blockquote>
**Configured Providers:** `{len(URL_SHORTENERS)}`
**Active Providers:** `{len([k for k, v in URL_SHORTENERS.items() if v.get('active', False)])}`

"""
    # Global System Status
    token_verification_enabled = await client.mongodb.get_bot_config('token_verification_enabled', True)
    system_status = "✅ Enabled" if token_verification_enabled else "❌ Disabled"
    msg += f"**Global Verification System:** {system_status}\n\n"

    for key, provider in URL_SHORTENERS.items():
        status = "✅ Active" if provider.get('active', False) else "❌ Inactive"
        msg += f"**{provider['name']}:** {status}\n"
        msg += f"  • API URL: `{provider['api_url']}`\n"
        msg += f"  • Token: `{provider.get('api_token', 'Not set')[:10]}...`\n\n"

    toggle_btn_text = "🔴 Disable System" if token_verification_enabled else "🟢 Enable System"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_btn_text, 'global_token_toggle')],
        [InlineKeyboardButton('⚠️ ᴀɴᴛɪ-ʙʏᴘᴀꜱꜱ ꜱᴇᴛᴛɪɴɢꜱ', 'anti_bypass_settings')],
        [InlineKeyboardButton('ᴀᴅᴅ ᴘʀᴏᴠɪᴅᴇʀ', 'add_shortener'), InlineKeyboardButton('ᴇᴅɪᴛ ᴘʀᴏᴠɪᴅᴇʀ', 'edit_shortener')],
        [InlineKeyboardButton('ᴛᴏɢɢʟᴇ ᴘʀᴏᴠɪᴅᴇʀ', 'toggle_shortener'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴘʀᴏᴠɪᴅᴇʀ', 'rm_shortener')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del(client, query):
    msg = f"""<blockquote>**Change Auto Delete Time:**</blockquote>
**Current Timer:** `{client.auto_del}`

__Enter new integer value of auto delete timer, keep 0 to disable auto delete and -1 to as it was, or wait for 60 second timeout to be comoleted!__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        timer = res.text.strip()
        if timer.isdigit() or (timer.startswith('+' or '-') and timer[1:].isdigit()):
            timer = int(timer)
            if timer >= 0:
                client.auto_del = timer
                # 💾 Save to MongoDB
                await client.mongodb.set_bot_config('auto_del', timer)
                return await query.message.edit_text(f'**Auto Delete timer vakue changed to {timer} seconds!**', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
            else:
                return await query.message.edit_text("**There is no change done in auto delete timer!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
        else:
            return await query.message.edit_text("**This is not an integer value!!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))

@Client.on_callback_query(filters.regex("^texts$"))
async def texts(client, query):
    msg = f"""<blockquote>**Text Configuration:**</blockquote>
**Start Message:**
<pre>{client.messages.get('START', 'Empty')}</pre>
**Force Sub Message:**
<pre>{client.messages.get('FSUB', 'Empty')}</pre>
**About Message:**
<pre>{client.messages.get('ABOUT', 'Empty')}</pre>
**Reply Message:**
<pre>{client.reply_text}</pre>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'ꜱᴛᴀʀᴛ ᴛᴇxᴛ', 'start_txt'), InlineKeyboardButton(f'ꜰꜱᴜʙ ᴛᴇxᴛ', 'fsub_txt')],
        [InlineKeyboardButton('ʀᴇᴘʟʏ ᴛᴇxᴛ', 'reply_txt'), InlineKeyboardButton('ᴀʙᴏᴜᴛ ᴛᴇxᴛ', 'about_txt')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_callback_query(filters.regex('^rm_start_photo$'))
async def rm_start_photo(client, query):
    client.messages['START_PHOTO'] = ''
    await query.answer()
    await photos(client, query)

@Client.on_callback_query(filters.regex('^rm_fsub_photo$'))
async def rm_fsub_photo(client, query):
    client.messages['FSUB_PHOTO'] = ''
    await query.answer()
    await photos(client, query)

@Client.on_callback_query(filters.regex("^add_start_photo$"))
async def add_start_photo(client, query):
    msg = f"""<blockquote>**Change Start Image:**</blockquote>
**Current Start Image:** `{client.messages.get('START_PHOTO', '')}`

__Enter new link of start image or send the photo, or wait for 60 second timeout to be comoleted!__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=(filters.text|filters.photo), timeout=60)
        if res.text and res.text.startswith('https://' or 'http://'):
            client.messages['START_PHOTO'] = res.text
            return await query.message.edit_text("**This link has been set at the place of start photo!!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        elif res.photo:
            loc = await res.download()
            client.messages['START_PHOTO'] = loc
            return await query.message.edit_text("**This image has been set as the starting image!!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        else:
            return await query.message.edit_text("**Invalid Photo or Link format!!**\n__If you're sending the link of any image it must starts with either 'http' or 'https'!__", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

@Client.on_callback_query(filters.regex("^add_fsub_photo$"))
async def add_fsub_photo(client, query):
    msg = f"""<blockquote>**Change Force Sub Image:**</blockquote>
**Current Force Sub Image:** `{client.messages.get('FSUB_PHOTO', '')}`

__Enter new link of fsub image or send the photo, or wait for 60 second timeout to be comoleted!__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=(filters.text|filters.photo), timeout=60)
        if res.text and res.text.startswith('https://' or 'http://'):
            client.messages['FSUB_PHOTO'] = res.text
            return await query.message.edit_text("**This link has been set at the place of fsub photo!!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        elif res.photo:
            loc = await res.download()
            client.messages['FSUB_PHOTO'] = loc
            return await query.message.edit_text("**This image has been set as the force sub image!!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        else:
            return await query.message.edit_text("**Invalid Photo or Link format!!**\n__If you're sending the link of any image it must starts with either 'http' or 'https'!__", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))


# URL Shortener Management Callbacks
@Client.on_callback_query(filters.regex("^add_shortener$"))
async def add_shortener(client, query):
    msg = f"""<blockquote>**Add New URL Shortener Provider:**</blockquote>

__Send the provider details in this format:__
```
provider_key|Provider Name|API URL|API Token|Format
```

**Example:**
```
bitly|Bitly|https://api-ssl.bitly.com/v4/shorten|YOUR_TOKEN|json
```

**Supported Formats:**
• `text` - Returns plain text URL
• `json` - Returns JSON response

__Send the details or wait for 60 second timeout to be completed!__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        details = res.text.strip().split('|')
        
        if len(details) != 5:
            return await query.message.edit_text("**Invalid format! Please use: provider_key|Name|API_URL|Token|Format**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider_key, name, api_url, api_token, format_type = details
        
        if provider_key in URL_SHORTENERS:
            return await query.message.edit_text(f"**Provider '{provider_key}' already exists!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        URL_SHORTENERS[provider_key] = {
            'name': name,
            'api_url': api_url,
            'api_token': api_token,
            'format': format_type,
            'active': True
        }
        
        return await query.message.edit_text(f"**✅ Provider '{name}' added successfully!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^edit_shortener$"))
async def edit_shortener(client, query):
    if not URL_SHORTENERS:
        return await query.answer("No providers configured!")
    
    msg = f"""<blockquote>**Edit URL Shortener Provider:**</blockquote>

**Available Providers:**
"""
    for key, provider in URL_SHORTENERS.items():
        status = "✅" if provider.get('active', False) else "❌"
        msg += f"{status} `{key}` - {provider['name']}\n"
    
    msg += f"\n__Send the provider key to edit or wait for 60 second timeout to be completed!__"
    
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        provider_key = res.text.strip()
        
        if provider_key not in URL_SHORTENERS:
            return await query.message.edit_text(f"**Provider '{provider_key}' not found!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider = URL_SHORTENERS[provider_key]
        msg = f"""<blockquote>**Edit Provider: {provider['name']}**</blockquote>

**Current Settings:**
• Name: `{provider['name']}`
• API URL: `{provider['api_url']}`
• Token: `{provider.get('api_token', 'Not set')[:15]}...`
• Format: `{provider.get('format', 'text')}`
• Active: `{"Yes" if provider.get('active', False) else "No"}`

__Send new details in format:__
```
Name|API URL|API Token|Format|Active(1/0)
```

**Example:**
```
Bitly Updated|https://api.bitly.com/v4/shorten|NEW_TOKEN|json|1
```
"""
        await query.message.edit_text(msg)
        try:
            res2 = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
            details = res2.text.strip().split('|')
            
            if len(details) != 5:
                return await query.message.edit_text("**Invalid format! Use: Name|API_URL|Token|Format|Active(1/0)**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
            
            name, api_url, api_token, format_type, active = details
            
            URL_SHORTENERS[provider_key] = {
                'name': name,
                'api_url': api_url,
                'api_token': api_token,
                'format': format_type,
                'active': active == '1'
            }
            
            return await query.message.edit_text(f"**✅ Provider '{name}' updated successfully!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
            
        except ListenerTimeout:
            return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^toggle_shortener$"))
async def toggle_shortener(client, query):
    if not URL_SHORTENERS:
        return await query.answer("No providers configured!")
    
    msg = f"""<blockquote>**Toggle URL Shortener Active Status:**</blockquote>

**Available Providers:**
"""
    for key, provider in URL_SHORTENERS.items():
        status = "✅ Active" if provider.get('active', False) else "❌ Inactive"
        msg += f"• `{key}` - {provider['name']} ({status})\n"
    
    msg += f"\n__Send the provider key to toggle or wait for 60 second timeout to be completed!__"
    
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        provider_key = res.text.strip()
        
        if provider_key not in URL_SHORTENERS:
            return await query.message.edit_text(f"**Provider '{provider_key}' not found!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider = URL_SHORTENERS[provider_key]
        current_status = provider.get('active', False)
        provider['active'] = not current_status
        
        status_text = "activated" if provider['active'] else "deactivated"
        return await query.message.edit_text(f"**✅ Provider '{provider['name']}' {status_text} successfully!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))


@Client.on_callback_query(filters.regex("^rm_shortener$"))
async def rm_shortener(client, query):
    if not URL_SHORTENERS:
        return await query.answer("No providers configured!")
    
    msg = f"""<blockquote>**Remove URL Shortener Provider:**</blockquote>

**Available Providers:**
"""
    for key, provider in URL_SHORTENERS.items():
        status = "✅ Active" if provider.get('active', False) else "❌ Inactive"
        msg += f"• `{key}` - {provider['name']} ({status})\n"
    
    msg += f"\n__Send the provider key to remove or wait for 60 second timeout to be completed!__\n"
    msg += f"**⚠️ Warning:** This action cannot be undone!"
    
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        provider_key = res.text.strip()
        
        if provider_key not in URL_SHORTENERS:
            return await query.message.edit_text(f"**Provider '{provider_key}' not found!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
        provider_name = URL_SHORTENERS[provider_key]['name']
        del URL_SHORTENERS[provider_key]
        
        return await query.message.edit_text(f"**✅ Provider '{provider_name}' removed successfully!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))
        
    except ListenerTimeout:
        return await query.message.edit_text("**Timeout, try again!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'url_shorteners')]]))

@Client.on_callback_query(filters.regex("^global_token_toggle$"))
async def global_token_toggle(client, query):
    current_status = await client.mongodb.get_bot_config('token_verification_enabled', True)
    new_status = not current_status
    await client.mongodb.set_bot_config('token_verification_enabled', new_status)
    await query.answer(f"System {'Enabled' if new_status else 'Disabled'}!")
    return await url_shorteners(client, query)

@Client.on_callback_query(filters.regex("^anti_bypass_settings$"))
async def anti_bypass_settings(client, query):
    bypass_check_enabled = await client.mongodb.get_bot_config('bypass_check_enabled', True)
    bypass_timer = await client.mongodb.get_bot_config('bypass_timer', 60)
    
    status = f"✅ {sc('Enabled')}" if bypass_check_enabled else f"❌ {sc('Disabled')}"
    
    msg = f"""<blockquote>**⚠️ {sc('Anti-Bypass System Configuration')}:**</blockquote>

**{sc('System Status')}:** {status}
**{sc('Minimum Wait Time')}:** `{bypass_timer} {sc('seconds')}`

__{sc('This system prevents users from solving the shortener too quickly (skipping ads)')}.__
"""
    toggle_text = f"🔴 {sc('Disable')}" if bypass_check_enabled else f"🟢 {sc('Enable')}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_text, 'toggle_bypass_check'), InlineKeyboardButton(f'⏰ {sc("change timer")}', 'set_bypass_timer')],
        [InlineKeyboardButton(f'◂ {sc("back")}', 'url_shorteners')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^toggle_bypass_check$"))
async def toggle_bypass_check(client, query):
    current = await client.mongodb.get_bot_config('bypass_check_enabled', True)
    await client.mongodb.set_bot_config('bypass_check_enabled', not current)
    await query.answer(f"{sc('Anti-Bypass System')} {'Disabled' if current else 'Enabled'}!")
    return await anti_bypass_settings(client, query)

@Client.on_callback_query(filters.regex("^set_bypass_timer$"))
async def set_bypass_timer(client, query):
    msg = f"""<blockquote>**{sc('change anti-bypass timer')}:**</blockquote>
    
__{sc('enter the minimum time (in seconds) a user must take to solve the shortener')}.__
__{sc('default is 60 seconds')}.__

__{sc('send the number or wait for timeout')}!__
"""
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        if res.text.isdigit():
            timer = int(res.text)
            await client.mongodb.set_bot_config('bypass_timer', timer)
            await query.message.edit_text(f"**{sc('timer updated to')} {timer} {sc('seconds')}!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'anti_bypass_settings')]]))
        else:
            await query.message.edit_text(f"**{sc('invalid number')}!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'anti_bypass_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text(f"**{sc('timeout')}!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'◂ {sc("back")}', 'anti_bypass_settings')]]))
