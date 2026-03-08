from ctypes import pythonapi

from attr import attributes

from utils.websocket_utils import send_message, get_user_nickname, get_image, require_group_admin_ws, get_at, \
    require_master_ws
import time
from hashlib import md5
from math import sqrt

from .data_handles import data,configdata,DHandles
from .yinpa_config import Config
from .utils import Utils
from .dicts import dicts

plugin_config = Config

class yinpa_Handles():
    """消息处理
    """

    @staticmethod
    @require_group_admin_ws
    async def module_enable(websocket, args):
        """处理银趴的开关
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")
        if "enable" in message and not Utils.group_enable_check(group_id):
            DHandles.configdata_set("yinpa_enabled_group",configdata["yinpa_enabled_group"] + [group_id])
            await send_message(websocket, "本群银趴已开启", user_id, group_id)
        elif "disable" in message and Utils.group_enable_check(group_id):
            DHandles.group_remove(group_id)
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
        else:
            await send_message(websocket,"错误：参数错误！\n命令：yinpa_control <enable/disable>", user_id, group_id)
    
    @staticmethod
    async def sign_in(websocket, args):
        """处理签到
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")
        
        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        if not Utils.yinpa_user_presence_check(user_id):
            await send_message(websocket,"您还未加入银趴！\ntips：请使用 yinpa_join 或 加入银趴", user_id, group_id)
            return
        uid: str = user_id
        if data[uid]["last_sign_in_time"] < (int)(time.time() / 86400):
            DHandles.data_set(uid,"last_sign_in_time",(int)(time.time() / 86400))
            d_pl = Utils.dice(100,(int)(data[uid]['penis_length']) ^ 1)
            d_vd = Utils.dice(100,(int)(data[uid]['vagina_depth']) ^ 2)
            d_m = Utils.dice(100,(int)(data[uid]['money']) ^ 3)
            await send_message(websocket,f"{data[uid]['name']}签到成功\n长度增加：{data[uid]['penis_length']} + (1d100 / 100) = {data[uid]['penis_length']} + ({d_pl} / 100) = {round(data[uid]['penis_length'] + d_pl / 100,2)}\n深度增加：{data[uid]['vagina_depth']} + (1d100 / 100) = {data[uid]['vagina_depth']} + ({d_vd} / 100) = {round(data[uid]['vagina_depth'] + d_vd / 100,2)}\n金钱增加：{data[uid]['money']} + 1d100 = {data[uid]['money']} + {d_m} = {data[uid]['money'] + d_m}\nps：签到于早上8点刷新", user_id, group_id)
            DHandles.data_set(uid,'penis_length',round(data[uid]['penis_length'] + d_pl / 100,2))
            DHandles.data_set(uid,'vagina_depth',round(data[uid]['vagina_depth'] + d_vd / 100,2))
            DHandles.data_set(uid,'money',data[uid]['money'] + d_m)
        else:
            await send_message(websocket,"你今天已经打过卡了呢~\nps：签到于早上8点刷新，别问我为什么", user_id, group_id)

    @staticmethod
    async def yinpa_join(websocket, args):
        """处理加入银趴
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")
        
        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用，你不准参加银趴！", user_id, group_id)
            return
        if Utils.yinpa_user_presence_check(user_id):
            await send_message(websocket,"您已加入银趴！\n如果想要重置银趴数据，请使用 leave_yinpa 或 离开银趴 后再加入", user_id, group_id)
            return
        uid: str = user_id
        command: str = message.split(' ', 1)[1] if ' ' in message else None
        if command is not None:
            arg_list: list = command.split()
        else:
            arg_list: list = []
        if not len(arg_list) >= 1:
            name: str = await get_user_nickname(websocket, user_id)
        else:
            name: str = arg_list[0]
        if len(arg_list) <= 1:
            species: int = Utils.dice(7,user_id)
        else:
            if not arg_list[1].isdigit():
                await send_message(websocket,"参数错误！\n种族应为一个正整数（种族编号）\n种族列表参照： yinpa_help 种族 ", user_id, group_id)
                return
            species: int = (int)(arg_list[1])
        if not dicts.species_dict.get(species):
            await send_message(websocket,"参数错误！\n不存在指定的种族\n种族列表参照： yinpa_help 种族 ", user_id, group_id)
            return
        if Utils.find_user_name(name):
            await send_message(websocket,f"已经有人使用这个昵称了！{Utils.find_user_name(name)}", user_id, group_id)
            return
        DHandles.user_add(uid,{
            'name':name,
            'species':species,
            'sex_value':plugin_config.chikari_yinpa_initial_sex_value,
            'penis_length':plugin_config.chikari_yinpa_initial_penis_length,
            'vagina_depth':plugin_config.chikari_yinpa_initial_vagina_depth,
            'strength':dicts.species_initial_ability[species][0][0] + Utils.dice(dicts.species_initial_ability[species][0][1],species ^ 4),
            'constitution':dicts.species_initial_ability[species][1][0] + Utils.dice(dicts.species_initial_ability[species][1][1],species ^ 5),
            'technique':dicts.species_initial_ability[species][2][0] + Utils.dice(dicts.species_initial_ability[species][2][1],species ^ 6),
            'volition':dicts.species_initial_ability[species][3][0] + Utils.dice(dicts.species_initial_ability[species][3][1],species ^ 7),
            'intelligence':dicts.species_initial_ability[species][4][0] + Utils.dice(dicts.species_initial_ability[species][4][1],species ^ 8),
            'charm':dicts.species_initial_ability[species][5][0] + Utils.dice(dicts.species_initial_ability[species][5][1],species ^ 9),
            'money':plugin_config.chikari_yinpa_initial_money,
            'state':[],
            "passive_times":0,
            "active_times":0,
            "last_sign_in_time":0,
            "last_operation_time":0,
            "last_refresh_time": time.time(),
            "next_work_time":0,
        })
        skill = []
        for i in dicts.species_initial_ability[species][6]:
            skill.append([i,0,1])
        DHandles.data_set(uid,"skill",skill)
        obj = md5("Chikari`s salt".encode("utf-8"))
        obj.update(f"{uid}".encode("utf-8"))
        DHandles.data_set(uid,"md5",obj.hexdigest())
        await send_message(websocket,"成功加入银趴！", user_id, group_id)
        await send_message(websocket,get_image(Utils.get_user_info_image(uid)), user_id, group_id)

    @staticmethod
    async def yinpa_leave(websocket, args):
        """处理离开银趴
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")
        
        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        if not Utils.yinpa_user_presence_check(user_id):
            await send_message(websocket,"您还未加入银趴！\n请使用 join_yinpa 或 加入银趴", user_id, group_id)
            return
        uid: str=user_id
        command: str = message.split(' ', 1)[1] if ' ' in message else None
        if not command or not data[uid]["md5"] or command != data[uid]["md5"]:
            obj = md5("Chikari`s salt".encode("utf-8"))
            obj.update(f"{uid}".encode("utf-8"))
            DHandles.data_set(uid,"md5",obj.hexdigest())
            await send_message(websocket,f"警告：这将清除你的所有银趴数据！\n请输入 yinpa_leave {obj.hexdigest()} 以完成操作", user_id, group_id)
        else:
            name = data[uid]['name']
            DHandles.user_remove(uid)
            await send_message(websocket,f"离开银趴成功。\n大家会记住你的，{name}", user_id, group_id)

    @staticmethod
    async def yinpa_help(websocket, args):
        """处理银趴帮助
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        command = message.split(' ', 1)[1] if ' ' in message else None
        if command is not None:
            help_key = command.split()
        else:
            help_key = []
        if not help_key:
            await send_message(websocket,get_image(Utils.text_to_image(dicts.yinpa_help_dict[""])), user_id, group_id)
            return
        if dicts.help_aliases.get(help_key[0]):
            help_key[0] = dicts.help_aliases[help_key[0]]
        if help_key[0] == "all":
            await send_message(websocket,get_image(Utils.text_to_image("可用帮助：\n" + "\n".join(list(dicts.yinpa_help_dict.keys())))), user_id, group_id)
            return
        elif help_key[0] == 'species':
            if len(help_key) >= 2 and dicts.species_help.get(help_key[1]):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.species_help[help_key[1]])), user_id, group_id)
            elif len(help_key) >= 2 and dicts.species_dict.get(int(help_key[1])):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.species_help[dicts.species_dict[int(help_key[1])]])), user_id, group_id)
            else:
                str = ""
                for i in list(dicts.species_dict.keys()):
                    str += f"{i}：{dicts.species_dict[i]}\n"
                await send_message(websocket,"错误：该种族不存在\n可用种族：\n" + str + "\n输入yinpa_help species [种族名或种族ID] 以查看种族描述", user_id, group_id)
                return
        elif help_key[0] == "skill":
            if len(help_key) >= 2 and dicts.skill_help.get(help_key[1]):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.skill_help[help_key[1]])), user_id, group_id)
            elif len(help_key) >= 2 and dicts.skill_dict.get(int(help_key[1])):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.skill_help[dicts.skill_dict[int(help_key[1])]])), user_id, group_id)
            else:
                str = ""
                for i in list(dicts.skill_dict.keys()):
                    str += f"{i}：{dicts.skill_dict[i]}\n"
                await send_message(websocket,"错误：该技能不存在\n可用技能：\n" + str + "\n输入yinpa_help skill [技能名或技能ID] 以查看技能描述", user_id, group_id)
                return
        elif help_key[0] == 'state':
            if len(help_key) >= 2 and dicts.state_help.get(help_key[1]):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.state_help[help_key[1]])), user_id, group_id)
            elif len(help_key) >= 2 and dicts.state_dict.get(int(help_key[1])):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.state_help[dicts.state_dict[int(help_key[1])]])), user_id, group_id)
            else:
                str = ""
                for i in list(dicts.state_dict.keys()):
                    str += f"{i}：{dicts.state_dict[i]}\n"
                await send_message(websocket,"错误：该状态不存在\n可用状态：\n" + str + "\n输入yinpa_help state [状态名或状态ID] 以查看状态描述", user_id, group_id)
                return
        elif help_key[0] == "shop":
            if len(help_key) >= 2 and dicts.shop_help.get(help_key[1]):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.shop_help[help_key[1]])), user_id, group_id)
            elif len(help_key) >= 2 and dicts.shop_dict.get(int(help_key[1])):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.shop_help[dicts.shop_dict[int(help_key[1])]])), user_id, group_id)
            else:
                str = ""
                for i in list(dicts.shop_dict.keys()):
                    str += f"{i}：{dicts.shop_dict[i]} 售价：{dicts.shop_price_dict[i]}\n"
                await send_message(websocket,get_image(Utils.text_to_image("错误：该商品不存在\n可用商品：\n" + str + "\n输入yinpa_help shop [商品名或商品ID] 以查看商品描述")), user_id, group_id)
                return
        elif help_key[0] == "work":
            if len(help_key) >= 2 and dicts.work_dict.get(help_key[1]):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.work_help_dict[help_key[1]])), user_id, group_id)
            elif len(help_key) >= 2 and dicts.work_dict.get(int(help_key[1])):
                await send_message(websocket,get_image(Utils.text_to_image(dicts.work_help_dict[dicts.work_dict[int(help_key[1])]])), user_id, group_id)
            else:
                str = ""
                for i in list(dicts.work_dict.keys()):
                    str += f"{i}：{dicts.work_dict[i]}\n"
                await send_message(websocket,"错误：该工作不存在\n可用工作：\n" + str + "\n输入yinpa_help work [工作名或工作ID] 以查看工作描述", user_id, group_id)
                return
        elif dicts.yinpa_help_dict.get(help_key[0]):
            await send_message(websocket,get_image(Utils.text_to_image(dicts.yinpa_help_dict[help_key[0]])), user_id, group_id)
        elif help_key[0] == "attr":
            str = "\n".join([f"{k}: {v}" for k, v in dicts.attribute_dict.items()])
            await send_message(websocket,get_image(Utils.text_to_image(str)),user_id, group_id)
        else:
            await send_message(websocket,get_image(Utils.text_to_image("错误：不存在对应的帮助\n可用帮助：\n" + "\n".join(list(dicts.yinpa_help_dict.keys())))), user_id, group_id)
            return

    @staticmethod
    async def yinpa_info(websocket, args):
        """处理查询信息
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        at:list = get_at(message)
        if not at:
            arg_list = message.split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = [f_uid]
                        break
                if not f_uid:
                    await send_message(websocket,"错误：未找到目标！", user_id, group_id)
                    return
        else:
            at = [at[0]]
        uid: str = user_id
        if not at or at == ['all']:
            if not data.get(uid):
                await send_message(websocket,"错误：你还没加入银趴！", user_id, group_id)
                return
            await send_message(websocket,get_image(Utils.get_user_info_image(uid)), user_id, group_id)
        else:
            at = at[0]
            if not data.get(at):
                await send_message(websocket,"错误：目标还没加入银趴！", user_id, group_id)
                return
            await send_message(websocket,get_image(Utils.get_user_info_image(at)), user_id, group_id)

    @staticmethod
    async def yinpa_tou(websocket, args):
        """处理透人
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        at:list = get_at(message)
        if not at:
            arg_list = message.split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = f_uid
                        break
                if not f_uid:
                    await send_message(websocket,"错误：未找到目标！", user_id, group_id)
                    return
            else:
                await send_message(websocket,"错误：未指定目标！", user_id, group_id)
                return
        elif at == ['all']:
            await send_message(websocket,"错误：未指定目标！", user_id, group_id)
            return
        else:
            at = at[0]
        uid: str = user_id
        if not Utils.yinpa_user_presence_check(uid):
            await send_message(websocket,"您还未加入银趴！\ntips：请使用 yinpa_join 或 加入银趴", user_id, group_id)
            return
        if not Utils.yinpa_user_presence_check(at):
            await send_message(websocket,"对方还未加入银趴！", user_id, group_id)
            return
        if uid == at:
            await send_message(websocket,"你想透自己？请使用 冲 或 扣", user_id, group_id)
            return
        Utils.refresh_data(uid)
        Utils.refresh_data(at)
        oc = Utils.operation_check(uid)
        if oc:
            await send_message(websocket,f"错误：操作失败！\n原因：{oc}", user_id, group_id)
            return
        if Utils.get_state(at,2):
            await send_message(websocket,f"错误：操作失败！\n原因：hentai! 连昏迷的{data[at]['name']}都不放过!", user_id, group_id)
            return
        pl = (int)(data[uid]['penis_length']) * 4
        if pl >= 80:
            pl = 80 + sqrt(pl - 80)
        atk_u = Utils.get_attack_list(uid,at) + [[pl,f"{data[uid]['name']}：长度",False]]
        str_u = f"{data[at]['name']}受到的伤害：1d50"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_u += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - 1d{-int(i[0])}（{i[1]}）"
        res_u = Utils.dice(50,uid)
        str_u += f" = {res_u}"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}"
                    res_u += int(i[0])
                elif i[0] < 0:
                    str_u += f" - {int(i[0])}"
                    res_u -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(uid) ^ int(i[0]) ^ 101)
                    str_u += f" + {d}"
                    res_u += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(uid) ^ int(i[0]) ^ 102)
                    str_u += f" - {d}"
                    res_u -= d
        str_u += f" = {res_u}\n"
        if res_u <= 0:
            res_u = 0
            str_u += " = 0"
        vd = (int)(data[at]['vagina_depth']) * 4
        if vd >= 80:
            vd = 80 + sqrt(vd - 80)
        atk_t = Utils.get_attack_list(at,uid) + [[vd,f"{data[at]['name']}：深度",False]]
        str_t = f"{data[uid]['name']}受到的伤害：1d50"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_t += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - 1d{-int(i[0])}（{i[1]}）"
        res_t = Utils.dice(50,at)
        str_t += f" = {res_t}"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}"
                    res_t += int(i[0])
                elif i[0] < 0:
                    str_t += f" - {int(i[0])}"
                    res_t -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(at) ^ int(i[0]) ^ 103)
                    str_t += f" + {d}"
                    res_t += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(at) ^ int(i[0]) ^ 104)
                    str_t += f" - {d}"
                    res_t -= d
        str_t += f" = {res_t}"
        if res_t <= 0:
            res_t = 0
            str_t += " = 0"
        hp_u = Utils.get_value(uid,"hp")
        hp_t = Utils.get_value(at,"hp")
        hp_str = f"HP： {hp_u[0]} → {hp_u[0] - res_t} "
        if hp_u[1]:
            hp_str += "（体质）"
        hp_str += f" | {hp_t[0]} → {hp_t[0] - res_u} "
        if hp_t[1]:
            hp_str += "（体质）"
        rh_str_u = Utils.reduce_hp(uid,res_t)
        rh_str_t = Utils.reduce_hp(at,res_u)
        DHandles.data_set(uid,"active_times",data[uid]["active_times"] + 1)
        DHandles.data_set(at,"passive_times",data[at]["passive_times"] + 1)
        await send_message(websocket, get_image(Utils.text_to_image(f"{data[uid]['name']}透了{data[at]['name']}\n" + str_t + "\n" + str_u + hp_str +  rh_str_u +  rh_str_t)), user_id, group_id)
        
    @staticmethod
    async def yinpa_zha(websocket, args):
        """处理榨人
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        at:list = get_at(message)
        if not at:
            arg_list = message.split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = f_uid
                        break
                if not f_uid:
                    await send_message(websocket,"错误：未找到目标！", user_id, group_id)
                    return
            else:
                await send_message(websocket,"错误：未指定目标！", user_id, group_id)
                return
        elif at == ['all']:
            await send_message(websocket,"错误：未指定目标！", user_id, group_id)
            return
        else:
            at = at[0]
        uid: str = user_id
        if not Utils.yinpa_user_presence_check(uid):
            await send_message(websocket,"您还未加入银趴！\ntips：请使用 yinpa_join 或 加入银趴", user_id, group_id)
            return
        if not Utils.yinpa_user_presence_check(at):
            await send_message(websocket,"对方还未加入银趴！", user_id, group_id)
            return
        if uid == at:
            await send_message(websocket,"想榨自己？请使用 冲 或 扣", user_id, group_id)
            return
        oc = Utils.operation_check(uid)
        Utils.refresh_data(uid)
        Utils.refresh_data(at)
        if oc:
            await send_message(websocket,f"错误：操作失败！\n原因：{oc}", user_id, group_id)
            return
        if Utils.get_state(at,2):
            await send_message(websocket,f"错误：操作失败！\n原因：hentai!连昏迷的{data[at]['name']}都不放过吗!", user_id, group_id)
            return
        vd = (int)(data[uid]['vagina_depth']) * 4
        if vd >= 80:
            vd = 80 + sqrt(vd - 80)
        atk_u = Utils.get_attack_list(uid,at) + [[vd,f"{data[uid]['name']}：深度",False]]
        str_u = f"{data[at]['name']}受到的伤害：1d50"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_u += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - 1d{-int(i[0])}（{i[1]}）"
        res_u = Utils.dice(50,uid)
        str_u += f" = {res_u}"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}"
                    res_u += int(i[0])
                elif i[0] < 0:
                    str_u += f" - {int(i[0])}"
                    res_u -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(uid) ^ int(i[0]) ^ 101)
                    str_u += f" + {d}"
                    res_u += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(uid) ^ int(i[0]) ^ 102)
                    str_u += f" - {d}"
                    res_u -= d
        str_u += f" = {res_u}\n"
        if res_u <= 0:
            res_u = 0
            str_u += " = 0"
        pl = (int)(data[at]['penis_length']) * 4
        if pl >= 80:
            pl = 80 + sqrt(pl - 80)
        atk_t = Utils.get_attack_list(at,uid) + [[pl,f"{data[at]['name']}：长度",False]]
        str_t = f"{data[uid]['name']}受到的伤害：1d50"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_t += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - 1d{-int(i[0])}（{i[1]}）"
        res_t = Utils.dice(50,at)
        str_t += f" = {res_t}"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}"
                    res_t += int(i[0])
                elif i[0] < 0:
                    str_t += f" - {int(i[0])}"
                    res_t -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(at) ^ int(i[0]) ^ 103)
                    str_t += f" + {d}"
                    res_t += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(at) ^ int(i[0]) ^ 104)
                    str_t += f" - {d}"
                    res_t -= d
        str_t += f" = {res_t}"
        if res_t <= 0:
            res_t = 0
            str_t += " = 0"
        hp_u = Utils.get_value(uid,"hp")
        hp_t = Utils.get_value(at,"hp")
        hp_str = f"HP： {hp_u[0]} → {hp_u[0] - res_t}"
        if hp_u[1]:
            hp_str += "（体质）"
        hp_str += f" | {hp_t[0]} → {hp_t[0] - res_u}"
        if hp_t[1]:
            hp_str += "（体质）"
        rh_str_u = Utils.reduce_hp(uid,res_t)
        rh_str_t = Utils.reduce_hp(at,res_u)
        DHandles.data_set(uid,"active_times",data[uid]["active_times"] + 1)
        DHandles.data_set(at,"passive_times",data[at]["passive_times"] + 1)
        await send_message(websocket,get_image(Utils.text_to_image(f"{data[uid]['name']}榨了{data[at]['name']}\n" + str_t  + "\n" + str_u + hp_str + rh_str_u + rh_str_t)), user_id, group_id)
        
    @staticmethod
    async def yinpa_chong(websocket, args):
        """处理冲
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        uid: str = user_id
        if not Utils.yinpa_user_presence_check(user_id):
            await send_message(websocket,"您还未加入银趴！\ntips：请使用 yinpa_join 或 加入银趴", user_id, group_id)
            return
        oc = Utils.operation_check(uid)
        if oc:
            await send_message(websocket,f"错误：操作失败！\n原因：{oc}", user_id, group_id)
            return
        Utils.refresh_data(uid)
        d = Utils.dice(100,uid)
        hp = Utils.get_value(uid,"hp")
        if Utils.get_state(uid, 4):
            pl_str = f"长度： {data[uid]['penis_length']} → {round(data[uid]['penis_length'] + d / 100 - 0.5, 2)} + {round(d / 100, 2)}"
            DHandles.data_set(uid, 'penis_length', round(data[uid]['penis_length'] + d / 100 - 0.5 + d / 100, 2))
        else:
            pl_str = f"长度： {data[uid]['penis_length']} → {round(data[uid]['penis_length'] + d / 100 - 0.5,2)}"
            DHandles.data_set(uid,'penis_length',round(data[uid]['penis_length'] + d / 100 - 0.5,2))
        hp_str = f"HP： {hp[0]} → {hp[0] - d}"
        rh_str = Utils.reduce_hp(uid,d)
        await send_message(websocket,f"{data[uid]['name']}冲了一发\n" + pl_str + "\n" + hp_str + rh_str, user_id, group_id)
        
    @staticmethod
    async def yinpa_kou(websocket, args):
        """处理扣
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        uid: str = user_id
        if not Utils.yinpa_user_presence_check(user_id):
            await send_message(websocket,"您还未加入银趴！\ntips：请使用 yinpa_join 或 加入银趴", user_id, group_id)
            return
        oc = Utils.operation_check(uid)
        if oc:
            await send_message(websocket,f"错误：操作失败！\n原因：{oc}", user_id, group_id)
            return
        Utils.refresh_data(uid)
        d = Utils.dice(40,uid)
        hp = Utils.get_value(uid,"hp")
        if Utils.get_state(uid, 4):
            vd_str = f"深度： {data[uid]['vagina_depth']} → {round(data[uid]['vagina_depth'] + d / 100,2)} + {round(d / 100, 2)}"
            DHandles.data_set(uid,'vagina_depth',round(data[uid]['vagina_depth'] + d / 100 + d / 100,2))
        else:
            vd_str = f"深度： {data[uid]['vagina_depth']} → {round(data[uid]['vagina_depth'] + d / 100,2)}"
            DHandles.data_set(uid,'vagina_depth',round(data[uid]['vagina_depth'] + d / 100,2))
        hp_str = f"HP： {hp[0]} → {hp[0] - d}"
        rh_str = Utils.reduce_hp(uid,d)
        await send_message(websocket,f"{data[uid]['name']}扣了一次\n" + vd_str + "\n" + hp_str + rh_str, user_id, group_id)

    @staticmethod
    async def yinpa_shop(websocket, args):
        """处理商店
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        uid = user_id
        command = message.split(' ', 1)[1] if ' ' in message else None
        if command is not None:
            shop_key = command.split()
        else:
            shop_key = []
        if not shop_key:
            str = ""
            for i in list(dicts.shop_dict.keys()):
                str += f"{i}：{dicts.shop_dict[i]} 售价：{dicts.shop_price_dict[i]}\n"
            await send_message(websocket,get_image(Utils.text_to_image("可用商品：\n" + str + "\n输入yinpa_help shop [商品名或商品ID] 以查看商品描述")), user_id, group_id)
            return
        else:
            goods = shop_key
            price = 0
            for i in goods:
                if not dicts.shop_dict.get(i) and not dicts.shop_help.get(i) and not dicts.shop_dict.get(int(i)):
                    str = ""
                    for j in list(dicts.shop_dict.keys()):
                        str += f"{j}：{dicts.shop_dict[j]} 售价：{dicts.shop_price_dict[j]}\n"
                    await send_message(websocket,get_image(Utils.text_to_image("错误：该商品不存在\n可用商品：\n" + str + "\n输入yinpa_help shop [商品名或商品ID] 以查看商品描述")), user_id, group_id)
                    return
                if i in list(dicts.shop_dict.values()):
                    i = (list(dicts.shop_dict.keys()))[(list(dicts.shop_dict.values())).index(i)]
                i = int(i)
                price += dicts.shop_price_dict[i]
            if data[uid]['money'] < price:
                await send_message(websocket,f"错误：你的金钱并不够买这些商品！\n这些商品的总售价：{price}\n你的金钱：{data[uid]['money']}", user_id, group_id)
                return
            DHandles.data_set(uid,'money',data[uid]['money'] - price)
            str = ""
            for i in goods:
                i = int(i)
                str += Utils.gain_item(uid,i)
            await send_message(websocket,get_image(Utils.text_to_image(str)), user_id, group_id)

    @staticmethod
    async def yinpa_work(websocket, args):
        """处理工作
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket,"本群银趴已禁用", user_id, group_id)
            return
        uid = user_id
        if not Utils.yinpa_user_presence_check(user_id):
            await send_message(websocket,"您还未加入银趴！\ntips：请使用 yinpa_join 或 加入银趴", user_id, group_id)
            return
        Utils.refresh_data(uid)
        command = message.split(' ', 1)[1] if ' ' in message else None
        if command is not None:
            work_key = command.split()
        else:
            work_key = []
        if not work_key:
            str = ""
            for i in list(dicts.work_dict.keys()):
                str += f"{i}：{dicts.work_dict[i]}\n"
            await send_message(websocket,"可用工作：\n" + str + "\n输入yinpa_help work [工作名或工作ID] 以查看工作描述", user_id, group_id)
            return
        work_key = work_key[0]
        if not dicts.work_dict.get(work_key) and not dicts.work_help_dict.get(work_key) and not dicts.work_dict.get(int(work_key)):
            str = ""
            for i in list(dicts.work_dict.keys()):
                str += f"{i}：{dicts.work_dict[i]}"
            await send_message(websocket,"错误：该工作不存在\n可用工作：\n" + str + "\n输入yinpa_help work [工作名或工作ID] 以查看工作描述", user_id, group_id)
            return
        oc = Utils.operation_check(uid)
        if oc:
            await send_message(websocket,f"错误：操作失败！\n原因：{oc}", user_id, group_id)
            return
        if data[uid]["next_work_time"] >= time.time():
            await send_message(websocket,"你现在正在工作冷却中！", user_id, group_id)
            return
        if work_key in list(dicts.work_dict.values()):
            work_key = (list(dicts.work_dict.keys()))[(list(dicts.work_dict.values())).index(work_key)]
        work_key = int(work_key)
        str = ""
        money = 0
        if work_key == 1:
            money += (Utils.get_value(uid,'strength')[0] + Utils.get_value(uid,'constitution')[0]) * Utils.dice(200,(Utils.get_value(uid,'strength')[0] + Utils.get_value(uid,'constitution')[0])) / 100
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
        elif work_key == 2:
            money += (Utils.get_value(uid,'technique')[0] * 0.7 + Utils.get_value(uid,'charm')[0] * 0.9) * Utils.dice(260,(Utils.get_value(uid,'technique')[0] + Utils.get_value(uid,'charm')[0])) / 100
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(100,Utils.get_value(uid,'volition')[0])
            str += f"意志检定：1d100 = {d} "
            if d >= Utils.get_value(uid,'volition')[0]:
                DHandles.data_set(uid,"hp_v",0)
                d = Utils.dice(10,(int)(uid) ^ 100)
                DHandles.state_refresh(uid,1,time.time() + d * 60)
                str += f" >= {data[uid]['volition']}\n{data[uid]['name']}失神了！失神状态将持续1d10 = {d}分钟。（期间无法行动，技能失效。如果失神期间受到攻击，失神状态将延长一分钟。）"
            else:
                str += f" < {data[uid]['volition']}\n"
        elif work_key == 3:
            money += (Utils.get_value(uid,'intelligence')[0] + Utils.get_value(uid,'charm')[0] - 60) * Utils.dice(200,(Utils.get_value(uid,'intelligence')[0] + Utils.get_value(uid,'charm')[0])) / 100
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(100,Utils.get_value(uid,'volition')[0])
            str += f"智力检定：1d100 = {d} "
            if d >= Utils.get_value(uid,'intelligence')[0]:
                str += f" >= {data[uid]['intelligence']}\n"
            else:
                money += 3 * d
                str += f" < {data[uid]['intelligence']}\n追加收益：{3 * d}\n"
        elif work_key == 4:
            money += (Utils.get_value(uid,'technique')[0] + Utils.get_value(uid,'intelligence')[0] - 100) * Utils.dice(300,(Utils.get_value(uid,'technique')[0] + Utils.get_value(uid,'intelligence')[0])) / 100
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
        elif work_key == 5:
            money += (Utils.get_value(uid,'strength')[0] * 0.9 + Utils.get_value(uid,'constitution')[0] * 0.8) * Utils.dice(200,(Utils.get_value(uid,'strength')[0] + Utils.get_value(uid,'constitution')[0])) / 120
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(100,Utils.get_value(uid,'constitution')[0])
            str += f"体质检定：1d100 = {d} "
            if d >= Utils.get_value(uid,'constitution')[0]:
                DHandles.data_set(uid,"hp_v",0)
                d = Utils.dice(10,(int)(uid) ^ 101)
                DHandles.state_refresh(uid,1,time.time() + d * 3600)
                str += f" >= {data[uid]['constitution']}\n{data[uid]['name']}昏迷了！失神状态将持续1d10 = {d}小时。（期间无法行动，无法被透，技能失效。）"
            else:
                str += f" < {data[uid]['constitution']}\n"
        elif work_key == 6:
            d = Utils.dice(100,(int)(uid) ^ 102)
            money += (d - 80) * 500
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(10,(int)(uid) ^ 103)
            if d == 1:
                d = Utils.dice(10,(int)(uid) ^ 104)
                if d >= 1 and d <= 1:
                    l = list(dicts.shop_dict.keys())
                    i = Utils.dice(len(l),(int)(uid) ^ 105)
                    str += Utils.gain_item(uid,l[i - 1])
                elif d >= 2 and d <= 4:
                    l = list(dicts.state_dict.keys())
                    i = Utils.dice(len(l),(int)(uid) ^ 106)
                    d = Utils.dice(86400,(int)(uid) ^ 107)
                    str += DHandles.state_refresh(uid,i,time.time() + d,level = 1,mode = 'add')
                elif d >= 5 and d <= 7:
                    i = Utils.dice(8,(int)(uid) ^ 108)
                    d = Utils.dice(100,(int)(uid) ^ 109) / 20
                    if i == 1:
                        i = 'strength'
                    elif i == 2:
                        i = 'constitution'
                    elif i == 3:
                        i = 'technique'
                    elif i == 4:
                        i = 'volition'
                    elif i == 5:
                        i = 'intelligence'
                    elif i == 6:
                        i = 'charm'
                    elif i == 7:
                        i = 'penis_length'
                    elif i == 8:
                        i = 'vagina_depth'
                    str += f"你的{dicts.attribute_dict[i]}： {data[uid][i]} → {data[uid][i] + d}\n"
                    DHandles.data_set(uid,i,(data[uid][i] + d))
                elif d >= 8 and d <= 10:
                    l = [10,11,12,13,14,15,]
                    i = Utils.dice(len(l),(int)(uid) ^ 106)
                    d = Utils.dice(86400,(int)(uid) ^ 107)
                    str += DHandles.skill_refresh(uid,l[i - 1],level = 1,mode = 'add')
        if work_key == 7:
            money += (Utils.get_value(uid,'strength')[0] + Utils.get_value(uid,'constitution')[0]) * Utils.dice(200,(Utils.get_value(uid,'strength')[0] + Utils.get_value(uid,'constitution')[0])) / 50
            if money < 0:
                money = 0
            str += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(100,Utils.get_value(uid,'constitution')[0])
            str += f"体质检定：1d100 = {d} "
            if d >= Utils.get_value(uid,'constitution')[0]:
                DHandles.data_set(uid,"hp_v",0)
                d = Utils.dice(10,(int)(uid) ^ 101)
                DHandles.state_refresh(uid,1,time.time() + d * 3600)
                str += f" >= {data[uid]['constitution']}\n{data[uid]['name']}昏迷了！失神状态将持续1d10 = {d}小时。（期间无法行动，无法被透，技能失效。）"
            else:
                str += f" < {data[uid]['constitution']}\n"
        DHandles.data_set(uid,"next_work_time",(time.time() + 3600))
        DHandles.data_set(uid,"money",data[uid]["money"] + money)
        str += "一小时内你将无法继续工作"
        await send_message(websocket,get_image(Utils.text_to_image(str)), user_id, group_id)
    @staticmethod
    async def yinpa_pay(websocket, args):
        """处理打钱
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if not Utils.group_enable_check(group_id):
            await send_message(websocket, "本群银趴已禁用", user_id, group_id)
            return
        at: list = get_at(message)
        arg_list = message.split()
        if not at:
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = f_uid
                        break
                if not f_uid:
                    await send_message(websocket, "错误：未找到目标！", user_id, group_id)
                    return
            else:
                await send_message(websocket, "错误：未指定目标！", user_id, group_id)
                return
        elif at == ['all']:
            await send_message(websocket, "错误：未指定目标！", user_id, group_id)
            return
        else:
            at = at[0]
        uid: str = user_id

        if not len(arg_list) == 3:
            await send_message(websocket, "错误：用法: pay <@某人 或 银趴昵称> <数量>", user_id, group_id)
            return

        amount = int(arg_list[2])

        if amount < 0:
            await send_message(websocket, "错误：不可以白嫖!", user_id, group_id)
            return
        elif amount == 0:
            await send_message(websocket, "错误：只有0元是什么嘛?!", user_id, group_id)
            return

        str = Utils.pay(uid, at, amount)
        await send_message(websocket, get_image(Utils.text_to_image(str)), user_id, group_id)
        return


    @staticmethod
    @require_group_admin_ws
    async def test(websocket, args):
        """测试用
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")
        
        uid = user_id
        DHandles.data_test_file_save()
        await send_message(websocket, "已发送至cache", user_id, group_id)

    @staticmethod
    @require_master_ws
    async def yinpa_set(websocket, args):
        """测试用
        """
        user_id = args.get("user_id")
        group_id = args.get("group_id")
        message = args.get("message", "")

        if len(message.split()) < 5:
            await send_message(websocket,"错误：yinpa_set <target> <type> <dict> <amount>", user_id, group_id)
            return

        at:list = get_at(message)
        if not at:
            arg_list = message.split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = f_uid
                        break
                if not f_uid:
                    await send_message(websocket,"错误：未找到目标！", user_id, group_id)
                    return
            else:
                await send_message(websocket,"错误：未指定目标！", user_id, group_id)
                return
        elif at == ['all']:
            await send_message(websocket,"错误：未指定目标！", user_id, group_id)
            return
        else:
            at = at[0]
        type = message.split()[2]
        dict = message.split()[3]
        amount = int(message.split()[4])

        if type == "attr":
            DHandles.data_set(at,dict,amount)
        elif type == "skill":
            DHandles.skill_refresh(at,dict,None,amount)
        elif type == "state":
            if len(message.split()) < 6:
                await send_message(websocket, "错误：state需要时长", user_id, group_id)
                return
            times = int(message.split()[5])
            DHandles.state_refresh(at,dict,time.time() + times, amount)
        else:
            await send_message(websocket,"错误：type can only be 'attr','skill','state'", user_id, group_id)
            return
        await send_message(websocket, "处理完成", user_id, group_id)


