#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

while True:
    try:
        x = input('请输入: ')
        if (y := x.encode('punycode').decode('utf-8')).endswith('-') or not x:
            print(x)
        else:
            print('xn--' + y)
        input()
    except KeyboardInterrupt:
        exit()
