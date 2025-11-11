# 文件路径：data\plugins\push_to_web.py

from astrbot.api.star import register, Star
from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

import aiohttp
import asyncio

# 使用 4 参数注册（根据你之前成功的尝试）
@register("WebBridge", "User", "QQ群转网页", "1.0.0")
class WebBridgePlugin(Star):
    def __init__(self, context):
        super().__init__(context)
        self.webhook_url = "http://127.0.0.1:8000/qq_message"

    async def initialize(self):
        logger.info("🌐 WebBridge 插件已加载")

    async def process(self, event: AstrMessageEvent):
        """
        所有消息都会经过这里（核心处理函数）
        我们手动判断是不是群消息
        """
        # 手动判断：如果 event 没有 group_id，说明不是群消息
        if not hasattr(event, 'group_id') or event.group_id is None:
            return  # 不是群消息，忽略

        # 获取用户昵称和消息内容
        nickname = getattr(event, 'sender', {}).get('nickname') or f"用户{event.user_id}"
        message = event.get_message_str()
        timestamp = event.timestamp

        if not message or not message.strip():
            return  # 忽略空消息

        # 构造要发送的数据
        data = {
            "type": "qq",
            "nickname": nickname,
            "message": message.strip(),
            "time": int(timestamp)
        }

        # 发送到网页后端
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=data) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.warning(f"[WebBridge] 推送失败 HTTP {resp.status}: {text}")
                    else:
                        logger.debug(f"[WebBridge] 已推送: {nickname}: {message}")
        except Exception as e:
            logger.error(f"[WebBridge] 网络错误: {e}")

    async def terminate(self):
        logger.info("🌐 WebBridge 插件已停止")
