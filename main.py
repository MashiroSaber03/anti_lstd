from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.llm import Function, Arg

@register(
    "ccb_generator",
    "AstrBot",
    "将事件解构成XX笑传之CCB",
    "1.0.0",
    "https://example.com/ccb_generator",
)
class CCBGenerator(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.llm_name = "default"  # 可配置的 LLM 名称，这里先用 "default"
        self.llm = self.context.get_llm(self.llm_name)

    @filter.command("ccb {event}")
    async def generate_ccb(self, event: AstrMessageEvent, event: str):
        """将事件解构成XX笑传之CCB格式"""
        prompt = f"请将以下事件解构成 'XX笑传之CCB' 的格式：{event}\n\n请只返回 'XX笑传之CCB' 格式的结果，不要包含任何其他解释或说明。"
        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self.llm.chat(messages, event.source)
            ccb_result = response.content
            await event.reply(ccb_result)
        except Exception as e:
            self.context.logger.error(f"生成 CCB 失败: {e}")
            await event.reply("生成 CCB 失败，请检查后台日志。")

        return MessageEventResult.handled
