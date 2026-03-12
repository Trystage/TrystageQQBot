import math
import os
import re
from random import randint, seed, sample, choice
from time import time, localtime
from PIL import Image, ImageDraw, ImageFont
from math import sqrt

from config import CACHE_DIR
from .data_handles import DHandles, load_old_data
from .dicts import dicts
from .yinpa_config import Config

plugin_config = Config()


class Utils:
    @staticmethod
    def group_enable_check(groupid: int):
        """检查群组是否在银趴列表中"""
        config = DHandles.load_config()
        return config.get("yinpa_enabled_group", []).count(groupid)

    @staticmethod
    def last_operation_time_check(uid: str):
        """检测上次行动时间是否已过"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return False
        minutes = int(time() / 60)
        return user_data.get("last_operation_time", 0) < minutes

    @staticmethod
    def set_last_operation_time(uid: str):
        """设置上次行动时间"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return
        user_data["last_operation_time"] = int(time() / 60)
        DHandles.save_user(uid, user_data)

    @staticmethod
    def dice(d: int, _seed):
        """骰子（保持原逻辑）"""
        seed(int(time()) ^ int(d) ^ int(_seed))
        return randint(1, int(d))

    @staticmethod
    def yinpa_user_presence_check(uid: str):
        """检查用户是否存在"""
        return DHandles.load_user(uid) is not None

    @staticmethod
    def text_to_image(text: str):
        """文字转图片（不变）"""
        os.makedirs(CACHE_DIR, exist_ok=True)
        fontSize = 20
        lines = text.split('\n')
        max_len = max(len(line) for line in lines)
        image = Image.new("RGB", (fontSize * max_len, len(lines) * (fontSize + 5)), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(plugin_config.chikari_yinpa_font, fontSize)
        draw.text((0, 0), text, font=font, fill="#000000")
        filepath = os.path.join(CACHE_DIR, "image.png")
        image.save(filepath, "PNG")
        return filepath

    @staticmethod
    def get_user_info_image(uid: str):
        """获取用户信息图（只读，无需保存）"""
        Utils.refresh_data(uid)  # refresh 内部会保存
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return Utils.text_to_image("用户不存在")
        skill_text = ""
        state_text = ""
        for i in user_data.get("skill", []):
            if i[0] == 6 and i[1] and i[1] >= time():
                skill_text += f"\n    ——{dicts.skill_dict[i[0]]}（等级：{i[2]}）（舰装损坏，{int(i[1] - time())}秒后修复）；"
            else:
                skill_text += f"\n    ——{dicts.skill_dict[i[0]]}（等级：{i[2]}）；"
        if not skill_text:
            skill_text = '无'
        for i in user_data.get("state", []):
            state_text += f"{dicts.state_dict[i[0]]}（等级：{i[2]}）（剩余时间：{int(i[1] - time())}秒）；"
        if not state_text:
            state_text = '无'
        text = f"    ID：{uid}\n" \
               f"    昵称：{user_data.get('name', '')}\n" \
               f"    种族：{dicts.species_dict.get(user_data.get('species', 0), '未知')}\n" \
               f"    意志HP：{user_data.get('hp_v', 0)}\n" \
               f"    体质HP：{user_data.get('hp_c', 0)}\n" \
               f"    长度：{user_data.get('penis_length', 0)}\n" \
               f"    深度：{user_data.get('vagina_depth', 0)}\n" \
               f"    力量：{user_data.get('strength', 0)}（当前：{Utils.get_value(uid, 'strength')[0]}）\n" \
               f"    体质：{user_data.get('constitution', 0)}（当前：{Utils.get_value(uid, 'constitution')[0]}）\n" \
               f"    技巧：{user_data.get('technique', 0)}（当前：{Utils.get_value(uid, 'technique')[0]}）\n" \
               f"    意志：{user_data.get('volition', 0)}（当前：{Utils.get_value(uid, 'volition')[0]}）\n" \
               f"    智力：{user_data.get('intelligence', 0)}\n" \
               f"    魅力：{user_data.get('charm', 0)}\n" \
               f"    金钱：{user_data.get('money', 0)}\n" \
               f"    技能：{skill_text}\n" \
               f"    状态：{state_text}\n" \
               f"    被动次数：{user_data.get('passive_times', 0)}\n" \
               f"    主动次数：{user_data.get('active_times', 0)}"
        return Utils.text_to_image(text)

    @staticmethod
    def refresh_data(uid: str):
        """更新用户数据（读取并修改后保存）"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return
        # 补全技能/状态长度
        for i in user_data.get("skill", []):
            if len(i) <= 2:
                # 需要调用 skill_refresh 来修正，但 skill_refresh 会保存，这里我们手动处理
                # 简单起见，可以直接调用 DHandles.skill_refresh，它会处理保存
                DHandles.skill_refresh(uid, i[0], i[1] if len(i) > 1 else None)
        for i in user_data.get("state", []):
            if len(i) <= 2:
                DHandles.state_refresh(uid, i[0], i[1] if len(i) > 1 else time())
        # 重新加载 user_data，因为 skill_refresh 可能修改了数据
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return

        new_state = []
        b = False  # 标记是否有昏迷状态（id=1）
        for i in user_data.get("state", []):
            if i[1] <= time():
                continue  # 过期状态直接丢弃
            new_state.append(i)
            if i[0] == 1:
                b = True  # 有昏迷状态
            elif i[0] == 2 and i[1] <= time():
                # 失神状态结束，恢复满HP
                DHandles.data_set(uid, 'hp_v', (Utils.get_value(uid, 'volition')[0] + 10) * 5)
                DHandles.data_set(uid, 'hp_c', (Utils.get_value(uid, 'constitution')[0] + 10) * 10)

        # 更新状态列表
        user_data["state"] = new_state

        # 计算HP恢复
        last_refresh = user_data.get("last_refresh_time", time())
        delta_min = int((time() - last_refresh) / 60)
        regen_rate = Utils.get_regeneration_rate(uid)

        if b:
            # 有昏迷状态，只恢复体质HP
            max_hp_c = (Utils.get_value(uid, 'constitution')[0] + 10) * 10
            user_data["hp_c"] = min(user_data.get("hp_c", 0) + delta_min * regen_rate, max_hp_c)
        else:
            # 无昏迷状态，恢复意志HP
            max_hp_v = (Utils.get_value(uid, 'volition')[0] + 10) * 5
            user_data["hp_v"] = min(user_data.get("hp_v", 0) + delta_min * regen_rate, max_hp_v)

        user_data["last_refresh_time"] = time()
        DHandles.save_user(uid, user_data)

    @staticmethod
    def get_skill(uid: str, id: int):
        """获取技能（只读）"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return []
        # 补全长度
        for i in user_data.get("skill", []):
            if len(i) <= 2:
                DHandles.skill_refresh(uid, i[0], i[1] if len(i) > 1 else None)
        # 重新加载
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return []
        for i in user_data.get("skill", []):
            if i[0] == id:
                # 检查是否被昏迷抑制
                if i[0] not in [9, 10, 11, 12, 13, 14, 15] and Utils.get_state(uid, 1):
                    return []
                return i
        return []

    @staticmethod
    def get_state(uid: str, id: int):
        """获取状态（只读）"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return []
        # 补全长度
        for i in user_data.get("state", []):
            if len(i) <= 2:
                DHandles.state_refresh(uid, i[0], i[1] if len(i) > 1 else time())
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return []
        for i in user_data.get("state", []):
            if i[0] == id:
                return i
        return []

    @staticmethod
    def is_night():
        """判断是否为晚上（不变）"""
        hour = localtime().tm_hour
        return hour < 6 or hour >= 18

    @staticmethod
    def boat(uid: str):
        """判断舰装是否生效（只读）"""
        s = Utils.get_skill(uid, 6)
        if s and (s[1] is None or s[1] <= time()):
            return s[2]
        return 0

    @staticmethod
    def vampire(uid: str):
        """判断吸血鬼技能加成（只读）"""
        s = Utils.get_skill(uid, 7)
        if s:
            if Utils.is_night():
                return 50 * sqrt(s[2])
            else:
                return -50 / sqrt(s[2])
        return 0

    @staticmethod
    def get_value(uid: str, key: str):
        """获取用户当前状态下的某一数值（只读）"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return [0, False]

        b = False
        if key == "hp":
            if Utils.get_state(uid, 1):
                b = True
                value = user_data.get('hp_c', 0)
            else:
                value = user_data.get('hp_v', 0)
        elif key == 'penis_length':
            value = user_data.get('penis_length', 0)
        elif key == 'vagina_depth':
            value = user_data.get('vagina_depth', 0)
        elif key == 'strength':
            value = user_data.get('strength', 0)
            boat_lv = Utils.boat(uid)
            if boat_lv:
                value += Utils.get_value(uid, 'intelligence')[0] * sqrt(boat_lv)
            value += Utils.vampire(uid)
        elif key == 'constitution':
            value = user_data.get('constitution', 0)
            boat_lv = Utils.boat(uid)
            if boat_lv:
                value += Utils.get_value(uid, 'intelligence')[0] * sqrt(boat_lv)
            value += Utils.vampire(uid)
        elif key == 'technique':
            value = user_data.get('technique', 0)
            value += Utils.vampire(uid)
            curse = Utils.get_skill(uid, 12)
            if curse and Utils.is_night():
                value += -20 * curse[2]
        elif key == 'volition':
            value = user_data.get('volition', 0)
            boat_lv = Utils.boat(uid)
            if boat_lv:
                value += Utils.get_value(uid, 'intelligence')[0] * sqrt(boat_lv)
            value += Utils.vampire(uid)
            curse = Utils.get_skill(uid, 12)
            if curse and Utils.is_night():
                value += -20 * curse[2]
        elif key == 'intelligence':
            value = user_data.get('intelligence', 0)
        elif key == 'charm':
            value = user_data.get('charm', 0)
        else:
            value = 0

        if value < 0:
            value = 0
        return [value, b]

    @staticmethod
    def get_attack_list(uid: str, target: str):
        """获取攻击列表（只读，需要两个用户数据）"""
        Utils.refresh_data(uid)
        Utils.refresh_data(target)
        user_data = DHandles.load_user(uid)
        target_data = DHandles.load_user(target)
        if user_data is None or target_data is None:
            return []

        atk = []
        # 攻击方加成
        atk.append([Utils.get_value(uid, 'technique')[0], f"{user_data['name']}：技巧", False])
        if s := Utils.get_skill(uid, 2):
            atk.append([30 * sqrt(s[2]), f"{user_data['name']}：猫化", False])
        if s := Utils.get_skill(uid, 3):
            atk.append([Utils.get_value(uid, 'intelligence')[0] / 2 * sqrt(s[2]), f"{user_data['name']}：自然之心", False])
        if s := Utils.get_skill(uid, 5):
            atk.append([80 * sqrt(s[2]), f"{user_data['name']}：淫纹", False])
        if s := Utils.get_state(uid, 3):
            atk.append([30 * sqrt(s[2]), f"{user_data['name']}：伟哥", False])
        if s := Utils.get_skill(uid, 11):
            atk.append([60 * s[2], f"{user_data['name']}：亡命疯徒", False])
        if s := Utils.get_skill(target, 11):
            atk.append([60 * s[2], f"{target_data['name']}：亡命疯徒", False])
        if s := Utils.get_skill(target, 14):
            atk.append([50 * s[2], f"{target_data['name']}：敏感", False])
        if s := Utils.get_skill(target, 15):
            if Utils.dice(100, s[2] * 15) <= s[2]:
                atk.append([1000, f"{target_data['name']}：弱点", True])

        # 防御方减伤
        if s := Utils.get_skill(target, 2):
            atk.append([-30 * sqrt(s[2]), f"{target_data['name']}：猫化", False])
        if s := Utils.get_skill(target, 3):
            atk.append([-Utils.get_value(target, 'intelligence')[0] / 2 * sqrt(s[2]), f"{target_data['name']}：自然之心", False])
        if s := Utils.get_skill(target, 4):
            atk.append([-80 * sqrt(s[2]), f"{target_data['name']}：圣体", False])
        if s := Utils.get_skill(uid, 10):
            atk.append([-50 * s[2], f"{user_data['name']}：呓语", False])
        if s := Utils.get_skill(target, 16):
            atk.append([-50 * sqrt(s[2]), f"{target_data['name']}：庇佑", False])
        return atk

    @staticmethod
    def reduce_hp(uid: str, hp: int):
        """减少hp并返回描述文本（修改并保存）"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return ""

        str_desc = ""
        if not Utils.get_state(uid, 1):
            # 无昏迷，减意志HP
            new_hp_v = Utils.get_value(uid, "hp")[0] - hp
            user_data["hp_v"] = int(new_hp_v)
            if user_data["hp_v"] <= 0:
                d = Utils.dice(100, int(uid) ^ 10)
                str_desc += f"\n{user_data['name']}高潮了！\n意志检定：1d100 = {d}"
                if d >= user_data.get('volition', 0):
                    user_data["hp_v"] = 0
                    d2 = Utils.dice(10, int(uid) ^ 11)
                    # 添加失神状态
                    DHandles.state_refresh(uid, 1, time() + d2 * 60)
                    str_desc += f" >= {user_data['volition']}\n{user_data['name']}失神了！失神状态将持续1d10 = {d2}分钟。（期间无法行动，技能失效。如果失神期间受到攻击，失神状态将延长一分钟。）"
                else:
                    d2 = Utils.dice(user_data['volition'], int(uid) ^ 12)
                    user_data["hp_v"] = (d2 + 10) * 5
                    str_desc += f" < {user_data['volition']}\n{user_data['name']}的意志HP回复至{user_data['hp_v']}"
        else:
            # 有昏迷，减体质HP
            new_hp_c = Utils.get_value(uid, "hp")[0] - hp
            user_data["hp_c"] = int(new_hp_c)
            # 延长失神时间
            state_1 = Utils.get_state(uid, 1)
            if state_1:
                DHandles.state_refresh(uid, 1, state_1[1] + 60)
            if user_data["hp_c"] <= 0:
                d = Utils.dice(100, int(uid) ^ 13)
                str_desc += f"\n{user_data['name']}高潮了！\n体质检定：1d100 = {d}"
                if d >= user_data.get('constitution', 0):
                    user_data["hp_c"] = 0
                    d2 = Utils.dice(5, int(uid) ^ 14)
                    DHandles.state_refresh(uid, 2, time() + d2 * 3600)
                    str_desc += f" >= {user_data['constitution']}\n{user_data['name']}昏迷了！昏迷状态将持续1d5 = {d2}小时。（期间无法行动，无法被透，技能失效。）"
                    if Utils.boat(uid):
                        DHandles.skill_refresh(uid, 6, time() + 259200)
                        str_desc += f"\n{user_data['name']}的舰装破损了！将进入三天的冷却。"
                else:
                    d2 = Utils.dice(user_data['constitution'], int(uid) ^ 15)
                    user_data["hp_c"] = (d2 + 10) * 5
                    str_desc += f" < {user_data['constitution']}\n{user_data['name']}的体质HP回复至{user_data['hp_c']}"

        DHandles.save_user(uid, user_data)
        return str_desc

    @staticmethod
    def operation_check(uid: str):
        """检测用户是否能够行动（只读）"""
        Utils.refresh_data(uid)
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return "用户不存在"
        oc = ""
        if not Utils.last_operation_time_check(uid):
            oc += "你操作太快了！"
        if Utils.get_state(uid, 1) and not Utils.get_skill(uid, 9):
            oc += "你失神了！"
        if Utils.get_state(uid, 2):
            oc += "你昏迷了！"
        if not oc:
            Utils.set_last_operation_time(uid)
        return oc

    @staticmethod
    def find_user_name(name: str):
        """从昵称查找用户id"""
        for uid in DHandles.get_all_uids():
            user_data = DHandles.load_user(uid)
            if user_data and user_data.get('name') == name:
                return uid
        return None
    @staticmethod
    def get_regeneration_rate(uid: str):
        """获取hp自然恢复速度（只读）"""
        rate = 1
        if s := Utils.get_skill(uid, 8):
            rate += 5 * s[2]
        if s := Utils.get_skill(uid, 13):
            rate += -5 * s[2]
        if rate < 0:
            rate = 0
        return rate

    @staticmethod
    def gain_item(uid: str, id: int):
        """用户获得物品（修改并保存）"""
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return "用户不存在"

        result = f"你获得了物品：{dicts.shop_dict[id]}\n"
        if id == 1:
            result += DHandles.state_refresh(uid, 3, time() + 3600, level=1, mode='add')
        elif id == 2:
            user_data['penis_length'] = user_data.get('penis_length', 0) + 2
            user_data['vagina_depth'] = user_data.get('vagina_depth', 0) + 2
            result += "长度增加了2cm，深度增加了2cm\n"
        elif id == 3:
            hp = Utils.get_value(uid, "hp")
            if hp[1]:
                user_data["hp_c"] = user_data.get("hp_c", 0) + 100
                result += "体质HP增加了100\n"
            else:
                user_data["hp_v"] = user_data.get("hp_v", 0) + 100
                result += "意志HP增加了100\n"
            if Utils.get_state(uid, 2):
                DHandles.state_refresh(uid, 2, time())
                result += "已清理昏迷效果\n"
        elif id == 4:
            result += DHandles.skill_refresh(uid, 2, level=1, mode='add')
        elif id == 5:
            result += DHandles.skill_refresh(uid, 3, level=1, mode='add')
        elif id == 6:
            result += DHandles.skill_refresh(uid, 4, level=1, mode='add')
        elif id == 7:
            result += DHandles.skill_refresh(uid, 5, level=1, mode='add')
        elif id == 8:
            result += DHandles.skill_refresh(uid, 6, level=1, mode='add')
        elif id == 9:
            result += DHandles.skill_refresh(uid, 7, level=1, mode='add')
        elif id == 10:
            result += DHandles.skill_refresh(uid, 8, level=1, mode='add')
        elif id == 11:
            result += DHandles.skill_refresh(uid, 9, level=1, mode='add')
        elif id == 12:
            for i in [10, 11, 12, 13, 14, 15]:
                DHandles.skill_refresh(uid, i, level=0)
            result += "已清除所有诅咒"
        elif id == 13:
            # 需要用户数据中的 skill
            skills = user_data.get("skill", [])
            curse_samples = sample([[10, None, 0], [11, None, 0], [12, None, 0], [13, None, 0], [14, None, 0], [15, None, 0]], 5)
            combined = skills + curse_samples
            sk = choice(combined)
            base_level = sk[2] if sk[2] > 0 else 1
            total = sum(i[2] for i in combined)
            compressed = int(math.log(total + 1, 10) * 10)
            new_level = base_level + compressed * sqrt(base_level)
            # 直接调用 skill_refresh 会保存
            result += DHandles.skill_refresh(uid, sk[0], level=int(new_level))
        elif id == 14:
            d = Utils.dice(10, 13)
            result += f"1d10 = {d}"
            if d == 1:
                d = Utils.dice(10, 131)
                user_data['penis_length'] += d * 0.1
                result += f"\n1d10 = {d}\n长度增加 {d*0.1}，当前 {user_data['penis_length']}"
            elif d == 2:
                d = Utils.dice(10, 132)
                user_data['vagina_depth'] += d * 0.1
                result += f"\n1d10 = {d}\n深度增加 {d*0.1}，当前 {user_data['vagina_depth']}"
            elif d == 3:
                d = Utils.dice(10, 133)
                user_data['strength'] += d
                result += f"\n1d10 = {d}\n力量增加 {d}，当前 {user_data['strength']}"
            elif d == 4:
                d = Utils.dice(10, 134)
                user_data['constitution'] += d
                result += f"\n1d10 = {d}\n体质增加 {d}，当前 {user_data['constitution']}"
            elif d == 5:
                d = Utils.dice(10, 135)
                user_data['technique'] += d
                result += f"\n1d10 = {d}\n技巧增加 {d}，当前 {user_data['technique']}"
            elif d == 6:
                d = Utils.dice(10, 136)
                user_data['volition'] += d
                result += f"\n1d10 = {d}\n意志增加 {d}，当前 {user_data['volition']}"
            elif d == 7:
                d = Utils.dice(10, 137)
                user_data['intelligence'] += d
                result += f"\n1d10 = {d}\n智力增加 {d}，当前 {user_data['intelligence']}"
            elif d == 8:
                d = Utils.dice(10, 138)
                user_data['charm'] += d
                result += f"\n1d10 = {d}\n魅力增加 {d}，当前 {user_data['charm']}"
            elif d == 9:
                d = Utils.dice(10, 139)
                user_data['money'] += d * 1000
                result += f"\n1d10 = {d}\n金钱增加 {d*1000}，当前 {user_data['money']}"
            elif d == 10:
                d2 = Utils.dice(2, 1310)
                si = 1 if d2 == 1 else -1
                result += f"\n1d2 = {d2}（{'大成功' if d2==1 else '大失败'}）"
                d3 = Utils.dice(9, 1311)
                if d3 == 1:
                    d4 = Utils.dice(100, 131)
                    user_data['penis_length'] += d4 * 0.1 * si
                    result += f"\n1d9 = 1，1d100 = {d4}\n长度变化 {d4*0.1*si}，当前 {user_data['penis_length']}"
                elif d3 == 2:
                    d4 = Utils.dice(100, 132)
                    user_data['vagina_depth'] += d4 * 0.1 * si
                    result += f"\n1d9 = 2，1d100 = {d4}\n深度变化 {d4*0.1*si}，当前 {user_data['vagina_depth']}"
                elif d3 == 3:
                    d4 = Utils.dice(100, 133)
                    user_data['strength'] += d4 * si
                    result += f"\n1d9 = 3，1d100 = {d4}\n力量变化 {d4*si}，当前 {user_data['strength']}"
                elif d3 == 4:
                    d4 = Utils.dice(100, 134)
                    user_data['constitution'] += d4 * si
                    result += f"\n1d9 = 4，1d100 = {d4}\n体质变化 {d4*si}，当前 {user_data['constitution']}"
                elif d3 == 5:
                    d4 = Utils.dice(100, 135)
                    user_data['technique'] += d4 * si
                    result += f"\n1d9 = 5，1d100 = {d4}\n技巧变化 {d4*si}，当前 {user_data['technique']}"
                elif d3 == 6:
                    d4 = Utils.dice(100, 136)
                    user_data['volition'] += d4 * si
                    result += f"\n1d9 = 6，1d100 = {d4}\n意志变化 {d4*si}，当前 {user_data['volition']}"
                elif d3 == 7:
                    d4 = Utils.dice(100, 137)
                    user_data['intelligence'] += d4 * si
                    result += f"\n1d9 = 7，1d100 = {d4}\n智力变化 {d4*si}，当前 {user_data['intelligence']}"
                elif d3 == 8:
                    d4 = Utils.dice(100, 138)
                    user_data['charm'] += d4 * si
                    result += f"\n1d9 = 8，1d100 = {d4}\n魅力变化 {d4*si}，当前 {user_data['charm']}"
                elif d3 == 9:
                    d4 = Utils.dice(100, 139)
                    user_data['money'] += d4 * 1000 * si
                    result += f"\n1d9 = 9，1d100 = {d4}\n金钱变化 {d4*1000*si}，当前 {user_data['money']}"
        elif id == 15:
            user_data['hp_v'] = 0
            DHandles.state_refresh(uid, 1, time() + 10 * 60)
            result += f"{user_data['name']}失神了！失神状态将持续10分钟。（期间无法行动，技能失效。如果失神期间受到攻击，失神状态将延长一分钟。）"
        elif id == 16:
            if not Utils.get_state(uid, 4):
                result += DHandles.state_refresh(uid, 4, time() + 60 * 60)
            else:
                state_4 = Utils.get_state(uid, 4)
                if state_4:
                    result += DHandles.state_refresh(uid, 4, state_4[1] + 60 * 60)
        elif id == 17:
            result += DHandles.skill_refresh(uid, 16, level=1, mode='add')

        # 保存修改（除了已经通过 DHandles 方法保存的，还有本地修改的）
        DHandles.save_user(uid, user_data)
        return result

    @staticmethod
    def pay(uid: str, target: str, amount: int):
        """支付接口（修改两个用户并保存）"""
        user_data = DHandles.load_user(uid)
        target_data = DHandles.load_user(target)
        if user_data is None or target_data is None:
            return "用户不存在"

        if user_data.get('money', 0) < amount * 1.1:  # amount + 0.1*amount
            return f"支付失败, 你的金钱:{user_data['money']} < 支付金额:{amount} + tax:{amount*0.1}"

        user_data['money'] -= int(amount * 1.1)
        target_data['money'] += amount

        DHandles.save_user(uid, user_data)
        DHandles.save_user(target, target_data)

        return f"失败是成功之母, 你是成功支付!~\n{user_data['name']} 金钱：{user_data['money'] + int(amount*1.1)} - {amount} - {amount*0.1} → {user_data['money']}\n{target_data['name']} 金钱：{target_data['money'] - amount} + {amount} → {target_data['money']}"

    @staticmethod
    def claim_newbie_reward(uid: str) -> str:
        """领取新手礼包（仅可领取一次）

        奖励规则：
        - 基础金币 +1000
        - 如果旧数据中存在该用户，则额外获得：
            * 金币增加 = √(旧金钱) 取整
            * 力量、体质、技巧、意志、智力、魅力 各增加 √(旧属性) 取整
            * 长度、深度 各增加 √(旧值) 取整（保留一位小数）
        - 如果旧数据中不存在，则仅获得基础金币。
        """
        # 1. 加载当前用户数据
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return f"❌ 用户 {uid} 不存在，请先注册或使用其他命令。"

        # 2. 检查是否已领取
        if user_data.get("newbie_reward_claimed", False):
            return "🎁 你已经领取过新手礼包啦，不能再领了哦~"

        # 3. 加载旧数据
        old_data = load_old_data()
        old_user = old_data.get(uid)

        # 4. 计算奖励
        base_gold = 1000
        extra_gold = 0
        attr_boosts = {
            "strength": 0,
            "constitution": 0,
            "technique": 0,
            "volition": 0,
            "intelligence": 0,
            "charm": 0,
            "penis_length": 0.0,
            "vagina_depth": 0.0,
        }

        if old_user:
            # 金钱奖励
            old_money = old_user.get("money", 0)
            extra_gold = int(math.isqrt(int(old_money))) if old_money >= 0 else 0  # sqrt取整

            # 属性奖励（取整）
            for attr in ["strength", "constitution", "technique", "volition", "intelligence", "charm"]:
                old_val = old_user.get(attr, 0)
                boost = int(math.isqrt(int(old_val))) if old_val >= 0 else 0
                attr_boosts[attr] = boost

            # 长度/深度（保留一位小数）
            for attr in ["penis_length", "vagina_depth"]:
                old_val = old_user.get(attr, 0.0)
                boost = round(math.sqrt(max(old_val, 0)), 1)
                attr_boosts[attr] = boost
        else:
            # 无旧数据，仅给基础金币
            pass

        # 5. 更新用户数据
        user_data["money"] = user_data.get("money", 0) + base_gold + extra_gold
        for attr, boost in attr_boosts.items():
            user_data[attr] = user_data.get(attr, 0) + boost

        user_data["newbie_reward_claimed"] = True

        # 6. 保存
        DHandles.save_user(uid, user_data)

        # 7. 生成描述文本
        desc = f"🎉 恭喜你领取新手礼包！\n"
        desc += f"💰 获得基础金币 {base_gold}"
        if extra_gold > 0:
            desc += f" + {extra_gold}（旧数据加成）"
        desc += f"，总计金币 +{base_gold + extra_gold}\n"

        boosted_attrs = [f"{attr} +{boost}" for attr, boost in attr_boosts.items() if boost > 0]
        if boosted_attrs:
            desc += "✨ 属性提升：" + "，".join(boosted_attrs) + "\n"
        else:
            desc += "✨ 属性未获得额外提升（旧数据中无对应属性）\n"

        desc += "🎁 记得常回来玩哦~"
        return desc