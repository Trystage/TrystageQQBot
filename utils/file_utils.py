import json
import os
from typing import List, Dict, Any
from config import PROJECT_ROOT

# 定义数据文件路径
DATA_DIR = PROJECT_ROOT / "data"
GROUPS_FILE = DATA_DIR / "groups.json"


class FileUtils:
    """文件工具类，用于处理群组ID等数据的持久化存储"""

    @staticmethod
    def initialize_data_files():
        """初始化数据文件"""
        # 确保数据目录存在
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 如果群组文件不存在，创建默认文件
        if not os.path.exists(GROUPS_FILE):
            default_data = {
                "joinchat_group_ids": [533050694, 695789887],
                "yinpa_group_ids": [533050694, 695789887, 478943760]
            }
            FileUtils.save_groups_data(default_data)

    @staticmethod
    def load_groups_data() -> Dict[str, Any]:
        """加载群组数据"""
        FileUtils.initialize_data_files()
        try:
            with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或解析失败，返回默认数据
            default_data = {
                "joinchat_group_ids": [533050694, 695789887],
                "yinpa_group_ids": [533050694, 695789887, 478943760]
            }
            FileUtils.save_groups_data(default_data)
            return default_data

    @staticmethod
    def save_groups_data(data: Dict[str, Any]) -> None:
        """保存群组数据到文件"""
        # 确保数据目录存在
        os.makedirs(DATA_DIR, exist_ok=True)
        
        groups_file_path = os.path.join(DATA_DIR, GROUPS_FILE)
        with open(groups_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_joinchat_group_ids() -> List[int]:
        """获取需要处理入群事件的群组ID列表"""
        data = FileUtils.load_groups_data()
        return data.get("joinchat_group_ids", [])

    @staticmethod
    def get_yinpa_group_ids() -> List[int]:
        """获取银趴功能的群组ID列表"""
        data = FileUtils.load_groups_data()
        return data.get("yinpa_group_ids", [])

    @staticmethod
    def get_black_group_ids() -> List[int]:
        """获取黑名单的群组ID列表"""
        data = FileUtils.load_groups_data()
        return data.get("black_group_ids", [])

    @staticmethod
    def add_joinchat_group_id(group_id: int):
        """添加入群事件处理群组ID"""
        data = FileUtils.load_groups_data()
        if group_id not in data["joinchat_group_ids"]:
            data["joinchat_group_ids"].append(group_id)
            FileUtils.save_groups_data(data)

    @staticmethod
    def add_yinpa_group_id(group_id: int):
        """添加银趴功能群组ID"""
        data = FileUtils.load_groups_data()
        if group_id not in data["yinpa_group_ids"]:
            data["yinpa_group_ids"].append(group_id)
            FileUtils.save_groups_data(data)

    @staticmethod
    def add_black_group_id(group_id: int):
        """添加黑名单群组ID"""
        data = FileUtils.load_groups_data()
        if group_id not in data["black_group_ids"]:
            data["black_group_ids"].append(group_id)
            FileUtils.save_groups_data(data)

    @staticmethod
    def remove_joinchat_group_id(group_id: int):
        """移除入群事件处理群组ID"""
        data = FileUtils.load_groups_data()
        if group_id in data["joinchat_group_ids"]:
            data["joinchat_group_ids"].remove(group_id)
            FileUtils.save_groups_data(data)

    @staticmethod
    def remove_yinpa_group_id(group_id: int):
        """移除银趴功能群组ID"""
        data = FileUtils.load_groups_data()
        if group_id in data["yinpa_group_ids"]:
            data["yinpa_group_ids"].remove(group_id)
            FileUtils.save_groups_data(data)

    @staticmethod
    def remove_black_group_id(group_id: int):
        """移除黑名单群组ID"""
        data = FileUtils.load_groups_data()
        if group_id in data["black_group_ids"]:
            data["black_group_ids"].remove(group_id)
            FileUtils.save_groups_data(data)