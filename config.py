# 项目配置文件
from pathlib import Path

# WebSocket服务器配置
WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 12000

# 群组ID配置
ADMIN_GROUP_ID = 695789887
TARGET_GROUP_ID = 533050694
BACKUP_GROUP_ID = 695789887
TEST_GROUP_ID = 695789887

SUPER_USER = [3289138258, 728722384, 3654280169, 2257104941]

PROJECT_ROOT = Path(__file__).parent

# 资源目录
RESOURCE_DIR = str(PROJECT_ROOT / "resource")

# 资源文件路径
FONT_FILE = str(PROJECT_ROOT / "resource" / "SourceHanSansSC-VF.ttf")

# API密钥文件路径
API_KEY_FILE = str(PROJECT_ROOT / "resource" / "key")

# 缓存目录
CACHE_DIR = str(PROJECT_ROOT / "cache")

# 日志目录
LOGS_DIR = str(PROJECT_ROOT / "logs")

# 延迟加载群组ID配置，避免循环导入
def get_joinchat_group_ids():
    from utils.file_utils import FileUtils
    return FileUtils.get_joinchat_group_ids()

def get_yinpa_group_ids():
    from utils.file_utils import FileUtils
    return FileUtils.get_yinpa_group_ids()

# 使用属性延迟加载群组ID
class _GroupIds:
    @property
    def JOINCHAT_GROUP_IDS(self):
        return get_joinchat_group_ids()
    
    @property
    def YINPA_GROUP_IDS(self):
        return get_yinpa_group_ids()

GROUP_IDS = _GroupIds()