import re
from nonebot.adapters.onebot.v11 import MessageSegment, unescape

class Funny():

    @staticmethod
    def fake_msg(text: str) -> list:
        arg = text.split("\n")
        node = list()
    
        for i in arg:
            args = i.split("-")
            qq = args[0]
            name = unescape(args[1])
            repo = unescape(args[2].replace("\\n","\n"))
            if r := re.search('\[CQ:image[^\[\]]*\]',repo):  # type: ignore
                r = r if not 'http' in r.group() else re.search('http[^\[\],]*,?', r.group())  # type: ignore
                repo = repo.replace(r.group(), f'{MessageSegment.image(file=r.group().strip(","))}')  # type: ignore
            dic = {"type": "node", "data": {"name": name, "uin": qq, "content": repo}}
            node.append(dic)
        return node

