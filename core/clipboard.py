#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' read and write clipboard '

__author__ = 'Zhu XiaoLong'

import pyperclip

class ClipBorad(object):
    def read_clipboard_data(self):
        return [pyperclip.paste()]
