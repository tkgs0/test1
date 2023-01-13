#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import time
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json


filepath = Path('.').rglob(r'*.json')


start = time.time()
print('loading...')
x = 0
n = len(filepath := list(filepath))

if not n:
    print('没有扫描到json文件.')
    exit(-1)

for _file in filepath:
    x += 1
    y = int(float(x) / n * 20)
    print(
        f"\r[{'='*y}{' '*(20-y)}] {y*5}% {time.time()-start:.2f}s",
        end=' ', flush=True
    )

    try:
        content = json.loads(_file.read_text('utf-8'))
        _file.write_text(
            json.dumps(
                content, ensure_ascii=False,
                escape_forward_slashes=False,
                indent=2
            ),
            encoding='utf-8'
        )
    except:
        continue

print('done.')
