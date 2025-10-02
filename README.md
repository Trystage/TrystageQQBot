# TrystageQQBot

一个基于WebSocket的QQ机器人项目，实现了银趴(chikari_yinpa)模块功能。

## 项目结构

```
new_TrystageQQBot/
├── commands/           # 命令定义目录
├── handlers/           # 事件处理器目录
├── main.py             # 主程序入口
├── modules/            # 功能模块目录
│   └── chikari_yinpa/  # 银趴模块
│       ├── __init__.py
│       ├── config.py   # 配置文件
│       ├── data_handles.py  # 数据处理
│       ├── dicts.py    # 字典定义
│       ├── handles.py  # 处理器
│       └── utils.py    # 工具函数
├── resource/           # 资源文件目录
├── utils/              # 工具函数目录
└── requirements.txt    # 依赖文件
```

## 功能特性

- 基于WebSocket的通信协议
- 实现了银趴(chikari_yinpa)模块的核心功能：
  - 用户签到系统
  - 角色属性管理（长度、深度、性别倾向等）
  - 种族系统
  - 技能系统
  - 状态系统
  - 商店系统
  - 工作系统
- 模块化设计，易于扩展

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行项目

```bash
python main.py
```

项目将在11007端口启动WebSocket服务。

## 银趴模块命令

- `银趴帮助` - 显示帮助信息
- `银趴签到` - 每日签到
- `银趴加入` - 加入银趴游戏
- `银趴状态` - 查看当前状态
- `银趴信息` - 查看详细信息
- `银趴商店` - 访问商店
- `银趴工作` - 工作赚钱
- `银趴技能` - 查看技能
- `银趴种族` - 查看种族信息

## 配置说明

在`modules/chikari_yinpa/config.py`中可以修改以下配置：

- 初始性别倾向
- 初始长度
- 初始深度
- 初始金钱
- 绘图所用字体

## 注意事项

1. resource目录下的字体文件需要替换为实际的SourceHanSansSC-VF.ttf字体文件
2. 本项目仅用于学习交流，请勿用于非法用途