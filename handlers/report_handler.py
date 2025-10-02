import re
import os
from datetime import datetime
from utils.websocket_utils import send_message, extract_qq
from config import TARGET_GROUP_ID, ADMIN_GROUP_ID, TEST_GROUP_ID, LOGS_DIR



def log_report_record(user_id, reason, operator):
    """记录举报信息到单独的文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = f"{timestamp} | 被举报人: {user_id} | 举报者: {operator} | 原因: {reason}\n"

    os.makedirs(LOGS_DIR, exist_ok=True)
    # 写入举报日志文件
    with open(f"{LOGS_DIR}/report_records.txt", "a", encoding="utf-8") as f:
        f.write(record)

    return record


async def handle_report_command(message_text, user_id, group_id, websocket):
    """处理举报命令"""
    parts = message_text.split()
    if len(parts) >= 3:
        target_qq = extract_qq(parts[2])
        reason = " ".join(parts[3:])
        operator = user_id
        log_entry = log_report_record(
            user_id=target_qq,
            reason=reason,
            operator=user_id
        )
        print(f"已记录举报信息:\n{log_entry}")
        feedback_msg = f"[CQ:at,qq={target_qq}] 成功被举报\n原因: {reason}"
        await send_message(websocket, feedback_msg, group_id=group_id)
        feedback_msg = f"[CQ:at,qq={target_qq}] 被举报,举报人[CQ:at,qq={operator}],所在群聊{group_id}\n原因: {reason}"
        await send_message(websocket, feedback_msg, group_id=ADMIN_GROUP_ID)
        return True
    else:
        # 命令格式错误反馈
        error_feedback = "命令格式错误！正确格式: /try report QQ号 原因\n示例: /try report 3289138258 喵喵喵"
        await send_message(websocket, error_feedback, group_id=group_id)
        return False