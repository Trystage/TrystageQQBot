from config import SUPER_USER, POKE_SU_ANS, POKE_ANS
from utils.misc_utils import dice
from utils.websocket_utils import send_message

async def handle_poke_neko(group_id, user_id, target_id, websocket):
    if user_id in SUPER_USER:
        await send_message(websocket, POKE_SU_ANS[dice(len(POKE_SU_ANS) - 1,  114514^114514)], user_id, group_id)
    else:
        await send_message(websocket, POKE_ANS[dice(len(POKE_ANS) - 1,  114514^114514)], user_id, group_id)