# main.py

import aiohttp
import random
import astrbot.api.star as star
import astrbot.api.event.filter as filter
from astrbot.api.event import AstrMessageEvent, MessageEventResult
from astrbot.api import llm_tool, logger
from astrbot.core.message import components
from .engines.bing import Bing
from .engines.sogo import Sogo
from .engines.google import Google
from readability import Document
from bs4 import BeautifulSoup
from .engines import HEADERS, USER_AGENTS

@star.register(name="scare_mode_qq", desc="QQ 机器人：开启恐吓模式，有人 @ 机器人时发送私聊", author="Your Name", version="1.0.0")
class ScareModeQQPlugin(star.Star):
    def __init__(self, context: star.Context) -> None:
        super().__init__(context)
        self.context = context
        self.scare_mode = False  # 恐吓模式开关
        self.napcat_api_url = self.context.get_config()['platform_settings'].get('napcat_api_url', '')  # NapCat API 地址
        self.napcat_api_key = self.context.get_config()['platform_settings'].get('napcat_api_key', '') # NapCat API 密钥

    @filter.command("scare")
    async def scare_command(self, event: AstrMessageEvent, oper: str = None):
        """
        控制恐吓模式的开启和关闭。
        使用方法: /scare on 或 /scare off
        """
        if oper == "on":
            self.scare_mode = True
            yield event.plain_result("已开启恐吓模式")
        elif oper == "off":
            self.scare_mode = False
            yield event.plain_result("已关闭恐吓模式")
        else:
            status = "开启" if self.scare_mode else "关闭"
            yield event.plain_result(f"当前恐吓模式状态：{status}。使用 /scare on 或 /scare off 开启或关闭。")

    @filter.event_message_type(star.EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        """
        监听 QQ 群消息，如果有人 @ 机器人，则发送私聊消息。
        """
        if not self.scare_mode:
            return

        #判断是否at了
        if not self.is_at_me(event):
            return
        
        # 获取@用户的QQ号
        user_id = event.message_obj.sender.user_id # 发送者 QQ 号
        bot_id = event.message_obj.self_id # 机器人QQ号
        session_id = bot_id + "_" + user_id #构造私聊会话id

        # 发送私聊消息
        await self.send_private_message_via_napcat(session_id, "我在看着你")

    async def send_private_message_via_napcat(self, session_id: str, message: str):
        """
        通过 NapCat API 发送私聊消息。
        """
        if not self.napcat_api_url or not self.napcat_api_key:
            logger.error("NapCat API URL or API Key not configured.")
            return

        url = f"{self.napcat_api_url}/send"
        headers = {
            "Authorization": f"Bearer {self.napcat_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "session_id": session_id,
            "message_type": "private",
            "message": message,
            "auto_escape": False, # 根据需要修改
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    response_data = await response.json()
                    if response.status == 200 and response_data.get("code") == 0:
                        logger.info(f"发送恐吓消息成功: {message}，Session ID: {session_id}")
                    else:
                        logger.error(f"发送恐吓消息失败: {response.status} - {response_data}")
        except Exception as e:
            logger.exception(f"发送消息到 NapCat 失败: {e}")

    def is_at_me(self, event: AstrMessageEvent) -> bool:
        """
        判断消息是否 @ 了机器人
        """
        for msg in event.message_obj.message:
            if msg.type == "at" and msg.qq == event.message_obj.self_id:
                return True
        return False


