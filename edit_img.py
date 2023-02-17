#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from sys import argv
from pathlib import Path
from nonebot_plugin_imageutils import BuildImage as Image


def edit_img(filepath: Path) -> bytes | str:
    image = Image.open(filepath)
    if image.width <= 2000:
        return '图片不大'
    image = image.resize_width(2000)
    return image.save_png().getvalue()


def run(arg: str) -> str:
    filepath = Path(arg)
    img = edit_img(filepath) if filepath.is_file() else '文件不存在'

    if isinstance(img, str):
        return img

    filepath.write_bytes(img)
    return 'complete'


if __name__ == '__main__':
    if len(argv) < 2:
        print('需要参数')
        exit(-1)
    print(run(argv[1]))

