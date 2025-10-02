import os
from datetime import datetime
from utils.websocket_utils import send_message, send_mute
from config import TARGET_GROUP_ID, ADMIN_GROUP_ID, TEST_GROUP_ID, LOGS_DIR


def format_duration(seconds):
    """将秒数转换为更易读的格式"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        return f"{seconds // 60}分钟"
    elif seconds < 86400:
        return f"{seconds // 3600}小时"
    else:
        return f"{seconds // 86400}天"


def log_ban_record(user_id, duration, reason, operator):
    """记录封禁信息到单独的文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = f"{timestamp} | 被封禁人: {user_id} | 时长: {duration}秒 | 操作者: {operator} | 原因: {reason}\n"

    os.makedirs(LOGS_DIR, exist_ok=True)
    # 写入封禁日志文件
    with open(f"{LOGS_DIR}/ban_records.txt", "a", encoding="utf-8") as f:
        f.write(record)

    return record


async def handle_mute_command(message_text, user_id, group_id, websocket):
    """处理禁言命令"""
    # 检查是否为管理群
    if group_id != ADMIN_GROUP_ID and group_id != TEST_GROUP_ID:
        error_feedback = "只有管理员可以使用此命令。"
        await send_message(websocket, error_feedback, group_id=group_id)
        return False
    
    # 解析命令参数
    parts = message_text.split()
    if len(parts) >= 5:
        target_qq = int(parts[2])  # 要禁言的QQ号
        duration = int(parts[3])  # 禁言时长（秒）
        reason = " ".join(parts[4:])  # 原因（合并剩余部分）
        
        # 记录封禁信息
        log_entry = log_ban_record(
            user_id=target_qq,
            duration=duration,
            reason=reason,
            operator=user_id
        )
        print(f"已记录封禁信息:\n{log_entry}")
        # 执行禁言
        await send_mute(websocket, TARGET_GROUP_ID, target_qq, duration)
        print(f"已发送禁言指令: QQ:{target_qq} 时长:{duration}秒")
        # 反馈消息
        feedback_msg = f"[CQ:at,qq={target_qq}] 被禁言,时长: {format_duration(duration)}\n原因: {reason}"
        await send_message(websocket, feedback_msg, group_id=TARGET_GROUP_ID)
        await send_message(websocket, feedback_msg, group_id=group_id)
        # 管理员群反馈
        feedback_msg = f"{target_qq} 被禁言,时长: {format_duration(duration)}\n原因: {reason}"
        await send_message(websocket, feedback_msg, group_id=ADMIN_GROUP_ID)
        return True
    else:
        # 命令格式错误反馈
        error_feedback = "命令格式错误！正确格式: /try mute QQ号 时长(秒) 原因\n示例: /try mute 3289138258 600 Advertising(劣质广告)"
        await send_message(websocket, error_feedback, group_id=group_id)
        return False