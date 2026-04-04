# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import MSG_EFFECT


@Client.on_callback_query(filters.regex('^home$'))
async def menu_callback(client, query: CallbackQuery):
    user_id = query.from_user.id

    # base buttons (visible to everyone)
    buttons = [
        [InlineKeyboardButton("⌜UPDATES⌟", url="https://t.me/Awakeners_bots"),
         InlineKeyboardButton("⌜ɴᴇᴛᴡᴏʀᴋ⌟", url="https://t.me/The_Mortals")],
        [InlineKeyboardButton("⌜ᴀʙᴏᴜᴛ⌟", callback_data="about"),
         InlineKeyboardButton("⌜ᴅᴇᴠ⌟", url="https://t.me/GPGMS0")]
    ]

    # ✅ Only admins see the Settings button
    if user_id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("⌜ꜱᴇᴛᴛɪɴɢꜱ⌟", callback_data="settings")])

    await query.message.edit_text(
        text=client.messages.get('START', 'No Start Message').format(
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return


@Client.on_callback_query(filters.regex('^about$'))
async def about(client: Client, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="home")]]
    await query.message.edit_text(
        text=client.messages.get('ABOUT', 'No Start Message').format(
            owner_id=client.owner,
            bot_username=client.username,
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return


@Client.on_callback_query(filters.regex('^premium_plans$'))
async def premium_plans_callback(client: Client, query: CallbackQuery):
    """Handle premium plans button callback"""
    premium_text = (
        "Hᴇʟʟᴏ <b>{}</b>, \n\n"
        "• Wʜɪᴄʜ Pʟᴀɴ Dᴏ Yᴏᴜ Wᴀɴᴛ Tᴏ Bᴜʏ?\n"
        "📜 <b>Pʀɪᴄɪɴɢ:</b>\n"
        "╭──────────\n"
        "↻ ₹99 / $1 : 1 Mᴏɴᴛʜ\n"
        "↻ ₹179 / $2 : 2 Mᴏɴᴛʜs\n"
        "↻ ₹249/ $2.5: 3 Mᴏɴᴛʜs (Mᴏsᴛ Bᴏᴜɢʜᴛ)\n"
        "↻ ₹399 / $6 : 6 Mᴏɴᴛʜs\n"
        "↻ ₹699/ $10 : 9 Mᴏɴᴛʜs\n"
        "↻ ₹999 / $12 : 12 Mᴏɴᴛʜs\n"
        "╰──────────\n\n"
        "<b>💎 Pʀᴇᴍɪᴜᴍ Bᴇɴᴇғɪᴛs:</b>\n"
        "✓ Dɪʀᴇᴄᴛ Fɪʟᴇ Aᴄᴄᴇss\n"
        "✓ Nᴏ Aᴅs ᴏʀ URL Sʜᴏʀᴛᴇɴᴇʀs\n"
        "✓ Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ\n"
        "✓ Fᴀsᴛ Dᴏᴡɴʟᴏᴀᴅs\n\n"
        "Cᴏɴᴛᴀᴄᴛ Hᴇʀᴇ Fᴏʀ Fᴜʀᴛʜᴇʀ Iɴǫᴜɪʀʏ - @Cultured_Support_bot"
    ).format(query.from_user.first_name)
    
    buttons = [
        [InlineKeyboardButton("💰 Bᴜʏ Pʀᴇᴍɪᴜᴍ", url="https://t.me/Cultured_Support_bot?start=0")],
        [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="home")]
    ]
    
    await query.message.edit_text(
        text=premium_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return


@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
                continue
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} users have been banned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")


@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
                continue
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} users have been unbanned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")
