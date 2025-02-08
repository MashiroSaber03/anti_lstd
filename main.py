import logging
from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.event.filter import EventMessageType, event_message_type
from astrbot.api.message import At, Plain

# 获取当前模块 logger
logger = logging.getLogger(__name__)

@register("stalker", "YourName", "当群员@bot时，私聊发送“我在看着你哦”", "1.0", "https://example.com/your_repo")  # 替换信息
class StalkerPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.self_id = self.context.bot_id # 获取机器人自身的 ID

    @event_message_type(EventMessageType.GROUP)
    async def on_group_message(self, event: AstrMessageEvent) -> MessageEventResult:
        """
        监听群消息，当检测到有人@bot时，私聊发送消息。
        """
        msg_obj = event.message_obj
        group_id = msg_obj.group_id
        user_id = msg_obj.user_id

        if group_id is None:
            return MessageEventResult.unhandled  # 只处理群聊消息

        # 遍历消息链，查找 @Bot 的消息段
        for segment in msg_obj.message:
            if isinstance(segment, At) and str(segment.qq) == str(self.self_id): # 检查 At 消息段是否 @ 本 Bot
                try:
                    # 调用 API 发送私聊消息 (使用 self.bot.send_private_msg，如果可用)
                    # 也可以使用 NapCat API, 具体要看 AstrBot 框架如何封装API
                    # 如果 AstrBot 没有封装，可能需要自己构建 HTTP 请求
                    await event.reply_private(user_id, "我在看着你哦")  #假设event.reply_private可以直接调用，发送私聊消息
                    logger.info(f"向用户 {user_id} 发送了私聊消息 '我在看着你哦'")

                except Exception as e:
                    logger.exception(f"发送私聊消息失败: {e}")
                    # 可以考虑在群里发送一个错误提示，但需要谨慎，避免暴露过多信息
                
                return MessageEventResult.handled # 已经处理，停止事件传播

        return MessageEventResult.unhandled  # 没有 @Bot，不处理



