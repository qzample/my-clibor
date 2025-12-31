#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Use Tkinter for GUI '

__author__ = 'Zhu XiaoLong'

import tkinter as tk
from tkinter import ttk
from core.database import DataBase
from core.clipboard import ClipBorad
import clipboard_monitor
import logging
from collections import deque

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

class MyClibor(object):
    '''
    __width: window width
    __height: window height
    __limit: the limit of clipboard size
    '''
    __width = 250
    __height = 600
    __limit = 20

    def __init__(self):
        self.__widget_list = deque()
        self.__db = DataBase()
        self.__clipboard = ClipBorad()

        # read data from clipboard
        self.__load_data_from_clipboard()

        # read data from sqllite3
        self.__load_data_from_db()

        self.__load_fixed_data_from_db()

        # init widget
        self.__init_window()

    def __load_data_from_clipboard(self):
        self.__clipboard_data = self.__clipboard.read_clipboard_data()

    def __load_fixed_data_from_db(self):
        return self.__db.read_fixed_clipboard_data()

    def __load_data_from_db(self):
        clipboard_data = self.__db.read_clipboard_data()
        if len(clipboard_data) == 0 and len(self.__clipboard_data) != 0:
            for item in self.__clipboard_data:
                self.__db.write_clipboard_data(item)
            return
        self.__clipboard_data = deque(clipboard_data)
        while len(self.__clipboard_data) > 20:
            self.__clipboard_data.popleft()

    def __init_window(self):
        '''
        init window by tkinter

        :param self: Description
        '''
        root = tk.Tk()
        root.title('MyClibor')
        root.iconbitmap('./assets/bird.ico')
        root.geometry(f'{self.__width}x{self.__height}-50-50')
        root.resizable(False, False)
        root.configure(bg='#ADD8E6')
        root.columnconfigure(0, weight=1)
        for i in range(self.__limit):
            root.rowconfigure(i, weight=1)
        for i in range(len(self.__clipboard_data)):
            label = None
            value = self.__clipboard_data[i]
            if i % 2:
                label = tk.Label(root, text=value, bg="#3BB5DD")
            else:
                label = tk.Label(root, text=value, bg="#ADD8E6")
            label.bind('<Enter>', self.__on_enter_label)
            label.bind('<Leave>', lambda event,
                       index=i: self.__on_leave_label(event, index))
            label.grid(column=0, row=i, sticky=tk.NSEW, padx=0, pady=0, ipadx=5, ipady=5)
            self.__widget_list.append(label)
        self.__root = root

    def __on_enter_label(self, event):
        event.widget['bg'] = "#074155"

    def __on_leave_label(self, event, index):
        if index % 2:
            event.widget['bg'] = '#3BB5DD'
        else:
            event.widget['bg'] = '#ADD8E6'
    
    def __on_text(self, value):
        logging.info(value)
        self.__db.write_clipboard_data(value)
        self.__clipboard_data.append(value)
        index = len(self.__clipboard_data) - 1
        if index % 2 != 0:
            label = tk.Label(self.__root, text=value, bg="#3BB5DD")
        else:
            label = tk.Label(self.__root, text=value, bg="#ADD8E6")
        label.bind('<Enter>', self.__on_enter_label)
        label.bind('<Leave>', lambda event,
                    index=index: self.__on_leave_label(event, index))
        label.grid(column=0, row=index, sticky=tk.NSEW, padx=0, pady=0, ipadx=5, ipady=5)
        if index > self.__limit - 1:
            self.__clipboard_data.popleft()
            label = self.__widget_list.popleft()
            label.destroy()


    def __start_listen_clipboard(self):
        clipboard_monitor.on_text(self.__on_text)

    def run(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        finally:
            self.__start_listen_clipboard()
            self.__root.mainloop()
