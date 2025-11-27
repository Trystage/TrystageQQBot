from config import ADMIN_GROUP_ID, TEST_GROUP_ID


async def handle_help_command(message_text, user_id, group_id, message_type):
    """处理帮助命令"""
    # 检查用户是否在管理员群或测试群
    is_admin_or_test_group = group_id == ADMIN_GROUP_ID or group_id == TEST_GROUP_ID
    
    # 构造帮助信息
    if is_admin_or_test_group:
        # 管理员或测试群用户帮助信息
        help_message = """Trystage QQ Bot 帮助信息（管理员）：
    
基础命令：
/try ref <反馈内容> - 向管理组发送反馈信息
/try report <QQ> <原因>

管理员专用命令：
/try announce <公告内容> - 发送公告到指定群组
/try mute <QQ号> <时长(秒)> <原因> - 对指定用户进行禁言操作
/try add (yinpa/join) [群号1] [群号2] ... - 添加银趴或入群事件处理群组

使用示例：
/try report @rootlaw03 刷屏
/try ref 管理组变女仆!
/try announce qq机器猫更新啦!
/try mute 3289138258 600 Advertising - 禁言玩家3289138258 10分钟，原因：Advertising
/try add yinpa 114514 1919810 - 添加银趴功能群组
/try add join 114514 1919810 - 添加入群事件处理群组

注意：您当前在管理员或测试群组中，可以使用所有命令。"""
    else:
        # 普通用户帮助信息
        help_message = """Trystage QQ Bot 帮助信息：
    
基础命令：
/try ref <反馈内容> - 向管理组发送反馈信息
/try report <QQ> <原因>

使用示例：
/try report @rootlaw03 刷屏
/try ref 管理组变女仆!
投喂好次的请使用/try ref反馈给我取件码~~"""
    
    # 构造响应消息
    response_message = {
        "action": "send_msg",
        "params": {
            "user_id": user_id if message_type == "private" else None,
            "group_id": group_id if message_type == "group" else None,
            "message": help_message
        }
    }
    
    return response_message