from jmcomic import JmcomicClient, JmOption
import os
import asyncio

from utils.websocket_utils import send_message
from config import JM_DOWNLOAD_DIR
from .jm_downloader import (
    get_option,
    download_album_by_id,
    move_album_dirs_by_photo_titles,
    safe_cleanup,
)
from .jm_tools import images_to_pdf, batch_chapter_to_pdfs, zip_pdfs

active_tasks = {}

async def get_album_info(album_id: str):
    option = get_option()
    client: JmcomicClient = option.build_jm_client()
    album = await asyncio.to_thread(client.album, album_id)

    title = album.title
    photo_count = album.photo_count
    chapters = album.chapter_list
    return {
        "title": title,
        "photo_count": photo_count,
        "chapter_count": len(chapters)
    }


async def handle_jm(message_text, user_id, group_id, websocket):

    # 防止重复请求
    if active_tasks.get(user_id, False):
        await send_message(websocket, "⏳ 阁下的上一个请求还在处理，稍微耐心一些...", user_id, group_id)
        return

    active_tasks[user_id] = True

    args = message_text.split(' ')
    if len(args) != 2 or not args[1].isdigit():
        await send_message(websocket, "❗ 阁下，请注意吟唱格式: .JM [本子ID]，例如 .JM 472537", user_id, group_id)
        return

    album_id = args[1]

    await send_message(websocket, f"📥 已接收到阁下的请求，开始收集材料 {album_id}，请稍候…", user_id, group_id)


    option = get_option()
    album = await download_album_by_id(album_id, option)

    album_dir = move_album_dirs_by_photo_titles(album, user_id)
    if not os.path.exists(album_dir):
        await send_message(websocket, "❌ 抱歉阁下，下载任务失败了：可能是主目录不存在", user_id, group_id)
        return

    subdirs = sorted([
        d for d in os.listdir(album_dir)
        if os.path.isdir(os.path.join(album_dir, d))
    ])
    image_files = [
        f for f in os.listdir(album_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    if len(subdirs) == 0 and image_files:
        pdf_path = os.path.join(album_dir, f"{album_id}.pdf")
        await asyncio.to_thread(images_to_pdf, album_dir, pdf_path)
        await send_message(websocket,f"[CQ:image,file=file:///{pdf_path}]", user_id, group_id)

    elif len(subdirs) == 1:
        chapter_name = subdirs[0]
        chapter_dir = os.path.join(album_dir, chapter_name)
        pdf_path = os.path.join(album_dir, f"{album_id}.pdf")
        await asyncio.to_thread(images_to_pdf, chapter_dir, pdf_path)
        await send_message(websocket,f"[CQ:image,file=file:///{pdf_path}]", user_id, group_id)

    else:
        pdf_paths = await asyncio.to_thread(batch_chapter_to_pdfs, album_dir)
        if not pdf_paths:
            await send_message(websocket, "❌ 抱歉阁下，我暂时没有发现可以打包的 章节PDF 文件", user_id, group_id)
            return
        zip_path = os.path.join(album_dir, f"{album_id}.zip")
        await asyncio.to_thread(zip_pdfs, pdf_paths, zip_path)
        await send_message(websocket,f"[CQ:image,file=file:///{zip_path}]", user_id, group_id)

    await asyncio.sleep(1)
    active_tasks[user_id] = False

async def handle_jmzip(message_text, user_id, group_id, websocket):

    if active_tasks.get(user_id, False):
        await send_message(websocket, "⏳ 阁下的上一个请求还在处理，稍微耐心一些...", user_id, group_id)
        return

    active_tasks[user_id] = True

    args = message_text.split(' ')
    if len(args) != 2 or not args[1].isdigit():
        await send_message(websocket,"❗ 阁下，请注意吟唱格式: .JMZIP [本子ID]，例如 .JMZIP 472537", user_id, group_id)
        return

    album_id = args[1]
    album_dir = os.path.join(JM_DOWNLOAD_DIR, user_id, album_id)

    zip_path = os.path.join(album_dir, f"{album_id}.zip")

    if not os.path.exists(album_dir):
        await send_message(websocket,"❌ 阁下所需要的材料还未缓存，请先使用 .JM 下载", user_id, group_id)
        return

    if not os.path.exists(zip_path):
        pdf_paths = await asyncio.to_thread(batch_chapter_to_pdfs, album_dir)
        if not pdf_paths:
            await send_message(websocket,"❌ 抱歉阁下，我暂时没有发现可以打包的 PDF 文件", user_id, group_id)
            return
        await asyncio.to_thread(zip_pdfs, pdf_paths, zip_path)

    await send_message(websocket,f"[CQ:image,file=file:///{zip_path}]", user_id, group_id)
    await asyncio.sleep(1)
    active_tasks[user_id] = False
