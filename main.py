import logging
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.event.filter import EventMessageType, event_message_type

# 获取当前模块 logger
logger = logging.getLogger(__name__)

@register(
    "keyword_watcher",
    "AI助手",
    "一个关键词监听插件，当群里有人提到关键词时，Bot会私聊发送消息",
    "1.0",
    "https://github.com/your_github/astrbot_plugin_keyword_watcher",  # 替换为你的仓库地址
)
class KeywordWatcherPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.keyword = None  # 初始化关键词
        self.default_reply = "我在看着你哦" # 初始化默认回复

    @filter.command("设置关键词 {keyword}")
    async def set_keyword(self, event: AstrMessageEvent, keyword: str):
        """设置监听的关键词"""
        self.keyword = keyword
        yield event.plain_result(f"关键词已设置为：{self.keyword}")

    @filter.command("设置回复 {reply}")
    async def set_reply(self, event: AstrMessageEvent, reply: str):
        """设置监听的关键词"""
        self.default_reply = reply
        yield event.plain_result(f"回复内容已设置为：{self.default_reply}")

    @event_message_type(EventMessageType.GROUP)
    async def on_group_message(self, event: AstrMessageEvent) -> MessageEventResult:
        """监听群聊消息，匹配关键词并私聊发送消息"""
        if not self.keyword:
            return MessageEventResult.unhandled #如果没有设置关键词，则不处理

        message_text = event.message_obj.message_str or ""

        if self.keyword in message_text:
            user_id = event.message_obj.user_id  # 触发消息的用户 ID
            group_id = event.message_obj.group_id

            if not user_id:
                logger.warning(f"无法获取用户ID, 消息: {event.message_obj.raw_message}")
                return MessageEventResult.unhandled

            if not group_id:
                logger.warning(f"无法获取群组ID, 消息: {event.message_obj.raw_message}")
                return MessageEventResult.unhandled

            try:
                # 构造私聊消息
                reply_text = f"{self.default_reply}"

                # 调用 NapCat API 发送私聊消息
                api_url = f"你的 NapCat 实例地址/send_private_msg"  # 替换为你的 NapCat 实例地址
                api_data = {
                    "user_id": user_id,
                    "message": reply_text,
                }
                api_headers = {"Content-Type": "application/json"}

                import requests
                import json

                response = requests.post(api_url, headers=api_headers, data=json.dumps(api_data))

                if response.status_code == 200:
                    response_json = response.json()
                    if response_json["status"] == "ok" and response_json["retcode"] == 0:
                        logger.info(f"已向用户 {user_id} 发送私聊消息")
                    else:
                        logger.error(f"发送私聊消息失败: {response_json['message']}")
                else:
                    logger.error(f"API 请求失败，状态码: {response.status_code}")

                return MessageEventResult.handled #表示已经处理
            except Exception as e:
                logger.exception("处理消息时发生错误")
                return MessageEventResult.unhandled
        return MessageEventResult.unhandled #如果消息没有关键词，不处理
