#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' Use Tkinter for GUI '

__author__ = 'Zhu XiaoLong'

import tkinter as tk
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
        self.__last_copied_val = None

        # read data from clipboard
        self.__load_data_from_clipboard()

        # read data from sqllite3
        self.__load_data_from_db()

        self.__load_fixed_data_from_db()

        # init widget
        self.__init_window()

    def __load_data_from_clipboard(self):
        self.__clipboard_data = self.__clipboard.read_clipboard()

    def __load_fixed_data_from_db(self):
        self.__fixed_data = deque(self.__db.read_fixed_clipboard_data(self.__limit))

    def __load_data_from_db(self):
        clipboard_data = self.__db.read_clipboard_data(self.__limit)
        if len(clipboard_data) == 0 and len(self.__clipboard_data) != 0:
            for item in self.__clipboard_data:
                self.__db.write_clipboard_data(item)
            return
        self.__clipboard_data = deque(clipboard_data)

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
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=0, minsize=50)
        for i in range(1, self.__limit + 1):
            root.rowconfigure(i, weight=1)
        self.__init_title(root)
        self.__draw_main_layout(root, self.__clipboard_data, self.__widget_list)
        self.__root = root

    def __init_title(self, root):
        clipboard_title_label = tk.Label(root, text="clipboard", bg="#B2DD3B", relief='solid', borderwidth=1)
        clipboard_title_label.grid(column=0, row=0, sticky=tk.NSEW, padx=0, pady=0, ipadx=5, ipady=5)

        fixed_title_label = tk.Label(root, text="fixed", bg="#B2DD3B", relief='solid', borderwidth=1)
        fixed_title_label.grid(column=1, row=0, sticky=tk.NSEW, padx=0, pady=0, ipadx=5, ipady=5)

        clipboard_title_label.bind('<Enter>', lambda event, widget=fixed_title_label: self.__on_enter_clipboard_title(event, widget))
        fixed_title_label.bind('<Enter>', lambda event, widget=clipboard_title_label: self.__on_enter_fixed_title(event, widget))
    
    def __draw_main_layout(self, root, data, container):
        while len(self.__widget_list) > 0:
            widget = self.__widget_list.pop()
            widget.destroy()
        if len(data) == 0:
            label = tk.Label(root, text='There is Nothing...', bg="#ADD8E6")
            label.grid(column=0, row=1, sticky=tk.NSEW, columnspan=2, rowspan=self.__limit, padx=0, pady=0, ipadx=5, ipady=5)
            container.append(label)
        for i in range(1, len(data) + 1, 1):
            label = None
            id = data[i - 1][0]
            value = data[i - 1][1]
            if i % 2:
                label = tk.Label(root, text=value, bg="#3BB5DD")
            else:
                label = tk.Label(root, text=value, bg="#ADD8E6")
            label.bind('<Enter>', self.__on_enter_label)
            label.bind('<Leave>', lambda event,
                       index=i: self.__on_leave_label(event, index))
            label.bind('<Button-1>', lambda event,
                       id=id: self.__on_click_label(event, id))
            label.id = id
            label.grid(column=0, row=i, sticky=tk.NSEW, columnspan=2, padx=0, pady=0, ipadx=5, ipady=5)
            container.append(label)

    def __on_enter_clipboard_title(self, event, widget):
        event.widget['bg'] = "#94B834"
        widget['bg'] = "#B2DD3B"
        self.__draw_main_layout(self.__root, self.__clipboard_data, self.__widget_list)

    def __on_enter_fixed_title(self, event, widget):
        event.widget['bg'] = "#94B834"
        widget['bg'] = "#B2DD3B"
        self.__draw_main_layout(self.__root, self.__fixed_data, self.__widget_list)

    def __on_enter_label(self, event):
        event.widget['bg'] = "#074155"

    def __on_leave_label(self, event, index):
        if index % 2:
            event.widget['bg'] = '#3BB5DD'
        else:
            event.widget['bg'] = '#ADD8E6'
    
    def __on_click_label(self, event, id):
        logging.info(f'id is {id}')
        val = self.__db.read_blob_data_by_id(id)
        self.__clipboard.write_clipboard(val)
        self.__last_copied_val = val
    
    def __on_text(self, value):
        if self.__last_copied_val and len(self.__last_copied_val) == len(value) and self.__last_copied_val == value:
            return
        self.__last_copied_val = value
        self.__db.write_clipboard_data(value)
        while len(self.__clipboard_data) > 20:
            self.__clipboard_data.popleft()
        self.__clipboard_data.clear()
        self.__clipboard_data = self.__db.read_clipboard_data(self.__limit)
        self.__draw_main_layout(self.__root, self.__clipboard_data, self.__widget_list)


    def __start_listen_clipboard(self):
        clipboard_monitor.on_text(self.__on_text)

    def run(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        finally:
            self.__start_listen_clipboard()
            self.__root.mainloop()
