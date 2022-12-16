import psycopg2
import pandas as pd
import os
import numpy as np
from datetime import date, datetime, timedelta
import time
import asimov_database as ad

class Updater:
    def __init__(self):
        self.today = date.today().strftime("%Y-%m-%d %H:%M:%S")
        self.yesterday = ((date.today() - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")) 
        self.parquet = ad.ParquetCreator()

    def _load_postgres_data_for_incremental(self, db = 'md_rt'):
        self.parquet._create_sql_connection(database=db)
    
        string_inc = "SELECT distinct symbol, EXTRACT(year FROM ts) as year_, EXTRACT(month FROM ts)*100 + EXTRACT(day FROM ts) as month_ FROM {} WHERE ts between '{}' AND '{}'".format('md_incremental', self.yesterday, self.today)   
        df_incremental = pd.read_sql_query(string_inc, self.parquet.conn)
        # df_incremental = df_incremental [ (df_incremental['symbol'].str.contains('DOL')) | ( df_incremental['symbol'].str.contains('WDO') ) ]
        # df_incremental = df_incremental [ (df_incremental['symbol'].str.len() == 6) ]
        df_incremental['inc'] = 'incremental' 

        
        string_snap = "SELECT distinct symbol, EXTRACT(year FROM ts) as year_, EXTRACT(month FROM ts)*100 + EXTRACT(day FROM ts) as month_ FROM {} WHERE ts between '{}' AND '{}'".format('md_snapshot', self.yesterday, self.today)
        df_snapshot = pd.read_sql_query(string_snap, self.parquet.conn)
        df_snapshot['inc'] = 'snapshot'

        df_total = pd.concat([df_incremental, df_snapshot])

        return df_total

    def _load_postgres_data_for_trades(self, db = 'md_rt'):    
        self.parquet._create_sql_connection(database=db)

        string_trade = "SELECT distinct symbol, EXTRACT(year FROM ts) as year_, EXTRACT(month FROM ts)*100 + EXTRACT(day FROM ts) as month_ FROM {} WHERE ts between '{}' AND '{}'".format('md_trade', self.yesterday, self.today)
        df_trade = pd.read_sql_query(string_trade, self.parquet.conn)
    
        df_trade['Day'] = df_trade.month_ % 100
        df_trade['Month'] = (df_trade.month_ // 100)
        df_trade['Year'] = df_trade['year_'].astype(int)
        df_trade['Month'] =df_trade['Month'].astype(int)
        df_trade['Day'] =df_trade['Day'].astype(int)
        df_trade['Month'] =df_trade['Month'].astype(str)
        df_trade['Year'] = df_trade['Year'].astype(str)
        df_trade['Day'] =df_trade['Day'].astype(str)
        df_trade['Day'] = df_trade['Day'].apply(lambda x: '{0:0>2}'.format(x))
        df_trade['Month'] = df_trade['Month'].apply(lambda x: '{0:0>2}'.format(x))
        df_trade['title'] = df_trade.symbol + '-'  + df_trade.Year + '-'+ df_trade.Month + '-' +  df_trade.Day
        df_trade  = df_trade.drop(columns=['Day', 'Month', 'symbol', 'month_', 'Year', 'year_'])

        return df_trade

    def _load_postgres_data_for_mirror(self, db = 'asimov_mirror'):
        self.parquet._create_sql_connection(database=db)

        date_b = str(date.today() - timedelta(days=26))
        date_a = str(date.today())

        since = int(datetime.strptime(date_b, "%Y-%m-%d").strftime("%s")) * (1000 ** 3)
        until = (int(datetime.strptime(date_a, "%Y-%m-%d").strftime("%s")) + 24 * 60 * 60) * (1000 ** 3)

        string_mirror = "SELECT * FROM {} WHERE ts between '{}' AND '{}'".format('order_mirror', since, until)
        mirror = pd.read_sql_query(string_mirror, self.parquet.conn)
        mirror['timestamp'] = mirror['ts'].apply(lambda x : pd.to_datetime(x, format = "%Y-%m-%d"))
        df = pd.DataFrame()
        df['title'] = mirror['timestamp'].dt.date.unique()

        return df
        
    def _cleanser_for_inc(self, db = 'md_rt'):     
        df_final = self._load_postgres_data_for_incremental(db=db)

        df_final['Day'] = df_final.month_ % 100
        df_final['Month'] = (df_final.month_ // 100)
        df_final['Year'] = df_final['year_'].astype(int)
        df_final['Month'] =df_final['Month'].astype(int)
        df_final['Day'] =df_final['Day'].astype(int)
        df_final['Month'] =df_final['Month'].astype(str)
        df_final['Year'] = df_final['Year'].astype(str)
        df_final['Day'] =df_final['Day'].astype(str)
        df_final['Day'] = df_final['Day'].apply(lambda x: '{0:0>2}'.format(x))
        df_final['Month'] = df_final['Month'].apply(lambda x: '{0:0>2}'.format(x))
        df_final['title'] = df_final.symbol + '-' + df_final.inc + '-' + df_final.Year + '-'+ df_final.Month + '-' +  df_final.Day
        df_final  = df_final.drop(columns=['Day', 'Month', 'symbol', 'month_', 'inc', 'Year', 'year_'])
    
        return df_final

    def append_to_file(self, db = 'md_rt'):
        start_path = os.getenv("HOME") + '/bigdata/database' if os.path.isdir(os.getenv("HOME") + '/bigdata') else '/bigdata/database'
        os.chdir(start_path)
        
        df_historical_inc = pd.read_csv("allsymbols.csv", sep = ',')
        df_historical_trade = pd.read_csv("alltrades.csv", sep = ',')
        df_historical_mirror = pd.read_csv("mirrorfiles.csv", sep = ',')

        df_new_trade = self._load_postgres_data_for_trades(db = db)
        df_new_inc  = self._cleanser_for_inc(db = db)
        df_new_mirror = self._load_postgres_data_for_mirror(db = 'asimov_mirror')

        df_uptaded_trade = pd.concat([df_historical_trade, df_new_trade]).drop_duplicates(subset ="title", keep = 'first')
        df_uptaded_inc = pd.concat([df_historical_inc, df_new_inc]).drop_duplicates(subset ="title", keep = 'first')
        df_uptaded_mirror = pd.concat([df_historical_mirror, df_new_mirror]).drop_duplicates(subset ="title", keep = 'first')

             
        df_uptaded_inc.to_csv('allsymbols.csv', sep = ',', header = True, index = False)
        df_uptaded_trade.to_csv('alltrades.csv', sep = ',', header = True, index = False)
        df_uptaded_mirror.to_csv('mirrorfiles.csv', sep = ',', header = True, index = False)


if __name__ == '__main__':
    #from asimov_database import Uptader
    update = Updater()                               
    update.append_to_file()

