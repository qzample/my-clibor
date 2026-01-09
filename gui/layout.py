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
from pystray import Icon, MenuItem, Menu
import keyboard
from PIL import Image
import threading
import time,sys,os,win32gui,win32con

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
    __light_clipbor_color="#ADD8E6"
    __dark_clipbor_color="#3BB5DD"
    __deeper_clipbor_color="#074155"
    __light_fixed_color="#94F58B"
    __dark_fixed_color="#57D34C"
    __deeper_fixed_color="#278A1F"

    __ctrl_count = 0
    __last_ctrl_time = 0

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
                self.__db.write_clipboard_data(item, self.__limit)
        clipboard_data = self.__db.read_clipboard_data(self.__limit)
        self.__clipboard_data = deque(clipboard_data)

    def __resource_path(self, relative_path):
        """获取资源文件路径"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def __init_window(self):
        '''
        init window by tkinter

        :param self: Description
        '''
        bird_ico_path = self.__resource_path('assets/bird.ico')
        self.__tray_icon = Image.open(bird_ico_path).resize((64, 64))
        root = tk.Tk()
        # 默认隐藏到托盘
        root.withdraw()
        root.title('MyClibor')
        root.iconbitmap(bird_ico_path)
        root.geometry(f'{self.__width}x{self.__height}-50-50')
        root.resizable(False, False)
        root.configure(bg='#ADD8E6')
        root.attributes("-topmost", True)
        root.bind("<FocusOut>", lambda event: self.__hide_window(event.widget))
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=0, minsize=30)
        for i in range(1, self.__limit + 1):
            root.rowconfigure(i, weight=1)
        self.__init_title(root)
        self.__draw_main_layout(root, self.__clipboard_data, self.__widget_list, False)
        root.protocol("WM_DELETE_WINDOW", lambda root=root: self.__hide_window(root))
        # self.__setup_hotkey(root)
        self.__icon = self.__setup_tray(root)
        self.__root = root

    def __paste_to_other_app(self):
        windows = []
        def callback(hwnd, extra):
            # 检查窗口是否可见
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                windows.append(hwnd)
        win32gui.EnumWindows(callback, None)
        current_window = win32gui.GetForegroundWindow()
        current_window_index = windows.index(current_window)
        if len(windows) <= 1:
            return
        previous_window = windows[current_window_index + 1]
        win32gui.ShowWindow(previous_window, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(previous_window)
        keyboard.press_and_release("ctrl+v")

    def __setup_tray(self, root):
        menu = Menu(
            MenuItem("show", lambda: self.__show_window(icon, root), default=True),
            MenuItem("exit", lambda: self.__on_stop(icon, root))
        )
        icon = Icon("MyClibor", self.__tray_icon, menu=menu)
        return icon

    def __on_stop(self, icon, root):
        icon.stop()
        root.destroy()

    # def __setup_hotkey(self, root):
    #     # 只能监听按键同时按下
    #     keyboard.add_hotkey("ctrl+m", lambda: self.__show_window(None, root))
    
    def __show_window(self, icon, root):
        root.deiconify()
    
    def __hide_window(self, root):
        root.withdraw()

    def __init_title(self, root):
        clipboard_title_label = tk.Label(root, text="clipboard", bg=self.__deeper_clipbor_color, relief='solid', borderwidth=1)
        clipboard_title_label.grid(column=0, row=0, sticky=tk.NSEW, padx=0, pady=0, ipadx=5, ipady=5)

        fixed_title_label = tk.Label(root, text="fixed phrase", bg=self.__deeper_fixed_color, relief='solid', borderwidth=1)
        fixed_title_label.grid(column=1, row=0, sticky=tk.NSEW, padx=0, pady=0, ipadx=5, ipady=5)

        clipboard_title_label.bind('<Enter>', lambda event, widget=fixed_title_label: self.__on_enter_clipboard_title(event, widget))
        fixed_title_label.bind('<Enter>', lambda event, widget=clipboard_title_label: self.__on_enter_fixed_title(event, widget))
    
    def __draw_main_layout(self, root, data, container, isfixed):
        while len(self.__widget_list) > 0:
            widget = self.__widget_list.pop()
            widget.destroy()
        if len(data) == 0:
            label = tk.Label(root, text='There is Nothing...', bg=self.__light_fixed_color if isfixed else self.__light_clipbor_color)
            label.grid(column=0, row=1, sticky=tk.NSEW, columnspan=2, rowspan=self.__limit, padx=0, pady=0, ipadx=5, ipady=5)
            container.append(label)
        for i in range(1, len(data) + 1, 1):
            label = None
            id = data[i - 1][0]
            value = data[i - 1][1]
            if i % 2:
                label = tk.Label(root, text=value, bg=self.__dark_fixed_color if isfixed else self.__dark_clipbor_color)
            else:
                label = tk.Label(root, text=value, bg=self.__light_fixed_color if isfixed else self.__light_clipbor_color)
            label.bind('<Enter>', lambda event, isfixed=isfixed:self.__on_enter_label(event, isfixed))
            label.bind('<Leave>', lambda event,
                       index=i, isfixed=isfixed: self.__on_leave_label(event, index, isfixed))
            label.bind('<Button-1>', lambda event,
                       id=id, isfixed=isfixed: self.__on_click_label(event, id, isfixed))
            context_menu = tk.Menu(root, tearoff=0)
            if isfixed:
                context_menu.add_command(label="remove from fixed", command=lambda id=id: self.__delete_from_fixed_phrase(id))
            else:
                context_menu.flag=True
                context_menu.add_command(label="add to fixed", command=lambda id=id: self.__save_to_fixed_phrase(id))
            label.bind('<Button-3>', lambda event, context_menu=context_menu: self.__show_context_menu(event, context_menu))
            label.id = id
            label.grid(column=0, row=i, sticky=tk.NSEW, columnspan=2, padx=0, pady=0, ipadx=5, ipady=5)
            container.append(label)
            container.append(context_menu)

    def __show_context_menu(self, event, context_menu):
        if len(self.__fixed_data) >= self.__limit and hasattr(context_menu, "flag"):
            context_menu.entryconfig(0, state="disabled")
        context_menu.post(event.x_root, event.y_root)
    
    def __save_to_fixed_phrase(self, id):
        self.__db.save_clipboard_data_to_fixed(id, self.__limit)
        self.__fixed_data = self.__db.read_fixed_clipboard_data(self.__limit)
    
    def __delete_from_fixed_phrase(self, id):
        self.__db.delete_from_fixed_by_id(id)
        self.__fixed_data = self.__db.read_fixed_clipboard_data(self.__limit)
        self.__draw_main_layout(self.__root, self.__fixed_data, self.__widget_list, True)

    def __on_enter_clipboard_title(self, event, widget):
        event.widget['bg'] = self.__deeper_clipbor_color
        widget['bg'] = self.__dark_fixed_color
        self.__draw_main_layout(self.__root, self.__clipboard_data, self.__widget_list, False)

    def __on_enter_fixed_title(self, event, widget):
        event.widget['bg'] = self.__deeper_fixed_color
        widget['bg'] = self.__dark_clipbor_color
        self.__fixed_data = self.__db.read_fixed_clipboard_data(self.__limit)
        self.__draw_main_layout(self.__root, self.__fixed_data, self.__widget_list, True)

    def __on_enter_label(self, event, isfixed):
        event.widget['bg'] = self.__deeper_fixed_color if isfixed else self.__deeper_clipbor_color

    def __on_leave_label(self, event, index, isfixed):
        if index % 2:
            event.widget['bg'] = self.__dark_fixed_color if isfixed else self.__dark_clipbor_color
        else:
            event.widget['bg'] = self.__light_fixed_color if isfixed else self.__light_clipbor_color
    
    def __on_click_label(self, event, id, isfixed):
        val = self.__db.read_blob_data_by_id(id, isfixed)
        self.__clipboard.write_clipboard(val)
        if not isfixed:
            self.__last_copied_val = val
        self.__paste_to_other_app()
    
    def __on_text(self, value):
        if self.__last_copied_val and len(self.__last_copied_val) == len(value) and self.__last_copied_val == value:
            return
        self.__last_copied_val = value
        self.__db.write_clipboard_data(value, self.__limit)
        while len(self.__clipboard_data) > 20:
            self.__clipboard_data.popleft()
        self.__clipboard_data.clear()
        self.__clipboard_data = self.__db.read_clipboard_data(self.__limit)
        self.__draw_main_layout(self.__root, self.__clipboard_data, self.__widget_list, False)


    def __start_listen_clipboard(self):
        clipboard_monitor.on_text(self.__on_text)

    def __on_ctrl_key(self):
        now = time.time()
        if now - self.__last_ctrl_time > 0.5:
            self.__last_ctrl_time = now
            self.__ctrl_count = 1
            return
        self.__last_ctrl_time = now
        self.__ctrl_count += 1
        if self.__ctrl_count == 3:
            self.__show_window(None, self.__root)
            self.__ctrl_count = 0
            self.__last_ctrl_time = 0
            return

    def run(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        finally:
            self.__start_listen_clipboard()
            # 监听快捷键，连续按下三次ctrl需要自己写逻辑实现
            # 这里监听on_release_key而不是on_press_key，是因为持续按住crtl也会触发
            keyboard.on_release_key("ctrl", lambda _: self.__on_ctrl_key())
            # icon.run是阻塞的，需要单独开个线程
            # 为什么不使用run_detached()，因为执行stop后只是停止了循环，线程还在
            threading.Thread(target=self.__icon.run, daemon=True).start()
            self.__root.mainloop()
