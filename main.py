#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' main function for my-clibor '

__author__ = 'Zhu XiaoLong'

from gui.layout import MyClibor
from win32event import CreateMutex
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS
import sys



if __name__ == "__main__":
    mutex_name = "MyClibor"
    mutex = CreateMutex(None, False, mutex_name)
    last_error = GetLastError()

    if last_error == ERROR_ALREADY_EXISTS:
        # 如果检测到互斥锁已存在，说明程序已经运行
        sys.exit(0)
    my_clibor = MyClibor()
    my_clibor.run()