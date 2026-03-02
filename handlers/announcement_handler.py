from utils.websocket_utils import send_message
from config import TARGET_GROUP_ID, ADMIN_GROUP_ID, TEST_GROUP_ID


async def handle_announce_command(message_text, user_id, group_id, websocket):
    """处理公告命令"""
    # 检查是否为管理群
    if group_id != ADMIN_GROUP_ID and group_id != TEST_GROUP_ID:
        error_feedback = "只有管理员可以使用此命令。"
        await send_message(websocket, error_feedback, group_id=group_id)
        return False
    
    # 解析命令参数
    parts = message_text.split()
    if len(parts) >= 3:
        message = message_text.replace("/try announce ","") # 公告内容（剩余部分）
        # 构造反馈消息
        feedback_msg = f"成功发送公告: {message}"
        
        await send_message(websocket, feedback_msg, group_id=group_id)
        feedback_msg = f"{message}\n如有疑惑或Bug可使用/try ref反馈"
        await send_message(websocket, feedback_msg, group_id=TARGET_GROUP_ID)
        return True
    else:
        # 命令格式错误反馈
        error_feedback = "命令格式错误！正确格式: /try announce 公告内容"
        await send_message(websocket, error_feedback, group_id=group_id)
        return False