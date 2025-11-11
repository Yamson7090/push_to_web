# push_to_web.py
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import register, Star
from astrbot.api import logger

import aiohttp
import asyncio

# 尝试传入 4 个参数：name, author, description, version
@register("WebBridge", "User", "QQ群消息转发到网页", "1.0.0")
class WebBridgePlugin(Star):
    def __init__(self, context):
        super().__init__(context)
        self.webhook_url = "http://127.0.0.1:8000/qq_message"

    async def initialize(self):
        logger.info("🌐 WebBridge 插件已加载，准备推送消息")

    @filter.group()
    async def on_group_message(self, event: AstrMessageEvent):
        nickname = event.get_sender_name() or f"用户{event.user_id}"
        message = event.get_message_str()
        timestamp = event.timestamp

        if not message.strip():
            return

        data = {
            "type": "qq",
            "nickname": nickname,
            "message": message,
            "time": timestamp
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=data) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.warning(f"[WebBridge] 推送失败: {resp.status} {text}")
        except Exception as e:
            logger.error(f"[WebBridge] 请求出错: {e}")

    async def terminate(self):
        logger.info("🌐 WebBridge 插件已停止")
