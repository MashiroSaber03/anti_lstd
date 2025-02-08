from astrbot.api.all import *

@register(
    "astrbot_plugin_repeat",
    "ましろSaber",
    "连续监测到两条相同的消息后自动复读一遍",
    "1.0.0",
    "repo url"
)
class RepeatMessagePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.last_message = None
        self.repeat_count = 0

    @event_message_type(EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        """
        监听所有消息，如果连续两条消息相同，则自动复读一遍。
        """
        current_message = event.message_str

        if self.last_message == current_message:
            self.repeat_count += 1
            if self.repeat_count == 1:  # 连续两条相同
                yield event.plain_result(f"{current_message}") # 复读消息
                self.repeat_count = 0 # 防止连续复读，重置计数器
        else:
            self.repeat_count = 0 
        
        self.last_message = current_message 
