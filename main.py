# plugins/push_to_web.py
from astrbot.core.plugin.plugin_base import PluginBase
from astrbot.core.platform.astr_message_event import MessageEvent
import aiohttp
import asyncio

class PushToWeb(PluginBase):
    def __init__(self, context):
        super().__init__(context)
        self.webhook_url = "http://127.0.0.1:8000/qq_message"  # 我们的后端接收地址

    async def process(self, event: MessageEvent):
        if event.type != "group":
            return  # 只处理群消息

        data = {
            "type": "qq",
            "nickname": event.get_nickname() or f"用户{event.user_id}",
            "message": event.get_message_content(),
            "time": event.timestamp  # 时间戳（秒）
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=data) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        print(f"[PushToWeb] 推送失败: {resp.status}, {text}")
        except Exception as e:
            print(f"[PushToWeb] 连接后端出错: {e}")
