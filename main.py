# main.py

import aiohttp
import astrbot.api.star as star
import astrbot.api.event.filter as filter
from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

@star.register(
    "anti_lstd",  # 插件名称
    "Your Name",  # 作者
    "检测到“来点色图”禁言",  # 插件描述
    "1.0.0",  # 版本号
    "https://github.com/your_repo"  # 仓库地址
)
class AntiLSTDPlugin(star.Star):
    def __init__(self, context: star.Context) -> None:
        super().__init__(context)
        self.context = context
        self.napcat_api_url = self.context.get_config()['platform_settings'].get('napcat_api_url', '')  # NapCat API 地址
        self.napcat_api_key = self.context.get_config()['platform_settings'].get('napcat_api_key', '') # NapCat API 密钥

    @filter.event_message_type(事件类型值)  # 替换为实际的事件类型
    async def on_group_message(self, event: AstrMessageEvent):
        """
        检测到“来点色图”禁言
        """
        message_str = event.message_str
        group_id = event.message_obj.group_id
        user_id = str(event.message_obj.sender.user_id) # 确保 user_id 是字符串类型

        logger.debug(f"收到群消息: {message_str}，群号: {group_id}，用户 ID: {user_id}")

        if "来点色图" in message_str.lower():  # 忽略大小写
            try:
                await self.mute_user_via_napcat(group_id, user_id, 300) # 禁言 5 分钟 (300 秒)
                logger.info(f"用户 {user_id} 在群 {group_id} 中发送“来点色图”，已禁言 5 分钟。")
                # 添加一条消息, 告诉执行结果
                yield event.plain_result(f"用户 {user_id} 因发送不当内容已被禁言 5 分钟。")

            except Exception as e:
                logger.exception(f"禁言用户 {user_id} 失败: {e}")
                yield event.plain_result(f"禁言用户失败，请检查日志。错误信息: {e}") # 包含错误信息

    async def mute_user_via_napcat(self, group_id: str, user_id: str, duration: int):
        """
        调用 NapCat API 禁言用户。
        """
        if not self.napcat_api_url or not self.napcat_api_key:
            logger.error("NapCat API URL or API Key not configured.")
            raise Exception("NapCat API 未配置")

        url = f"{self.napcat_api_url}/set_group_ban"  # 替换为实际的 NapCat 禁言 API
        headers = {
            "Authorization": f"Bearer {self.napcat_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration # 禁言时长，单位为秒
        }

        logger.debug(f"正在禁言用户 {user_id}，群号: {group_id}，时长: {duration} 秒")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    response_data = await response.json()
                    if response.status == 200 and response_data.get("code") == 0:
                        logger.info(f"成功禁言用户 {user_id}，群号: {group_id}，时长: {duration} 秒")
                    else:
                        logger.error(f"禁言用户失败: {response.status} - {response_data}")
                        raise Exception(f"禁言用户失败: {response.status} - {response_data['code']} - {response_data['msg']}")  # 包含错误代码和消息
        except Exception as e:
            logger.exception(f"调用 NapCat API 禁言用户失败: {e}")
            raise
