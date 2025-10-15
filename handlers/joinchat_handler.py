import os
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time
from datetime import datetime
from utils.websocket_utils import send_message
from config import RESOURCE_DIR, FONT_FILE

# 创建保存图片的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, "..", "cache", "welcome_images")
os.makedirs(images_dir, exist_ok=True)

async def download_avatar(user_id):
    """下载用户头像"""
    try:
        print(f"开始下载用户 {user_id} 的头像...")
        avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
        print(f"头像URL: {avatar_url}")
        
        # 下载头像
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as avatar_resp:
                print(f"下载头像响应状态: {avatar_resp.status}")
                if avatar_resp.status == 200:
                    avatar_data = await avatar_resp.read()
                    print(f"成功下载头像，大小: {len(avatar_data)} 字节")
                    return Image.open(BytesIO(avatar_data))
                else:
                    print(f"下载头像失败，状态码: {avatar_resp.status}")
    except Exception as e:
        print(f"下载头像时出错: {e}")
    return None

async def create_welcome_image(user_id, user_name):
    """创建欢迎图片并保存到本地"""
    try:
        print(f"开始为 {user_name}({user_id}) 创建欢迎图片...")
        # 加载背景图片
        bg_path = os.path.join(script_dir, "..", RESOURCE_DIR, "welcome_bg.png")
        print(f"背景图片路径: {bg_path}")
        if not os.path.exists(bg_path):
            print("未找到背景图片，使用默认背景")
            # 如果没有背景图片，创建一个默认背景
            bg_image = Image.new('RGB', (800, 400), color=(50, 50, 50))
        else:
            print("找到背景图片，正在加载...")
            bg_image = Image.open(bg_path)
            print(f"背景图片尺寸: {bg_image.size}")
        
        # 下载用户头像
        avatar = await download_avatar(user_id)
        if avatar:
            print("头像下载成功，正在处理...")
            # 计算头像位置 - 居中显示
            bg_width, bg_height = bg_image.size
            # 调整头像大小
            avatar_size = (bg_height // 3, bg_height // 3)
            avatar = avatar.resize(avatar_size)
            # 创建一个圆形遮罩
            mask = Image.new('L', avatar_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)
            
            avatar_x = (bg_width - avatar_size[0]) // 2  # 水平居中
            avatar_y = (bg_height - avatar_size[1]) // 2  # 垂直方向在上半部分居中
            
            # 将头像粘贴到背景上
            bg_image.paste(avatar, (avatar_x, avatar_y), mask)
            print("头像已添加到背景")
        else:
            print("头像下载失败，将创建不带头像的欢迎图片")
        
        # 添加文字
        draw = ImageDraw.Draw(bg_image)
        try:
            # 使用配置中的字体文件
            font_path = os.path.join(script_dir, "..", RESOURCE_DIR, FONT_FILE)
            font = ImageFont.truetype(font_path, 40)
            print(f"使用字体: {FONT_FILE}")
        except:
            # 回退到默认字体
            font = ImageFont.load_default()
            print("使用默认字体")
        
        # 添加欢迎文字
        welcome_text = f"欢迎{user_name}加入群聊"
        
        # 计算文字位置 - 在头像下方居中
        text_bbox = draw.textbbox((0, 0), welcome_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 文字位置：水平居中，垂直方向在图片下半部分的顶部
        text_x = (bg_width - text_width) // 2
        text_y = (bg_height + avatar_size[1]) // 2 + 20  # 从图片中间往下20像素
        
        # 绘制文字（带有一点阴影效果）
        shadow_color = (0, 0, 0)  # 黑色阴影
        main_color = (255, 255, 85)  # 主文字颜色
        
        # 先绘制阴影
        draw.text((text_x + 2, text_y + 2), welcome_text, font=font, fill=shadow_color)
        # 再绘制主文字
        draw.text((text_x, text_y), welcome_text, font=font, fill=main_color)
        
        print(f"已添加文字: {welcome_text}")
        
        # 生成唯一文件名
        timestamp = int(time.time())
        filename = f"welcome_{user_id}_{timestamp}.png"
        output_image_path = os.path.join(images_dir, filename)
        
        # 保存图片到本地
        bg_image.save(output_image_path, format='PNG')
        print(f"图片已保存到: {output_image_path}")
        
        return output_image_path
    except Exception as e:
        print(f"创建欢迎图片时出错: {e}")
        return None

async def handle_join_event(user_id, group_id, websocket):
    """处理群成员加入事件"""
    try:
        print(f"新成员加入: user_id={user_id}, group_id={group_id}")

        # 获取用户名
        user_name = f"({user_id})"  # 默认使用ID
        try:
            print("正在获取用户信息...")
            async with aiohttp.ClientSession() as session:
                # 注意：这里可能需要根据实际的API地址进行调整
                async with session.get(f'http://127.0.0.1:3000/get_stranger_info?user_id={user_id}') as resp:
                    print(f"获取用户信息响应状态: {resp.status}")
                    if resp.status == 200:
                        user_info = await resp.json()
                        print(f"用户信息: {user_info}")
                        if user_info.get('retcode') == 0:
                            user_name = user_info['data']['nickname']
                            print(f"获取到用户名: {user_name}")
                        else:
                            print(f"获取用户信息失败，错误码: {user_info.get('retcode')}")
        except Exception as e:
            print(f"获取用户信息时出错: {e}")

        # 创建欢迎图片
        print("开始创建欢迎图片...")
        output_image_path = await create_welcome_image(user_id, user_name)

        if output_image_path:
            print("图片创建成功，准备发送消息")
            # 构建包含图片的消息 - 使用本地文件路径
            message_content = f"[CQ:image,file=file:///{output_image_path}]"
        else:
            print("图片创建失败，使用文本消息")
            # 如果图片生成失败，使用文本消息
            message_content = f"欢迎新成员{user_name}加入群聊~"

        print(f"最终消息内容: {message_content}")

        # 发送欢迎消息到群组
        await send_message(websocket, message_content, group_id=group_id)
        print("欢迎消息已发送")

    except Exception as e:
        print(f"处理入群事件时出错: {e}")