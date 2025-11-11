# ~/.astrbot/plugins/push_to_web.py
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import register, Star
from astrbot.api import logger
import aiohttp
import asyncio

@register(
    name="web_bridge",
    author="User",
    description="将QQ群消息转发到本地网页聊天室",
    version="1.0.0"
)
class WebBridgePlugin(Star):
    def __init__(self, context):
        super().__init__(context)
        self.webhook_url = "http://127.0.0.1:8000/qq_message"  # 后端接收地址

    async def initialize(self):
        """插件初始化"""
        logger.info("🌐 WebBridge 插件已加载，准备推送消息到网页")

    @filter.group()  # 只监听群消息
    async def handle_group_message(self, event: AstrMessageEvent):
        """
        处理群聊消息，并推送到网页后端
        """
        # 获取必要信息
        user_nickname = event.get_sender_name() or f"用户{event.user_id}"
        message_content = event.get_message_str()  # 纯文本内容
        timestamp = event.timestamp  # 时间戳（秒）
        group_id = event.group_id

        if not message_content.strip():
            return  # 忽略空消息

        # 构造要发送的数据
        data = {
            "type": "qq",
            "nickname": user_nickname,
            "message": message_content,
            "time": timestamp,
            "group_id": group_id
        }

        # 异步发送到网页后端
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=data) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.warning(f"[WebBridge] 推送失败 HTTP {resp.status}: {text}")
                    else:
                        logger.debug(f"[WebBridge] 成功推送消息: {user_nickname}: {message_content}")
        except Exception as e:
            logger.error(f"[WebBridge] 连接网页后端出错: {e}")

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("🌐 WebBridge 插件已停止")
