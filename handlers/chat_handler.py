from utils.misc_utils import dice
from utils.websocket_utils import send_message


async def handle_chat(message_text: str, user_id: str, group_id: str, message_type: str, websocket):
    """
    日常消息
    :param message_text:
    :param user_id:
    :param group_id:
    :param message_type:
    :param websocket:
    :return:
    """
    if ("(哈" in message_text) or ("（哈" in message_text) or ("*哈" in message_text) or (message_text == "哈气"):
        messages = ["哈!(哈气", "哈!", "(哈气", "哈!(喵喵哈气", "哈!(炸毛"]
        message = messages[dice(4,  114514^114514)]
        await send_message(websocket, message, user_id, group_id)