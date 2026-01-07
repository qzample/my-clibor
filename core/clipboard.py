#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' read and write clipboard '

__author__ = 'Zhu XiaoLong'

import pyperclip

class ClipBorad(object):
    def read_clipboard(self):
        return [pyperclip.paste()]

    def write_clipboard(self, value):
        pyperclip.copy(value)