from config import ADMIN_GROUP_ID, TEST_GROUP_ID, GROUP_IDS
from utils.file_utils import FileUtils
from utils.websocket_utils import send_message


async def handle_add_group_command(message_text, user_id, group_id, message_type, websocket):
    """处理添加群组ID命令"""
    # 检查用户是否在管理员群或测试群
    is_admin_or_test_group = group_id == ADMIN_GROUP_ID or group_id == TEST_GROUP_ID

    if not is_admin_or_test_group:
        await send_message(websocket, "错误：您没有权限执行此命令", user_id, group_id)
        return

    # 解析命令参数
    parts = message_text.split()

    # 检查命令格式
    if len(parts) < 3:
        await send_message(websocket,
                           "错误：命令格式不正确\n正确格式：/try add (yinpa/join/black/jm) [群号1] [群号2] ...\n例如：/try add yinpa 114514 1919810",
                           user_id, group_id)
        return

    # 获取命令类型（yinpa或join）
    command_type = parts[2]

    # 检查命令类型是否有效
    if command_type not in ["yinpa", "join", "black", "jm"]:
        await send_message(websocket, "错误：命令类型不正确，只能是 yinpa, black, jm 或 join", user_id, group_id)
        return

    # 获取要添加的群组ID列表
    try:
        group_ids = [int(part) for part in parts[3:]]
    except ValueError:
        await send_message(websocket, "错误：群号必须是数字", user_id, group_id)
        return

    # 添加群组ID
    added_groups = []
    failed_groups = []

    for gid in group_ids:
        try:
            if command_type == "yinpa":
                FileUtils.add_yinpa_group_id(gid)
            elif command_type == "join":
                FileUtils.add_joinchat_group_id(gid)
            elif command_type == "black":
                FileUtils.add_black_group_id(gid)
            elif command_type == "jm":
                FileUtils.add_jm_group_id(gid)
            added_groups.append(str(gid))
        except Exception as e:
            failed_groups.append(f"{gid} ({str(e)})")

    # 构造响应消息
    response_message = "群组ID添加完成：\n"

    if added_groups:
        response_message += f"成功添加的{command_type}群组：{', '.join(added_groups)}\n"

    if failed_groups:
        response_message += f"添加失败的群组：{', '.join(failed_groups)}\n"

    # 显示当前所有群组ID
    if command_type == "yinpa":
        current_groups = GROUP_IDS.YINPA_GROUP_IDS
    elif command_type == "join":
        current_groups = GROUP_IDS.JOINCHAT_GROUP_IDS
    elif command_type == "black":
        current_groups = GROUP_IDS.BLACK_GROUP_IDS
    elif command_type == "jm":
        current_groups = GROUP_IDS.JM_GROUP_IDS

    response_message += f"\n当前{command_type}群组列表：{', '.join(map(str, current_groups))}"

    await send_message(websocket, response_message, user_id, group_id)

async def handle_remove_group_command(message_text, user_id, group_id, message_type, websocket):
    """处理删除群组ID命令"""
    # 检查用户是否在管理员群或测试群
    is_admin_or_test_group = group_id == ADMIN_GROUP_ID or group_id == TEST_GROUP_ID

    if not is_admin_or_test_group:
        await send_message(websocket, "错误：您没有权限执行此命令", user_id, group_id)
        return

    # 解析命令参数
    parts = message_text.split()

    # 检查命令格式
    if len(parts) < 3:
        await send_message(websocket, "错误：命令格式不正确\n正确格式：/try rem (yinpa/join/black/jm) [群号1] [群号2] ...\n例如：/try rem yinpa 114514 1919810", user_id, group_id)
        return

    # 获取命令类型（yinpa或join）
    command_type = parts[2]

    # 检查命令类型是否有效
    if command_type not in ["yinpa", "join", "black", "jm"]:
        await send_message(websocket, "错误：命令类型不正确，只能是 yinpa, black, jm 或 join", user_id, group_id)
        return

    # 获取要添加的群组ID列表
    try:
        group_ids = [int(part) for part in parts[3:]]
    except ValueError:
        await send_message(websocket, "错误：群号必须是数字", user_id, group_id)
        return

    # 添加群组ID
    removed_groups = []
    failed_groups = []

    for gid in group_ids:
        try:
            if command_type == "yinpa":
                FileUtils.remove_yinpa_group_id(gid)
            elif command_type == "join":
                FileUtils.remove_joinchat_group_id(gid)
            elif command_type == "black":
                FileUtils.remove_black_group_id(gid)
            elif command_type == "jm":
                FileUtils.remove_jm_group_id(gid)
            removed_groups.append(str(gid))
        except Exception as e:
            failed_groups.append(f"{gid} ({str(e)})")

    # 构造响应消息
    response_message = "群组ID删除完成：\n"

    if removed_groups:
        response_message += f"成功删除的{command_type}群组：{', '.join(removed_groups)}\n"

    if failed_groups:
        response_message += f"删除失败的群组：{', '.join(failed_groups)}\n"

    # 显示当前所有群组ID
    if command_type == "yinpa":
        current_groups = GROUP_IDS.YINPA_GROUP_IDS
    elif command_type == "join":
        current_groups = GROUP_IDS.JOINCHAT_GROUP_IDS
    elif command_type == "black":
        current_groups = GROUP_IDS.BLACK_GROUP_IDS
    elif command_type == "jm":
        current_groups = GROUP_IDS.JM_GROUP_IDS

    response_message += f"\n当前{command_type}群组列表：{', '.join(map(str, current_groups))}"

    await send_message(websocket, response_message, user_id, group_id)