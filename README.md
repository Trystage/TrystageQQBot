# TrystageQQBot

Trystage使用的的QQ机器人项目。
[本项目包含魔改过的chikari_yinpa插件](https://github.com/mrqx0195/nonebot_plugin_chikari_yinpa)
## 项目结构

```
TrystageQQBot/
├── commands/           # 命令定义目录
├── handlers/           # 事件处理器目录
├── main.py             # 主程序入口
├── modules/            # 功能模块目录
│   └── chikari_yinpa/  # 银趴模块
├── resource/           # 资源文件目录
├── utils/              # 工具函数目录
└── requirements.txt    # 依赖文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行项目

```bash
python main.py
```

项目将在12001端口启动WebSocket服务。

## 注意事项

1本项目仅用于学习交流，请勿用于非法用途