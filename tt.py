#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from httpx import AsyncClient

import sys, asyncio
from pathlib import Path


filepath = Path(__file__).parent / 'output.png'


headers = {
    'Host': 'i.pximg.net',
    'Referer': 'https://www.pixiv.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

async def get_url(url, headers = headers, redirects = True):
    async with AsyncClient() as client:
        response = await client.get(
            url,
            headers = headers,
            follow_redirects = redirects,
            timeout = 120
        )
        if response.status_code == 200:
            filepath.write_text(response.text)
        return response.status_code


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        exit(-1)
    print(asyncio.run(get_url(arg)))
