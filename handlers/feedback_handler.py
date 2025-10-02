import os
from datetime import datetime
from utils.websocket_utils import send_message
from config import TARGET_GROUP_ID, ADMIN_GROUP_ID, TEST_GROUP_ID, LOGS_DIR


def log_feedback_record(user_id, group_id, message):
    """记录反馈信息到单独的文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = f"{timestamp} | 反馈用户: {user_id} | 所在群聊: {group_id} | 内容: {message}\n"

    os.makedirs(LOGS_DIR, exist_ok=True)
    # 写入反馈日志文件
    with open(f"{LOGS_DIR}/feedback_records.txt", "a", encoding="utf-8") as f:
        f.write(record)

    return record


async def handle_feedback_command(message_text, user_id, group_id, websocket):
    """处理反馈命令"""
    parts = message_text.split()
    if len(parts) >= 3:
        message = " ".join(parts[2:])  # 反馈内容（合并剩余部分）
        operator = user_id
        # 记录反馈信息
        log_entry = log_feedback_record(
            user_id=user_id,
            group_id=group_id,
            message=message
        )
        print(f"已记录反馈信息:\n{log_entry}")
        feedback_msg = f"成功发送反馈: {message}"
        await send_message(websocket, feedback_msg, group_id=group_id)
        feedback_msg = f"用户[CQ:at,qq={operator}]反馈,所在群聊{group_id}\n内容: {message}"
        await send_message(websocket, feedback_msg, group_id=ADMIN_GROUP_ID)
        return True
    else:
        # 命令格式错误反馈
        error_feedback = "命令格式错误！正确格式: /try ref 反馈内容"
        await send_message(websocket, error_feedback, group_id=group_id)
        return False