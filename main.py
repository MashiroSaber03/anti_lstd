# main.py

import aiohttp
import random
import astrbot.api.star as star
import astrbot.api.event.filter as filter
from astrbot.api.event import AstrMessageEvent, MessageEventResult
from astrbot.api import llm_tool, logger
from astrbot.core.message import components

@star.register(
    "qq_group_raffler",  # 插件名称
    "Your Name",  # 作者
    "QQ 群随机抽人",  # 插件描述
    "1.0.0",  # 版本号
    "https://github.com/your_repo"  # 仓库地址
)
class QQGroupRafflerPlugin(star.Star):
    def __init__(self, context: star.Context) -> None:
        super().__init__(context)
        self.context = context
        self.napcat_api_url = self.context.get_config()['platform_settings'].get('napcat_api_url', '')  # NapCat API 地址
        self.napcat_api_key = self.context.get_config()['platform_settings'].get('napcat_api_key', '') # NapCat API 密钥

    @filter.command("抽人")
    async def raffle_command(self, event: AstrMessageEvent, count: int = 1):
        """
        从 QQ 群随机抽取指定数量的群员。
        使用方法: /抽人 <数量>
        """
        group_id = event.message_obj.group_id
        if not group_id:
            yield event.plain_result("该指令只能在群组中使用。")
            return

        try:
            member_list = await self.get_group_members_via_napcat(group_id)
            if not member_list:
                yield event.plain_result("获取群成员列表失败，请检查 NapCat API 是否配置正确。")
                return

            if count <= 0:
                yield event.plain_result("抽取数量必须大于 0。")
                return

            if count > len(member_list):
                yield event.plain_result(f"抽取数量超过群成员总数（{len(member_list)}人）。")
                return

            winners = random.sample(member_list, count)
            result_str = "恭喜以下幸运群友：\n" + "\n".join(winners)
            yield event.plain_result(result_str)

        except ValueError:
            yield event.plain_result("抽取数量必须为整数。")
        except Exception as e:
            logger.exception(f"抽人失败: {e}")
            yield event.plain_result(f"抽人失败，请稍后再试。{e}")

    async def get_group_members_via_napcat(self, group_id: str) -> list:
        """
        通过 NapCat API 获取群成员列表。
        """
        if not self.napcat_api_url or not self.napcat_api_key:
            logger.error("NapCat API URL or API Key not configured.")
            return None

        url = f"{self.napcat_api_url}/获取群成员列表"  # 替换为实际的 NapCat 获取群成员列表 API
        headers = {
            "Authorization": f"Bearer {self.napcat_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "group_id": group_id
        }

        logger.debug(f"请求 NapCat API，URL: {url}，Headers: {headers}，Data: {data}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    logger.debug(f"NapCat API 响应状态码: {response.status}")
                    response_data = await response.json()
                    logger.debug(f"NapCat API 响应内容: {response_data}")

                if response.status == 200 and response_data.get("status") == "ok" and response_data.get("retcode") == 0:
                    member_list = [str(member["user_id"]) for member in response_data.get("data", [])] # 提取QQ号
                    logger.info(f"成功获取群成员列表，群号: {group_id}，成员数量: {len(member_list)}")
                    return member_list
                else:
                    logger.error(f"获取群成员列表失败: {response.status} - {response_data}")
                    return None
        except Exception as e:
            logger.exception(f"从 NapCat 获取群成员列表失败: {e}")
            return None

