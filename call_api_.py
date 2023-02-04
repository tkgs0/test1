from ast import literal_eval
from httpx import AsyncClient
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message


callapi = on_command(
    '/api',
    permission=SUPERUSER,
    priority=1,
    block=True
)

@callapi.handle()
async def _(args: Message = CommandArg()):
    if not args:
        await callapi.finish('需要参数! baka')
    url, params = args.extract_plain_text().split(maxsplit=1)
    res = await get_api(url, params)
    await callapi.finish(res)


async def get_api(url: str, params: str):
    headers = {
        'referer': 'http://127.0.0.1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    params = literal_eval(params)

    async with AsyncClient() as client:
        try:
            response = await client.get(url=url, params=params, headers=headers, timeout=30)
            try:
                res = response.json()
                res = json.dumps(res, indent=2, ensure_ascii=False)
            except:
                res = ',\n'.join(response.text.split(', '))
            await response.aclose()
            return res
        except Exception as e:
            return repr(e)

