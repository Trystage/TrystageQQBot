import json
import re

from functools import wraps

from config import SUPER_USER, ADMIN_GROUP_ID, TEST_GROUP_ID


async def send_response(websocket, user_id, group_id, message_type, message):
    """发送响应消息"""
    response_message = {
        "action": "send_msg",
        "params": {
            "user_id": user_id if message_type == "private" else None,
            "group_id": group_id if message_type == "group" else None,
            "message": message
        }
    }
    response_json = json.dumps(response_message)
    await websocket.send(response_json)


def get_image(path: str):
    return f"[CQ:image,file=file:///{path}]"
async def send_message(websocket, message, user_id=None, group_id=None):
    """发送消息到指定用户或群组"""
    if user_id is None and group_id is None:
        raise ValueError("必须提供user_id或group_id")

    response_message = {
        "action": "send_msg",
        "params": {
            "user_id": user_id,
            "group_id": group_id,
            "message": message
        }
    }
    response_json = json.dumps(response_message)
    await websocket.send(response_json)


async def send_mute(websocket, group_id, user_id, duration):
    """发送禁言命令到指定群组"""
    mute_action = {
        "action": "set_group_ban",
        "params": {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration
        }
    }
    response_json = json.dumps(mute_action)
    await websocket.send(response_json)


def parse_message_data(message):
    """解析消息数据"""
    try:
        data = json.loads(message)
        return data
    except Exception as e:
        print(f"解析消息时出错: {e}")
        return None


def extract_user_info(data):
    """提取用户信息"""
    user_id = data.get("user_id")
    message_text = data.get("message")
    message_type = data.get("message_type")
    group_id = data.get("group_id", None)
    return user_id, message_text, message_type, group_id


async def get_user_nickname(websocket, user_id):
    """获取昵称"""
    request_msg = {
        "action": "get_stranger_info",
        "params": {
            "user_id": user_id,
        }
        }
    try:
        await websocket.send(json.dumps(request_msg))
        # 接收响应
        response = await websocket.recv()
        response_data = json.loads(response)
        if "data" in response_data and "nickname" in response_data["data"]:
            return response_data["data"]["nickname"]
    except Exception as e:
        print(f"解析消息时出错: {e}")
        return None

async def get_group_member_list(websocket, group_id):
        """获取群成员列表"""
        try:
            # 构建请求消息
            request_msg = {
                "action": "get_group_member_list",
                "params": {
                    "group_id": group_id,
                    "no_cache": False
                }
            }

            # 发送请求
            await websocket.send(json.dumps(request_msg))
            print(f"已发送请求: {request_msg}")

            # 接收响应
            response = await websocket.recv()
            response_data = json.loads(response)

            # 检查响应状态
            if response_data.get("status") == "ok" and response_data.get("retcode") == 0:
                print("成功获取群成员列表")
                return response_data
            else:
                print(f"获取群成员列表失败: {response_data.get('message', '未知错误')}")
                return response_data
        except Exception as e:
            print(f"解析消息时出错: {e}")
            return None
def extract_qq(input_data):
    """提取QQ号"""
    # 如果输入是整数，直接处理
    if isinstance(input_data, int):
        qq_str = str(input_data)
        return input_data

    # 如果输入是字符串
    if isinstance(input_data, str):
        # 尝试匹配 CQ 码格式
        cq_match = re.search(r'\[CQ:at,qq=(\d+)\]', input_data)
        if cq_match:
            qq_str = cq_match.group(1)
            try:
                qq_int = int(qq_str)
                return qq_int
            except ValueError:
                return None

        # 尝试匹配纯数字 QQ 号码（10-11位）
        pure_qq_match = re.search(r'(?<!\d)([1-9]\d{4,10})(?!\d)', input_data)
        if pure_qq_match:
            qq_str = pure_qq_match.group(1)
            try:
                qq_int = int(qq_str)
                return qq_int
            except ValueError:
                return None

    # 其他情况返回 None
    return None


async def get_group_member_info(websocket, group_id: int, user_id: int, no_cache: bool = False) -> dict:
    """获取群成员信息"""
    # 构建请求消息
    request_msg = {
        "action": "get_group_member_info",
        "params": {
            "group_id": group_id,
            "user_id": user_id,
            "no_cache": no_cache
        }
    }
    try:
        # 发送请求
        await websocket.send(json.dumps(request_msg))

        # 等待并查找匹配的响应
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            return response_data

    except Exception as e:
        print(f"获取群成员信息失败: {e}")
        return None

async def check_user_role(websocket, group_id: int, user_id: int) -> bool:
    """检查用户在群内是否为管理员或群主
    Args:
        websocket: WebSocket连接
        group_id: 群号
        user_id: 用户QQ号
    Returns:
        bool: 是否是管理员或群主
    """
    if user_id in SUPER_USER:
        return True
    # 获取群成员信息
    member_info = await get_group_member_info(websocket, group_id, user_id)

    if not member_info or member_info.get("status") != "ok":
        return False

    role = member_info.get("data", {}).get("role", "")
    # role 可能的值: "owner"（群主）, "admin"（管理员）, "member"（普通成员）
    return role in ["admin", "owner"]

def require_group_admin_ws(func):
    """要求用户必须是群管理员或群主(websocket, data)"""

    @wraps(func)
    async def wrapper(websocket, data):
        user_id = int(data.get('user_id'))
        group_id = int(data.get('group_id'))

        has_permission = await check_user_role(websocket, group_id, user_id)
        if not has_permission:
            # 权限不足的处理
            response_msg = {
                "action": "send_group_msg",
                "params": {
                    "group_id": group_id,
                    "message": "权限不足：只有群管理员或群主才能使用此命令"
                }
            }
            await websocket.send(json.dumps(response_msg))
            return

        # 有权限，执行原函数
        return await func(websocket, data)

    return wrapper

def require_master_ws(func):
    """要求用户必须是机器猫猫主人(websocket, data)"""

    @wraps(func)
    async def wrapper(websocket, data):
        user_id = int(data.get('user_id'))
        group_id = int(data.get('group_id'))

        has_permission = (group_id == ADMIN_GROUP_ID or group_id == TEST_GROUP_ID or user_id in SUPER_USER)
        if not has_permission:
            # 权限不足的处理
            response_msg = {
                "action": "send_group_msg",
                "params": {
                    "group_id": group_id,
                    "message": "权限不足：只有机器猫猫主人才能使用此命令"
                }
            }
            await websocket.send(json.dumps(response_msg))
            return

        # 有权限，执行原函数
        return await func(websocket, data)

    return wrapper

def get_at(message: str):
    """
    从消息中提取所有@的QQ号

    Args:
        message (str): 消息内容，可能包含CQ码格式的@

    Returns:
        list: 包含所有被@的QQ号的列表，如果是@全体则返回['all']
    """
    # 如果消息为空，返回空列表
    if not message:
        return []

    # 检查是否@全体成员
    if '[CQ:at,qq=all]' in message:
        return ['all']

    # 使用正则表达式匹配所有CQ码格式的@
    at_pattern = r'\[CQ:at,qq=(\d+)\]'
    matches = re.findall(at_pattern, message)

    # 返回所有匹配到的QQ号
    return matches