import sqlite3
import json
from pathlib import Path
from time import time

from config import DATA_DIR
from .dicts import dicts

# 原有文件路径
plugin_data_file: Path = DATA_DIR / "chikari_yinpa" / "data.json"
plugin_config_file: Path = DATA_DIR / "chikari_yinpa" / "config.json"

# 新的 SQLite 数据库路径
DB_PATH = DATA_DIR / "chikari_yinpa" / "user_data.db"
# 旧数据备份文件路径（请根据实际情况调整）
OLD_DATA_PATH = DATA_DIR / "chikari_yinpa" / "data_legacy.json"

# 缓存旧数据，避免重复读取
_old_data_cache = None

def load_old_data():
    global _old_data_cache
    if _old_data_cache is None:
        if OLD_DATA_PATH.exists():
            with open(OLD_DATA_PATH, 'r', encoding='utf-8') as f:
                _old_data_cache = json.load(f)
        else:
            _old_data_cache = {}
    return _old_data_cache

def init_db():
    """初始化数据库，创建 users 表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (uid TEXT PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

# 在模块加载时初始化数据库
init_db()


class DHandles:
    """数据处理（用户数据存 SQLite，配置存 JSON）"""

    # ---------- 私有数据库操作方法 ----------
    @staticmethod
    def _get_conn():
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def load_user(uid: str) -> dict:
        """从数据库加载用户数据，若不存在返回 None"""
        conn = DHandles._get_conn()
        c = conn.cursor()
        c.execute("SELECT data FROM users WHERE uid=?", (uid,))
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None

    @staticmethod
    def save_user(uid: str, user_data: dict):
        """将用户数据保存到数据库（覆盖）"""
        conn = DHandles._get_conn()
        c = conn.cursor()
        c.execute("REPLACE INTO users (uid, data) VALUES (?, ?)",
                  (uid, json.dumps(user_data, ensure_ascii=False)))
        conn.commit()
        conn.close()

    # ---------- 配置操作方法（仍用 JSON 文件）----------
    @staticmethod
    def load_config():
        """从文件加载配置，返回字典"""
        if not plugin_config_file.exists():
            return {"yinpa_enabled_group": []}
        with open(plugin_config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _save_config(config: dict):
        """将配置字典写入文件"""
        with open(plugin_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    # ---------- 原有方法改造 ----------
    @staticmethod
    def get_all_uids():
        """返回所有已注册用户的 uid 列表"""
        conn = DHandles._get_conn()
        c = conn.cursor()
        c.execute("SELECT uid FROM users")
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows]
    @staticmethod
    def data_set(uid: str, key: str, value):
        user_data = DHandles.load_user(uid)
        if user_data is None:
            user_data = {}
        user_data[key] = value
        DHandles.save_user(uid, user_data)

    @staticmethod
    def configdata_set(key: str, value):
        config = DHandles.load_config()
        config[key] = value
        DHandles._save_config(config)

    @staticmethod
    def group_remove(group_id: int):
        config = DHandles.load_config()
        if group_id in config.get("yinpa_enabled_group", []):
            config["yinpa_enabled_group"].remove(group_id)
            DHandles._save_config(config)

    @staticmethod
    def user_add(uid: str, init_dict: dict):
        # 计算初始 HP
        init_dict["hp_v"] = (init_dict.get("volition", 0) + 10) * 5
        init_dict["hp_c"] = (init_dict.get("constitution", 0) + 10) * 10
        DHandles.save_user(uid, init_dict)

    @staticmethod
    def user_remove(uid: str):
        conn = DHandles._get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE uid=?", (uid,))
        conn.commit()
        conn.close()

    @staticmethod
    def skill_refresh(uid: str, id: int, value=None, level: int = 1, mode: str = ''):
        strings = ''
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return f"用户 {uid} 不存在"

        # 确保 skill 字段存在
        if "skill" not in user_data:
            user_data["skill"] = []

        skills = user_data["skill"]
        found = False
        for i, sk in enumerate(skills):
            if sk[0] == id:
                if mode == 'add':
                    level += sk[2]
                if level > 1145141919810:
                    level = 1145141919810
                    strings += "等级过高,更改为1145141919810\n"
                skills[i] = [id, value, level]
                found = True
                break

        if not found:
            skills.append([id, value, level])

        # 移除等级 <=0 的技能
        skills = [sk for sk in skills if sk[2] > 0]
        user_data["skill"] = skills

        DHandles.save_user(uid, user_data)
        strings += f"获得技能：{dicts.skill_dict[id]}（等级：{level}）（ID：{id}）\n"
        return strings

    @staticmethod
    def state_refresh(uid: str, id: int, value=time(), level: int = 1, mode: str = ''):
        strings = ''
        user_data = DHandles.load_user(uid)
        if user_data is None:
            return f"用户 {uid} 不存在"

        if "state" not in user_data:
            user_data["state"] = []

        states = user_data["state"]
        found = False
        for i, st in enumerate(states):
            if st[0] == id:
                if mode == 'add':
                    level += st[2]
                if level > 1145141919810:
                    level = 1145141919810
                    strings += "等级过高,更改为1145141919810\n"
                states[i] = [id, value, level]
                found = True
                break

        if not found:
            states.append([id, value, level])

        # 移除等级 <=0 的状态
        states = [st for st in states if st[2] > 0]
        user_data["state"] = states

        DHandles.save_user(uid, user_data)

        duration = int(value - time())
        strings += f"获得状态：{dicts.state_dict[id]}（等级：{level}）（ID：{id}）（持续时间：{duration}秒）\n"
        return strings

    # 废弃的方法（可删除或留空）
    @staticmethod
    def file_save():
        """不再需要，留空避免报错"""
        pass

    @staticmethod
    def data_test_file_save():
        """不再需要，留空避免报错"""
        pass