import asyncio
import json
import traceback

import websockets

from commands.base_commands import (
    is_announce_command,
    is_feedback_command,
    is_mute_command,
    is_report_command,
    is_help_command,
    is_add_group_command,
    is_yinpa_command, is_remove_group_command,
    is_jm_command
)
from handlers.announcement_handler import handle_announce_command
from handlers.chat_handler import handle_chat
from handlers.feedback_handler import handle_feedback_command
from handlers.jm_handler import handle_jm_command
from handlers.pokeneko_handler import handle_poke_neko
from handlers.punishment_handler import handle_mute_command
from handlers.report_handler import handle_report_command
from handlers.help_handler import handle_help_command
from handlers.group_handler import handle_add_group_command, handle_remove_group_command
from handlers.joinchat_handler import handle_join_event
from handlers.yinpa_handler import handle_yinpa_command
from config import WEBSOCKET_HOST, WEBSOCKET_PORT, GROUP_IDS
from utils.misc_utils import truncate_error_message
from utils.websocket_utils import send_message
from utils.file_utils import FileUtils


async def handle_message(websocket):
    print(f"运行在ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/ws")
    print("等待消息...")
    async for message in websocket:
        try:
            data = json.loads(message)
            print(f"收到消息:  {data}")
            self_id = data.get("self_id")
            # 处理消息类型
            if "post_type" in data and data["post_type"] == "message":
                user_id = data["user_id"]
                message_text = data["message"]
                message_type = data["message_type"]
                group_id = data.get("group_id", None)
                response_message = None

                # 处理公告命令
                if is_announce_command(message_text, group_id):
                    await handle_announce_command(message_text, group_id, websocket)
                    # 不需要额外的response_message，因为handle_announce_command已经发送了响应

                # 处理反馈命令
                elif is_feedback_command(message_text):
                    await handle_feedback_command(message_text, user_id, group_id, websocket)
                    # 不需要额外的response_message，因为handle_feedback_command已经发送了响应

                # 处理禁言命令
                elif is_mute_command(message_text, group_id):
                    await handle_mute_command(message_text, user_id, group_id, websocket)
                    # 不需要额外的response_message，因为handle_mute_command已经发送了响应

                # 处理举报命令
                elif is_report_command(message_text):
                    await handle_report_command(message_text, user_id, group_id, websocket)
                    # 不需要额外的response_message，因为handle_report_command已经发送了响应

                # 处理帮助命令
                elif is_help_command(message_text):
                    response_message = await handle_help_command(message_text, user_id, group_id, message_type)

                # 处理添加群组ID命令
                elif is_add_group_command(message_text, group_id):
                    await handle_add_group_command(message_text, user_id, group_id, message_type, websocket)
                    # 响应由handle_add_group_command内部处理，不需要额外的response_message
                # 处理添加群组ID命令
                elif is_remove_group_command(message_text, group_id):
                    await handle_remove_group_command(message_text, user_id, group_id, message_type, websocket)
                    # 响应由handle_add_group_command内部处理，不需要额外的response_message

                # 处理银趴命令
                elif is_yinpa_command(message_text):
                    group_id = data.get("group_id", None)
                    if group_id in GROUP_IDS.YINPA_GROUP_IDS:
                        await handle_yinpa_command(message_text, str(user_id), str(group_id), message_type, websocket)
                    # 银趴命令的响应由handle_yinpa_command内部处理，不需要额外的response_message

                # 处理jm命令
                elif is_jm_command(message_text):
                    group_id = data.get("group_id", None)
                    # if group_id in GROUP_IDS.JM_GROUP_IDS:
                        # await handle_jm_command(message_text, str(user_id), str(group_id), message_type, websocket)
                        # await send_message(websocket, "jm没写好qwq, 卡爆了, 先关了qwq", user_id, group_id)
                    # 银趴命令的响应由handle_yinpa_command内部处理，不需要额外的response_message
                else:
                    await handle_chat(message_text, user_id, group_id, message_type, websocket)

                # 发送响应消息（如果有的话）
                if response_message:
                    response_json = json.dumps(response_message)
                    await websocket.send(response_json)
            
            # 处理通知类型（如群成员加入）
            elif "post_type" in data and data["post_type"] == "notice":

                group_id = data.get("group_id", None)
                user_id = data.get("user_id", None)
                noticetype = data.get("notice_type", None)
                sub_type = data.get("sub_type", None)

                print(f"通知类型: {noticetype}, 群号: {group_id}, 用户ID: {user_id}")

                # 检查是否为群成员增加通知
                if noticetype == "group_increase":
                    # 只对配置列表中的群组ID作出反应
                    group_id = data.get("group_id", None)
                    if group_id in GROUP_IDS.JOINCHAT_GROUP_IDS:
                        # 处理群成员加入事件
                        await handle_join_event(user_id, group_id, websocket)
                if sub_type == "poke":
                    target_id = data.get("target_id", None)
                    print(f"摸摸头~ {sub_type}, 群号: {group_id}, 用户ID: {user_id}, 目标: {target_id}")
                    if target_id == self_id:
                        await handle_poke_neko(group_id, user_id,target_id, websocket)

        except Exception as e:
            error_msg = truncate_error_message(str(e))
            print(f"处理消息时出错: {error_msg}")
            traceback.print_exc()
            # 如果是消息类型，发送错误响应
            if "post_type" in data and data["post_type"] == "message":
                user_id = data.get("user_id")
                group_id = data.get("group_id", None)
                await send_message(websocket, f"处理消息时出错: {e}", user_id, group_id)

async def on_connect(websocket, path):
    print("连接建立")
    try:
        await handle_message(websocket)
    except Exception as e:
        print(f"处理消息时出错: {e}")
    finally:
        print("连接断开")


# 启动服务器
async def main():
    # 初始化数据文件
    FileUtils.initialize_data_files()
    
    start_server = await websockets.serve(on_connect, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print("WebSocket 服务器已启动")
    print(f"运行在ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/ws")
    await start_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())