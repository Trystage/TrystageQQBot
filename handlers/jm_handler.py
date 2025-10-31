from modules.jm.handler import handle_jm, handle_jmzip
async def handle_jm_command(message_text: str, user_id: str, group_id: str, message_type: str, websocket):
    """处理jm命令 - NapCat版本"""
    if message_text.startswith("jmz") or message_text.startswith("jmczip") or message_text.startswith("jmcomiczip") or message_text.startswith("jmzip"):
        await handle_jmzip(message_text, user_id, group_id, websocket)
    elif message_text.startswith("jm") or message_text.startswith("jmcomic") or message_text.startswith("jmc"):
        await handle_jm(message_text, user_id, group_id, websocket)
