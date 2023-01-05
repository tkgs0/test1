from nonebot import on_command
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.adapters.onebot.v11.helpers import autorevoke_send


withdraw_t = on_command('withdraw', permission=SUPERUSER)


@withdraw_t.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    args: Message = CommandArg()
):
    arg = args.extract_plain_text()
    _time  = int(arg) if arg and is_number(arg) and int(arg)<=120 else 10
    await autorevoke_send(
        bot=bot,
        event=event,
        message=f'撤回消息测试: 于{_time}秒后撤回本消息',
        revoke_interval=_time)


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
