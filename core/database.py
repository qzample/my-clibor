#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' read and write clipboard '

__author__ = 'Zhu XiaoLong'

import sqlite3

class DataBase(object):
    def __init__(self):
        conn = sqlite3.connect('my_clibor.db')
        self.__conn = conn
        self.__init_table()
    
    def read_clipboard_data(self):
        cursor = self.__conn.cursor()
        cursor.execute('''SELECT * FROM clibor_history''')
        values = cursor.fetchall()
        self.__conn.commit()
        cursor.close()
        return [x[1] for x in values]
    
    def write_clipboard_data(self, value):
        cursor = self.__conn.cursor()
        binary_data = value.encode('utf-8')
        cursor.execute('''INSERT INTO clibor_history (value) values(?)''', (binary_data,))
        self.__conn.commit()
        cursor.close()

    def read_fixed_clipboard_data(self):
        cursor = self.__conn.cursor()
        cursor.execute('''SELECT * FROM clibor_fixed_value''')
        values = cursor.fetchall()
        self.__conn.commit()
        cursor.close()
        return [x[1] for x in values]
    
    def __init_table(self):
        cursor = self.__conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS clibor_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        value BLOB)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS clibor_fixed_value (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        value BLOB)''')
        self.__conn.commit()
        cursor.close()
