import json
from modules.chikari_yinpa.handles import yinpa_Handles

# 初始化银趴处理类
yinpa_handler = yinpa_Handles()


async def handle_yinpa_command(message_text: str, user_id: str, group_id: str, message_type: str, websocket):
    """处理银趴命令 - NapCat版本"""
    args = {
        "user_id": user_id,
        "group_id": group_id,
        "message": message_text,
        "message_type": message_type
    }

    # 根据命令类型调用相应的处理函数
    if message_text.startswith("yinpa_control") or message_text.startswith("银趴控制"):
        await yinpa_handler.module_enable(websocket, args)
    elif message_text.startswith("yinpa_test"):
        await yinpa_handler.test(websocket, args)
    elif message_text.startswith("sign_in") or message_text.startswith("签到") or message_text.startswith("打卡"):
        await yinpa_handler.sign_in(websocket, args)
    elif message_text.startswith("info") or message_text.startswith("信息") or message_text.startswith("查询"):
        await yinpa_handler.yinpa_info(websocket, args)
    elif message_text.startswith("yinpa_help") or message_text.startswith("银趴帮助"):
        await yinpa_handler.yinpa_help(websocket, args)
    elif message_text.startswith("yinpa_join") or message_text.startswith("加入银趴"):
        await yinpa_handler.yinpa_join(websocket, args)
    elif message_text.startswith("yinpa_leave") or message_text.startswith("离开银趴"):
        await yinpa_handler.yinpa_leave(websocket, args)
    elif message_text.startswith("tou") or message_text.startswith("透") or message_text.startswith("插入"):
        await yinpa_handler.yinpa_tou(websocket, args)
    elif message_text.startswith("zha") or message_text.startswith("榨") or message_text.startswith("榨精"):
        await yinpa_handler.yinpa_zha(websocket, args)
    elif message_text.startswith("chong") or message_text.startswith("冲") or message_text.startswith("打胶") or message_text.startswith(
            "手冲") or message_text.startswith("撸") or message_text.startswith("导"):
        await yinpa_handler.yinpa_chong(websocket, args)
    elif message_text.startswith("kou") or message_text.startswith("扣") or message_text.startswith("扣扣") or message_text.startswith(
            "自慰") or message_text.startswith("紫薇"):
        await yinpa_handler.yinpa_kou(websocket, args)
    elif message_text.startswith("shop") or message_text.startswith("商店") or message_text.startswith("买") or message_text.startswith(
            "买东西") or message_text.startswith("店"):
        await yinpa_handler.yinpa_shop(websocket, args)
    elif message_text.startswith("work") or message_text.startswith("工作") or message_text.startswith("打工"):
        await yinpa_handler.yinpa_work(websocket, args)
    elif message_text.startswith("pay") or message_text.startswith("打钱") or message_text.startswith("v "):
        await yinpa_handler.yinpa_pay(websocket, args)
    else:
        # 默认响应，显示帮助信息
        await yinpa_handler.yinpa_help(websocket, args)