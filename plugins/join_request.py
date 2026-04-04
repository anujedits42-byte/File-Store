# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest

@Client.on_chat_join_request()
async def handle_join_request(client, join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    channel_id = join_request.chat.id
    
    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return
    
    channel = client.fsub_dict.get(channel_id, [])
    if channel:
        # Track this join
        await client.mongodb.add_channel_user(channel_id, user_id)
        # Approve the join request so user actually joins
        try:
            await client.approve_chat_join_request(channel_id, user_id)
        except Exception:
            pass
