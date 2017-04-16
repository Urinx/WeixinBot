#!/usr/bin/env python
# coding: utf-8

#===================================================
from config import Log
#---------------------------------------------------
import sqlite3
import threading
import traceback
#===================================================


def _dict_factory(cursor, row):
    aDict = {}
    for iField, field in enumerate (cursor.description):
        aDict [field [0]] = row [iField]
    return aDict


class SqliteDB(object):

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        # use 8-bit strings instead of unicode string
        self.conn.text_factory = str
        # not return a tuple but a dict with column name as key
        self.conn.row_factory = _dict_factory
        # for thread-save
        self.lock = threading.Lock()

    def create_table(self, table, cols):
        """
        @brief      Creates a table in database
        @param      table  String
        @param      cols   String, the cols in table
        """
        sql = "CREATE TABLE if not exists %s (%s);" % (table, cols)
        Log.debug('DB -> %s' % sql)
        self.execute(sql)

    def delete_table(self, table):
        """
        @brief      Delete a table in database
        @param      table  String
        """
        sql = "DROP TABLE if exists %s;" % table
        Log.debug('DB -> %s' % sql)
        self.execute(sql)

    def insert(self, table, value):
        """
        @brief      Insert a row in table
        @param      table  String
        @param      value  Tuple
        """
        sql = ("INSERT INTO %s VALUES (" + ",".join(['?'] * len(value)) + ");") % table
        Log.debug('DB -> %s' % sql)
        self.execute(sql, value)

    def insertmany(self, table, values):
        """
        @brief      Insert many rows in table
        @param      table  String
        @param      values  Array of tuple
        """
        c = self.conn.cursor()
        self.lock.acquire()
        n = len(values[0])
        sql = ("INSERT INTO %s VALUES (" + ",".join(['?'] * n) + ");") % table
        Log.debug('DB -> %s' % sql)

        try:
            c.executemany(sql, values)
        except Exception, e:
            Log.error(traceback.format_exc())
        finally:
            self.lock.release()

        self.conn.commit()

    def select(self, table, field='', condition=''):
        """
        @brief      select all result from table
        @param      table  String
        @param      field  String
        @param      condition  String
        @return     result  Tuple
        """
        result = []
        if field and condition:
            cond = (condition,)
            sql = "SELECT * FROM %s WHERE %s=?" % (table, field)
            Log.debug('DB -> %s' % sql)
            result = self.execute(sql, cond)
        else:
            sql = "SELECT * FROM %s" % table
            Log.debug('DB -> %s' % sql)
            result = self.execute(sql)
        return result

    def update(self, table, dic, condition=''):
        k_arr = []
        v_arr = []
        for (k, v) in dic.items():
            k_arr.append('%s=?' % k)
            v_arr.append(v)

        sql = "UPDATE %s SET %s" % (table, ','.join(k_arr))
        if condition:
            sql += " WHERE %s" % condition

        Log.debug('DB -> %s' % sql)
        self.execute(sql, tuple(v_arr))

    def get_table_column_name(self, table):
        """
        @brief      select all result from table
        @param      table  String
        @return     result  Array
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM %s" % table)
        names = list(map(lambda x: x[0], c.description))
        return names

    def execute(self, sql, value=None):
        """
        @brief      execute sql commands, return result if it has
        @param      sql  String
        @param      value  Tuple
        @return     result  Array
        """
        c = self.conn.cursor()
        self.lock.acquire()
        hasReturn = sql.lstrip().upper().startswith("SELECT")

        try:
            if value:
                c.execute(sql, value)
            else:
                c.execute(sql)

            if hasReturn:
                result = c.fetchall()
        except Exception, e:
            Log.error(traceback.format_exc())
        finally:
            self.lock.release()

        self.conn.commit()

        if hasReturn:
            return result

    def delete(self, table, field='', condition=''):
        """
        @brief      execute sql commands, return result if it has
        @param      table  String
        @param      field  String
        @param      condition  String
        """
        sql = "DELETE FROM %s WHERE %s=?" % (table, field)
        Log.debug('DB -> %s' % sql)
        cond = (condition,)
        self.execute(sql, cond)

    def close(self):
        """
        @brief      close connection to database
        """
        Log.debug('DB -> close')
        self.conn.close()
