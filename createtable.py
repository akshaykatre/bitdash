'''
Author: Akshay Katre <akshaykatre@gmail.com> 

This module creates a connection with BitStamp, and creates a 
individual database for each crypto that is listed in 'currencies'.

These tables are further used in app.py 

To do:
  * Automate the list of currencies from the account holder 
  *  
'''

import sqlite3
from bitstamp_trial import trading_client
import pandas 
import numpy 


class cryptocal():
  def __init__(self, dbname, tbname):
    self.dbname = dbname 
    self.tbname = tbname
    self.information_dump()
    self.currencies = ['eth', 'btc', 'snx', 'algo', 'mkr', 'xrp']
    self.individualtables()

  def createtable(self, cname):
    conn = sqlite3.connect(self.dbname)
    with conn:
      conn.execute('DROP TABLE IF EXISTS {cname}'.format(cname=cname))
      conn.execute('''CREATE TABLE {cname}(
          ID INT NOT NULL,
        --  SYMBOL TEXT NOT NULL, 
          STOCKNAME TEXT NOT NULL,
          UNITS REAL NOT NULL,
          PRICE REAL NOT NULL,
          DATE TEXT NOT NULL,
          TRANSACTIONTYPE TEXT NOT NULL)
      '''.format(cname=cname))

    #conn.close()

  def information_dump(self):
    conn = sqlite3.connect(self.dbname)
    with conn:
      df = pandas.DataFrame.from_records(trading_client.user_transactions())
      df.to_sql(self.tbname, conn, if_exists='replace')
      return df

  def individualtables(self):
    print("In individual stocks")
    conn = sqlite3.connect(self.dbname)
    with conn:
      for currency in self.currencies:
        self.createtable(currency)
        query = 'ID, datetime, EUR, {curr}, {curr}_EUR'.format(curr=currency)
        df = pandas.read_sql("SELECT {q} from {table} where {curr} is not null and {curr} != 0.0".format(q=query, table=self.tbname, curr=currency), conn)
        df['TRANSACTIONTYPE'] = numpy.where(df[currency].astype(float) < 0, 'sell', 'buy')
        #print(df)
        df.rename(columns = {currency: 'UNITS', currency+"_eur": 'PRICE', 'datetime': 'DATE'}, inplace=True)
        df['STOCKNAME'] = currency
        df['PRICE'] = df.PRICE.fillna(0)
        #print(" This is itttt", df.PRICE)
        df['UNITS'] = abs(df['UNITS'].astype(float))
        columnstoorder =['ID', 'STOCKNAME', 'UNITS', 'PRICE', 'DATE', 'TRANSACTIONTYPE']
        df = df.reindex(columns=columnstoorder)
        #print(df)
        df.to_sql(currency, conn, if_exists='replace')
        print("Created table for ", currency)

cryptocal('crypto', 'crypinvest')

