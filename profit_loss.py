'''
Author: Akshay Katre <akshaykatre@gmail.com> 

This module is used by app.py to get the data from the local sqlite 
databases where the crypto transaction information of the tradingclient 
is stored. It performs PNL based on the FIFO (First In First Out) Principle
and returns profit/loss, current investment as requested in app.py


To do:
  * Automate the list of currencies from the account holder 

'''

import sqlite3
import pandas 

class PNL():
    def __init__(self, dbname, tbname, stname):
        self.stockname = stname
        self.dbname = dbname
        self.tbname = tbname

        #cryptocal.__init__(self, dbname,tbname)

        self.tradedf, self.bought, self.sold = self.stocksale()
        self.profitloss, self.investment = self.profit_loss(self.bought, self.sold)


    def stockslist(self, bought_df, transaction):
      '''
      Return a list of quantity and price at which a commodity was bought/ sold
      ''' 
      #print("In stocklist", transaction, bought_df)
      st_bought = bought_df.where(bought_df.TRANSACTIONTYPE==transaction).dropna(how='all')

      bought = []
      for stb in st_bought.iterrows():
          bought.append([stb[1].UNITS, stb[1].PRICE])
      
      return bought

    def profit_loss(self, bought_stks, sale_stks):
        ''' 
        The calculations need to happen at a certain point in time (after all 
        sales and purchases have taken place). It is only important 
        to calculate the profit and loss at very end. 

        ''' 
        ## The total number of stocks to be sold
        #print(sale_stks)
        tobesold = sum(x[0] for x in sale_stks)
        costprice = 0
        #investment = 0 
        for idx, stks in enumerate(bought_stks):
            ## The number to sell is the minimum between the total number to 
            ## sell, or those available at a particular purchase price
            sell = min(tobesold, stks[0])
            ## The remaining number of stocks (after above sale) to be sold is 
            ## the difference between the total and sold stocks; floored at 0 
           # remainder = lambda tbs, s: 0 if tbs-s < 0 else tbs-s 

            tobesold = tobesold - sell #remainder(tobesold, sell)
            ## The cumulative cost of the stocks that are being sold 
            costprice += stks[1] * sell 

            #print("\n\n", bought_stks,  stks, tobesold, costprice)
            ## Once all the sold stocks are depleted, we can quit the loop
            if tobesold <= 0:
                break

              ## Get the current investment still in the instrument
        #print("tobesold: ", tobesold)
        investment = (stks[0]-sell) * stks[1] 
        try:
          #start = idx if (tobesold == 0 and idx!=len(bought_stks)) else idx + 1 
          for remain in bought_stks[idx+1:]:
            investment += remain[0] * remain[1]
        except:
          pass  

        saleprice = sum([nstks*salesprice for nstks,salesprice in sale_stks])

        ## This is the profit/ loss (loss is negative)
        return saleprice - costprice, investment


    def stocksale(self):
        conn = sqlite3.connect(self.dbname)
        with conn:
            query = "SELECT * from {table} where stockname like '%{stname}%' order by DATE".format(table=self.stockname, stname=self.stockname)
            ## Get dataframe for a stock 
            df = pandas.read_sql_query(query, conn)

        bought = self.stockslist(df, 'buy')
        sold = self.stockslist(df, 'sell') 
        return df, bought, sold 

