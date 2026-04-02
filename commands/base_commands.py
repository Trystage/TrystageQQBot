# 基础命令处理模块
from config import ADMIN_GROUP_ID, TEST_GROUP_ID

def is_announce_command(message_text, group_id):
    """检查是否为公告命令"""
    return message_text.startswith("/try announce")


def is_feedback_command(message_text):
    """检查是否为反馈命令"""
    return message_text.startswith("/try ref")


def is_mute_command(message_text, group_id):
    """检查是否为禁言命令（仅限管理员群或测试群）"""
    return message_text.startswith("/try mute")


def is_report_command(message_text):
    """检查是否为举报命令"""
    return message_text.startswith("/try report")


def is_help_command(message_text):
    """检查是否为帮助命令"""
    return message_text == "/try" or message_text.startswith("/try help")


def is_add_group_command(message_text, group_id):
    """检查是否为添加群组ID命令（仅限管理员群或测试群）"""
    return message_text.startswith("/try add")

def is_remove_group_command(message_text, group_id):
    """检查是否为添加群组ID命令（仅限管理员群或测试群）"""
    return message_text.startswith("/try rem")


def is_yinpa_command(message_text):
    """检查是否为银趴命令"""
    yinpa_commands = ["yinpa_control", "银趴控制", "sign_in", "签到", "打卡", "info", "信息", "查询",
                      "yinpa_help", "银趴帮助", "yinpa_join", "加入银趴", "yinpa_leave", "离开银趴",
                      "tou", "透", "插入", "zha", "榨", "榨精", "chong", "冲", "打胶", "手冲", "撸", "导",
                      "kou", "扣", "扣扣", "自慰", "紫薇", "shop", "商店", "买", "买东西", "店",
                      "work", "工作", "打工", "pay", "打钱", "v ", "yinpa_test", "yinpa_set", "老手礼包"]
    return any(message_text.startswith(cmd) for cmd in yinpa_commands)

def is_jm_command(message_text):
    jm_commands = ["jmz", "jm", "jmc", "jmzip", "jmcomiczip", "jmczip", "jmcomic"]
    return any(message_text.startswith(cmd) for cmd in jm_commands)
