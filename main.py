# push_to_web.py
# 兼容 AstrBotLauncher 的旧式 @register 写法

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import register, Star
from astrbot.api import logger

import aiohttp
import asyncio

# 尝试只传三个参数：name, author, version
@register("WebBridge", "User", "1.0.0")
class WebBridgePlugin(Star):
    def __init__(self, context):
        super().__init__(context)
        self.webhook_url = "http://127.0.0.1:8000/qq_message"

    async def initialize(self):
        logger.info("🌐 WebBridge 插件已加载，准备推送消息到网页")

    @filter.group()
    async def on_group_message(self, event: AstrMessageEvent):
        """
        监听群消息并转发到网页后端
        """
        # 获取信息
        nickname = event.get_sender_name() or f"用户{event.user_id}"
        message = event.get_message_str()
        timestamp = event.timestamp

        if not message.strip():
            return  # 忽略空消息

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
            logger.error(f"[WebBridge] 发送请求出错: {e}")

    async def terminate(self):
        logger.info("🌐 WebBridge 插件已停止")
