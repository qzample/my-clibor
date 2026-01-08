#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' read and write clipboard '

__author__ = 'Zhu XiaoLong'

import sqlite3

class DataBase(object):
    def __init__(self):
        conn = sqlite3.connect('my_clibor.db', check_same_thread=False)
        self.__conn = conn
        self.__init_table()
    
    def read_clipboard_data(self, limit):
        cursor = self.__conn.cursor()
        cursor.execute('''SELECT * FROM clibor_history order by id desc limit (?) ''', (limit,))
        rows = cursor.fetchall()
        cursor.close()
        res_tuple_list = []
        for row in rows:
            res_tuple = (row[0], self.trim_value(row[1].decode('utf-8')))
            res_tuple_list.append(res_tuple)
        return res_tuple_list
    
    def write_clipboard_data(self, value, limit):
        cursor = self.__conn.cursor()
        binary_data = value.encode('utf-8')
        cursor.execute('''DELETE FROM clibor_history WHERE ID NOT IN (SELECT ID FROM clibor_history ORDER BY ID desc limit (?))''', (limit,))
        cursor.execute('''INSERT INTO clibor_history (value) values(?)''', (binary_data,))
        id = cursor.lastrowid
        self.__conn.commit()
        cursor.close()
        return id

    def read_fixed_clipboard_data(self, limit):
        cursor = self.__conn.cursor()
        cursor.execute('''SELECT * FROM clibor_fixed_value order by id asc limit (?)''', (limit,))
        rows = cursor.fetchall()
        cursor.close()
        res_tuple_list = []
        for row in rows:
            res_tuple = (row[0], self.trim_value(row[1].decode('utf-8')))
            res_tuple_list.append(res_tuple)
        return res_tuple_list
    
    def read_blob_data_by_id(self, id):
        cursor = self.__conn.cursor()
        cursor.execute('''SELECT value FROM clibor_history where id = (?)''', (id,))
        value = cursor.fetchall()
        cursor.close()
        return value[0][0].decode('utf-8')
    
    def save_clipboard_data_to_fixed(self, id):
        cursor = self.__conn.cursor()
        cursor.execute('''SELECT value FROM clibor_history where id = (?)''', (id,))
        value = cursor.fetchall()
        cursor.execute('''INSERT INTO clibor_fixed_value (value) values(?) ''', (value[0][0],))
        id = cursor.lastrowid
        self.__conn.commit()
        cursor.close()
        return id
    
    def delete_from_fixed_by_id(self, id):
        cursor = self.__conn.cursor()
        cursor.execute('''DELETE FROM clibor_fixed_value where id = (?)''', (id,))
        self.__conn.commit()
        cursor.close()
    
    def trim_value(self, value):
        val = repr(value)
        return val[:20] + "..." if len(val) > 20 else val
    
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
