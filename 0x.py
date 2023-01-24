#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys, random

# random.seed(0x1010)  #设置随机种子数

#设置种子选择空间
s = "0123456789ABCDEF"

ls = [] #存取密码的列表

FirstPsw = "" #存取第一个密码的字符

length = 8 #默认密码长度
try:
    length = int(sys.argv[1]) #从命令行自定义密码长度
    print(f'\033[1;32m设置密码长度为:{length}\033[0m')
except ValueError:
    print(f'\033[1;31m输入值非int, 使用默认值:{length}\033[0m')
except IndexError:
    print(f'\033[1;33m未定义长度, 使用默认值:{length}\033[0m')


while len(ls) < 10:  #10个随机密码
    pwd = "0x"
    for i in range(length):
        pwd += s[random.randint(0,len(s)-1)]
    ls.append(pwd)
    FirstPsw +=pwd[0]


print("\n".join(ls))
