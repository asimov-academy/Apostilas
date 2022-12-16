import pandas as pd
import numpy as np
import gc
import pyarrow.parquet as pq
from datetime import datetime, timedelta
import pytz
import os
import re
import shutil

from asimov_tools.simplifiers.memory_optimizer import optimize_objects
from asimov_tools.simplifiers.supplement import BusinessDay, NextActive

from .parquet_creator import ParquetCreator



class ParquetReader:
    def __init__(self, connection_settings={}):
        self.RAM_AVAILABLE = 12
        self.creator = ParquetCreator(connection_settings=connection_settings)
        self.paths = self.creator._get_paths()
        self.files = {}

    def list_files(self, local=False, relist_files=True):
        if relist_files or not local in self.files:
            if local:
                root_path = self.paths['LOCAL']
            else:
                root_path = self.paths['MOUNTED']
            dict_files = {}
            dict_files['order-book'] = os.listdir(root_path + '/order-book') if os.path.isdir(root_path + '/order-book') else []
            dict_files['simple-level-book'] = os.listdir(root_path + '/simple-level-book') if os.path.isdir(root_path + '/simple-level-book') else []
            dict_files['level-book'] = os.listdir(root_path + '/level-book') if os.path.isdir(root_path + '/level-book') else []
            dict_files['trades'] = os.listdir(root_path + '/trades') if os.path.isdir(root_path + '/trades') else []
            dict_files['events'] = os.listdir(root_path + '/events') if os.path.isdir(root_path + '/events') else []
            dict_files['mirror'] = os.listdir(root_path + '/mirror') if os.path.isdir(root_path + '/mirror') else []
            dict_files['logs'] = os.listdir(root_path + '/logs') if os.path.isdir(root_path + '/logs') else []
            dict_files['ibov-composition'] = os.listdir(root_path + '/ibov/composition') if os.path.isdir(root_path + '/ibov/composition') else []
            self.files[local] = dict_files
        return self.files[local]
    
    def missing_files(self, source, symbol=None, days=20, local=False, relist_files=False):

        bd = BusinessDay()
        na = NextActive()

        if source in ['simple-level-book', 'trades', 'events'] and symbol is None:
            print(' [ DATABASE ] Must pass a valid symbol for source {}'.format(source))
            return

        files = self.list_files(local=local, relist_files=relist_files)
        if not source in files:
            print(' [ DATABASE ] Source not found! Possible sources {}'.format(list(files.keys())))
            return
        files = files[source]

        if relist_files or not '{}_per-date'.format(source) in self.files[local]:
            date_pattern = "(([12]\d{3})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))"
            files_per_date = {}
            for f in files:
                date = re.findall(date_pattern, f)
                if len(date) > 0:
                    list_of_files = files_per_date.setdefault(date[0][0], [])
                    list_of_files += [f]
            self.files[local]['{}_per-date'.format(source)] = files_per_date
        files_per_date = self.files[local]['{}_per-date'.format(source)]

        dates = bd.previous_business_days(datetime.now().strftime('%Y-%m-%d'), count=days)
        symbols = [na.next_active(date, symbol) for date in dates]


        missing_dates = []
        for i, date in enumerate(dates):
            symbol = symbols[i]
            
            ok = False
            for f in files_per_date.get(date, []):
                if source == 'events':
                    if 'incremental' in f and f.split('-')[0] == symbol:
                        ok = True
                        break
                elif source in ['trades', 'simple-level-book']:
                    if f.split('-')[0] == symbol:
                        ok = True
                        break
                elif source in ['mirror', 'logs', 'ibov-composition']:
                    if symbol is None or symbol in f:
                        ok = True
                        break
                else:
                    print(' [ DATABASE ] Method not inmplemented for source {}'.format(source))
            if not ok:
                missing_dates += [date]
        
        return missing_dates

    def file_info(self, symbol, date, type_='events'):
        
        file = self.get_parquet(symbol, date, type_=type_)
        if type_ == 'trades':
            data = file.read(columns=["msg_seq_num"], use_pandas_metadata=True).to_pandas()
        else:
            data = file['incremental'].read(columns=["msg_seq_num", "event_type"], use_pandas_metadata=True).to_pandas()
            data = data[~data['event_type'].isin(['STARTED', 'STATUS', 'DELETE_THRU', 'DELETE'])]
        data['diff_ts'] = data.index
        data['diff_ts'] = data['diff_ts'].diff()

        sp = pytz.timezone('America/Sao_Paulo')
        utc = pytz.timezone('UTC')

        if symbol[:3] in ['DOL', 'IND', 'WDO', 'WIN']:
            initial_time = sp.localize((datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=8, minutes=55))).astimezone(utc)
            end_time = sp.localize((datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=18, minutes=0))).astimezone(utc)
        else:
            initial_time = sp.localize((datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=9, minutes=45))).astimezone(utc)
            end_time = sp.localize((datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=18, minutes=0))).astimezone(utc)


        info = {'max_delta_ts': data['diff_ts'].max().total_seconds(),
                'starting_ts': data.index.min(),
                'ending_ts': data.index.max(),
                'starting_ts_diff': (initial_time - data.index.min()).total_seconds(),
                'ending_ts_diff': (data.index.max() - end_time).total_seconds()}
        return info


    def get_available_dates(self, source='events', filter_symbol=None):
        files = self.list_files()[source]
        files = [f.split('/')[-1].replace('.parquet', '') for f in files]
        dict_symbol_per_date = {}

        for file in files:
            symbol = file.split("-")[0]
            if symbol not in dict_symbol_per_date:
                dict_symbol_per_date[symbol] = [file]
            else:
                dict_symbol_per_date[symbol] += [file]

        all_symbols = list(dict_symbol_per_date.keys())
        for symbol in all_symbols:
            if filter_symbol == None or filter_symbol in symbol:
                dict_symbol_per_date[symbol] = [f.split('-') for f in dict_symbol_per_date[symbol]]
                dict_symbol_per_date[symbol] = list(set(['{}-{}-{}'.format(d[-3], d[-2], d[-1]) for d in dict_symbol_per_date[symbol]]))
                dict_symbol_per_date[symbol].sort()
            else:
                del dict_symbol_per_date[symbol] 
        return dict_symbol_per_date

    def _read_parquet_file(self, path):
        if os.path.isfile(self.paths['LOCAL'] + path):
            return pq.ParquetFile(self.paths['LOCAL'] + path)
        elif os.path.isfile(self.paths['MOUNTED'] + path):
            try:
                return pq.ParquetFile(self.paths['MOUNTED'] + path)
            except Exception as e:
                print("Error: {} on {}".format(e, path))
        else:
            print('File not found: ' + self.paths['MOUNTED'] + path)
    
    def _read_csv_file(self, path):
        if os.path.isfile(self.paths['LOCAL'] + path):
            return pd.read_csv(self.paths['LOCAL'] + path)
        elif os.path.isfile(self.paths['MOUNTED'] + path):
            try:
                return pd.read_csv(self.paths['LOCAL'] + path)
            except Exception as e:
                print("Error: {} on {}".format(e, path))
        else:
            print('File not found: ' + self.paths['MOUNTED'] + path)

    def _str_datetime_to_timestamp(self, x):
        try:
            if isinstance(x, str):
                a = x.split('.')
                if len(a) == 2:
                    b = a[0].split(':')
                    return int(a[1][:3]) + (int(b[0]) * 60 * 60 + int(b[1]) * 60 + int(b[2])) * 1000
                else:
                    b = a[0].split(':')
                    return (int(b[0]) * 60 * 60 + int(b[1]) * 60 + int(b[2])) * 1000
            else:
                return x.microsecond / 1000 + (x.second + x.minute * 60 + x.hour * 60 * 60) * 1000
        except:
            return np.nan

    def copy_file_to_local(self, date, symbol=None, type_=None):
        if type_ == 'mirror':
            path = '/mirror/{}.parquet'.format(date)
            shutil.copy2(self.paths['MOUNTED'] + path, self.paths['LOCAL'] + path)
            path = '/mirror/{}_processed.parquet'.format(date)
            shutil.copy2(self.paths['MOUNTED'] + path, self.paths['LOCAL'] + path)
        if type_ == 'trades':
            path = '/trades/' + "{}-{}.parquet".format(symbol, date)
            shutil.copy2(self.paths['MOUNTED'] + path, self.paths['LOCAL'] + path)
        if type_ == 'events':
            path = '/events/' + "{}-incremental-{}.parquet".format(symbol, date)
            shutil.copy2(self.paths['MOUNTED'] + path, self.paths['LOCAL'] + path)
            path = '/events/' + "{}-snapshot-{}.parquet".format(symbol, date)
            shutil.copy2(self.paths['MOUNTED'] + path, self.paths['LOCAL'] + path)

    # Reader
    def get_marketdata_from_postgres(self, table, symbol, date, next_date=None, db='md_rt'):
        if table == 'incremental':
            return self.creator._load_postgres_data_for_incremental(symbol, date, next_date, db)
        elif table == 'trades':
            return self.creator._load_postgres_data_for_trades(symbol, date, next_date, db)
        return None
    
    def get_account_data_from_postgres(self, date,  next_date=None, load_test_symbol=True, new_mirror=True):
        if len(date) == 10:
            date += ' 00:00:00'
        # if new_mirror:
            # date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            # next_date = date + timedelta(days=1)
        # else:
        date = int(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%s")) * 1000 * 1000 * 1000
        if next_date is not None:
            if len(next_date) == 10:
                next_date += ' 00:00:00'
            next_date = int(datetime.strptime(next_date, "%Y-%m-%d %H:%M:%S").strftime("%s")) * 1000 * 1000 * 1000

        return self.creator._load_order_mirror_data(date, next_date, load_test_symbol=load_test_symbol, new_mirror=new_mirror)

    def get_account_data_from_parquet(self, date, processed=None):
        path = '/mirror/{}_processed.parquet'.format(date) if processed else '/mirror/{}.parquet'.format(date)
        return self._read_parquet_file(path)

    def get_mirror_parquet(self, date, load_test_symbol=False):
        if load_test_symbol:
            path = '/mirror/{}_complete.parquet'.format(date)
            file = self._read_parquet_file(path)
            if not file is None:
                return file
        path = '/mirror/{}_processed.parquet'.format(date)
        file = self._read_parquet_file(path)
        if not file is None:
            return file
        path = '/mirror/{}.parquet'.format(date)
        return self._read_parquet_file(path)

    def get_parquet(self, symbol, date, type_='events'):
        type_ = '/' + type_ + '/'

        if type_ == '/trades/':
            path = type_ + "{}-{}.parquet".format(symbol, date)
            return self._read_parquet_file(path)

        elif type_ == '/events/':
            dict_data = {}
            incremental_file = type_ + "{}-incremental-{}.parquet".format(symbol, date)
            snapshot_file = type_ + "{}-snapshot-{}.parquet".format(symbol, date)
            dict_data['incremental'] = self._read_parquet_file(incremental_file)
            dict_data['snapshot'] = self._read_parquet_file(snapshot_file)
            return dict_data

        elif '/order-book/' in type_ or '/level-book/' in type_:
            dict_data = {}
            for side in ['bid', 'ask']:
                price_file = "{}-price-{}-{}.parquet".format(symbol, side, date)
                quantity_file = "{}-quantity-{}-{}.parquet".format(symbol, side, date)
                broker_file = "{}-broker-{}-{}.parquet".format(symbol, side, date)
                inc_code_file = "{}-inc_code-{}-{}.parquet".format(symbol, side, date)
                order_id_file = "{}-order_id-{}-{}.parquet".format(symbol, side, date)
                level_len_file = "{}-level_len-{}-{}.parquet".format(symbol, side, date)
                dict_data['{}_price'.format(side)] = self._read_parquet_file(type_ + price_file)
                dict_data['{}_quantity'.format(side)] = self._read_parquet_file(type_ + quantity_file)
                dict_data['{}_broker'.format(side)] = self._read_parquet_file(type_ + broker_file)
                dict_data['{}_inc_code'.format(side)] = self._read_parquet_file('/order-book/' + inc_code_file)
                dict_data['{}_order_id'.format(side)] = self._read_parquet_file('/order-book/' + order_id_file)
                dict_data['{}_level_len'.format(side)] = self._read_parquet_file('/level-book/' + level_len_file)
            return dict_data
        
        elif '/simple-level-book/' in type_:
            dict_data = {}
            for side in ['bid', 'ask']:
                price_file = "{}-price-{}-{}.parquet".format(symbol, side, date)
                quantity_file = "{}-quantity-{}-{}.parquet".format(symbol, side, date)
                level_len_file = "{}-level_len-{}-{}.parquet".format(symbol, side, date)
                dict_data['{}_price'.format(side)] = self._read_parquet_file(type_ + price_file)
                dict_data['{}_quantity'.format(side)] = self._read_parquet_file(type_ + quantity_file)
                dict_data['{}_level_len'.format(side)] = self._read_parquet_file(type_ + level_len_file)
            return dict_data
        else:
            print('{} type not understood.'.format(type_))

    def _fetch_single_simple_level(self, symb, date, depth):
        raw_data = self.get_parquet(symb, date, "simple-level-book")
        for side in ["bid", "ask"]:
            read_columns = [side + "_{}".format(i) for i in range(depth)]
            raw_data[side + "_price"] = raw_data[side + "_price"].read(columns=read_columns + ["msg_seq_num", "notify"], use_pandas_metadata=True).to_pandas().reset_index()
            raw_data[side + "_quantity"] = raw_data[side + "_quantity"].read(columns=read_columns).to_pandas()
            raw_data[side + "_level_len"] = raw_data[side + "_level_len"].read(columns=read_columns).to_pandas()

            raw_data[side + "_price"][read_columns] = raw_data[side + "_price"][read_columns].astype(np.float32)
            raw_data[side + "_quantity"][read_columns] = raw_data[side + "_quantity"][read_columns].astype(np.float32)
            raw_data[side + "_level_len"][read_columns] = raw_data[side + "_level_len"][read_columns].astype(np.float32)
    
        level_data = raw_data["bid_price"].copy()
        level_data = level_data.join(raw_data["bid_quantity"].rename(columns={i: "quantity_"+ i for i in raw_data["bid_quantity"].columns}), how="outer")
        level_data = level_data.join(raw_data["bid_level_len"].rename(columns={i: "level_len_"+ i for i in raw_data["bid_level_len"].columns}), how="outer")

        del raw_data["ask_price"]["msg_seq_num"], raw_data["ask_price"]["index"], raw_data["ask_price"]["notify"]
        level_data = level_data.join(raw_data["ask_price"], how="outer")
        level_data = level_data.join(raw_data["ask_quantity"].rename(columns={i: "quantity_"+ i for i in raw_data["ask_quantity"].columns}), how="outer")
        level_data = level_data.join(raw_data["ask_level_len"].rename(columns={i: "level_len_"+ i for i in raw_data["ask_level_len"].columns}), how="outer")
        level_data = level_data.set_index("index")
        return level_data

    def get_simple_level_data(self, symbols, date, depth=5, order_by="msg_seq_num", split_events=True, overwrite=False, add_suffix=False):
        from asimov_tools.simplifiers.supplement import NextActive
        import asimov_tools as at
        import gc
        from asimov_simulator.modules.message_utils import status, event_type
        na = NextActive()
        
        symbols = [symbols] if isinstance(symbols, str) else symbols
        dict_status = status
        dict_event_type = event_type
        dict_symbol = {na.next_active(date, j): i for i, j in enumerate(symbols)}

        dict_reference = {"symbols": symbols,
                        "date": date,
                        "depth": depth, 
                        "order_by": order_by}
        
        write = True
        pm = at.ParquetManager("level_data")

        if pm.isin(dict_reference) and not overwrite:
            print("[ PARQUET READER ] Reading level_data using ParquetManager.")
            try:
                return_data = pm.read(dict_reference)
                events_columns = ['price_trade', 'quantity_trade', 'buyer', 'seller', 'event_type', 'side', 'position', 
                                'order_id', 'broker', 'price_event', 'quantity_event', 'status', 'symbol', 'msg_seq_num', "id"]
                if order_by == "ts":
                    events_columns += ["ts"]
                write = False
            except Exception as e:
                print("[ PARQUET READER ] Error reading level data", e)
                write = True

        if write:
            print("[ PARQUET READER ] Data from {} not created yet. Working on.".format(date))
            dict_level_data = {}

            for symb in symbols:
                ticker = na.next_active(date, symb)
                dict_level_data[symb] = self._fetch_single_simple_level(ticker, date, depth)

                df_incremental = self.get_parquet(ticker, date, "events")["incremental"].read().to_pandas().sort_values(by="id")
                df_incremental.loc[df_incremental["status"].isin(["None", "nan"]), "status"] = np.nan
                df_incremental["status"] = df_incremental["status"].ffill()
                df_incremental.loc[df_incremental["side"] == "B", "side"] = 0
                df_incremental.loc[df_incremental["side"] == "A", "side"] = 1
                df_trades = self.get_parquet(ticker, date, "trades").read().to_pandas().sort_values(by="trade_id")
                df_trades = df_trades[(~df_trades["rlp"]) & (~df_trades["crossed"])]

                ignore_msn = df_incremental[df_incremental["event_type"].isin(["STARTED", "STATUS"])]["msg_seq_num"]
                df_trades = df_trades[~df_trades["msg_seq_num"].isin(ignore_msn)]
                df_incremental = df_incremental[~df_incremental["msg_seq_num"].isin(ignore_msn)]
                dict_level_data[symb] = dict_level_data[symb][~dict_level_data[symb]["msg_seq_num"].isin(ignore_msn)]
                df_incremental["side"] = df_incremental["side"].astype(np.int)

                trade_columns = ["msg_seq_num", "price", "quantity", "buyer", "seller", "event_type", "id"]
                inc_columns = ["msg_seq_num", "event_type", "side", "position", "order_id", "broker", "price", "quantity", "status", "id"]
                if order_by == "ts":
                    trade_columns += ["trade_ts"]
                    inc_columns += ["order_ts"]
                if 'id' in df_trades:
                    del df_trades['id']
                df_trades = df_trades.rename(columns={"trade_id": "id"})
                df_trades["event_type"] = "TRADE"
                suff = ("_trade", "_event")

                df_events = df_trades[trade_columns].reset_index().merge(df_incremental[inc_columns].reset_index(), on=["msg_seq_num", "event_type", "ts", "id"], how="outer", suffixes=suff).sort_values(by="msg_seq_num", kind="mergesort").reset_index()
                df_events["status"] = df_events["status"].ffill()

                df_events_join = df_events.loc[:, ~df_events.columns.isin(["ts", "msg_seq_num", "index"])].copy()
                events_columns = df_events_join.columns.tolist() + ["symbol", "msg_seq_num"]
                del df_trades, df_incremental, df_events
                gc.collect()
                
                if order_by == "ts":
                    df_events_join["ts"] = df_events_join["order_ts"]
                    df_events_join["ts"][df_events_join["ts"].isna()] = df_events_join["trade_ts"][df_events_join["ts"].isna()]
                    df_events_join["ts"] = df_events_join["ts"].apply(lambda x: self._str_datetime_to_timestamp(x))
                    df_events_join.loc[(df_events_join["ts"] - df_events_join["ts"].cummax()) < 0, "ts"] = np.nan
                    df_events_join["ts"] = df_events_join["ts"].ffill()
                    
                    df_events_join.loc[df_events_join["ts"].diff() < 0, "ts"] = np.nan
                    df_events_join["ts"] = df_events_join["ts"].ffill()
                    events_columns += ["ts"]
                    del df_events_join["trade_ts"], df_events_join["order_ts"]
                    events_columns.remove("trade_ts")
                    events_columns.remove("order_ts")
                
                dict_level_data[symb] = dict_level_data[symb].reset_index().join(df_events_join)#.set_index("index")
                dict_level_data[symb]["symbol"] = ticker
                dict_level_data[symb]["event_type"] = dict_level_data[symb]["event_type"].map(dict_event_type).astype(np.int16)
                dict_level_data[symb]["status"] = dict_level_data[symb]["status"].fillna(value='None').map(dict_status).astype(np.int16)
                dict_level_data[symb]["symbol"] = dict_level_data[symb]["symbol"].map(dict_symbol).astype(np.int16)
                dict_level_data[symb]["notify"] = dict_level_data[symb]["notify"].astype(bool)
                dict_level_data[symb]["i"] = np.arange(dict_level_data[symb].shape[0])     
            
            # Join if multiple symbols required
            if len(symbols) > 1:
                first_symb = symbols[0]
                for symb in symbols[1:]:
                    suff = ("_" + first_symb, "_" + symb)
                    merge_events = [i for i in events_columns if i != "status"]
                    
                    dict_level_data[first_symb] = dict_level_data[first_symb].merge(dict_level_data[symb], 
                                on=["index", "msg_seq_num", "notify", "i"]+ merge_events, how="outer", suffixes=suff)
                    del dict_level_data[symb]
                    gc.collect()
                    
                order_by = [order_by, "i"]
                return_data = dict_level_data[first_symb].sort_values(by=order_by).set_index("index")

                # Optimizing columns
                return_data["notify"] = return_data["notify"].astype(bool)
                # for col in merge_events:
                    # return_data[col] = pd.to_numeric(return_data[col], downcast="float")
                    
            elif len(symbols) == 1:
                return_data = dict_level_data[symbols[0]].set_index("index")
            print("[ PARQUET READER ] Saving level_data using ParquetManager.")

            del dict_level_data
            gc.collect()
            pm.write(dict_reference, return_data)

        events_columns.remove("status")

        if  len(symbols) == 1 and add_suffix:
            columns = [c if c in events_columns + ['notify', 'i'] else '{}_{}'.format(c, symbols[0]) for c in return_data.columns]
            return_data.columns = columns

        return_data.loc[:, ~return_data.columns.isin(events_columns)] = return_data.loc[:, ~return_data.columns.isin(events_columns)].ffill()
        if split_events:
            return_data = {"events": return_data[events_columns], "level_data":  return_data.loc[:, ~return_data.columns.isin(events_columns)]}  
        return return_data, {"status":dict_status, "event_type": event_type, "symbols": dict_symbol}


        # dict_level_data[symb] = dict_level_data[symb].rename(columns={i: symb + "_" + i for i in dict_level_data[symb]})
    
    def decrease_memory_consumption(self, df, type_):
        if type_ == 'incremental' or type_ == 'snapshot':
            # del df['order_ts']
            df = optimize_objects(df, ['order_ts'])
        if type_ == 'trades':
            # del df['trade_ts']
            del df['deleted']
            df = optimize_objects(df, ['trade_ts'])
        return df                    

    def add_trade_side(self, data, convert={}):

        delete_from = convert.get('DELETE_FROM', 'DELETE_FROM')
        delete = convert.get('DELETE', 'DELETE')
        change = convert.get('CHANGE', 'CHANGE')
    
        min_position = data['position'].min()
        data['deletes'] = np.nan
        data.loc[data['event_type'] == delete_from, 'deletes'] = True
        data.loc[(data['event_type'] == delete) & (data['position'] == min_position), 'deletes'] = True
        data.loc[(data['event_type'] == change) & (data['position'] == min_position), 'deletes'] = True
        dict_side = data[data['deletes'] == True].groupby('msg_seq_num')['side'].last().to_dict()
        data['trade_side'] = data['msg_seq_num'].map(dict_side)
        data['trade_side'].fillna(method='bfill', inplace=True)

        del data['deletes']
        
        return data

if __name__ == '__main__':
    import asimov_database as ad
    self = ad.ParquetReader()

    path = "/datastore/date_2020-07-21_decrease_memory_true_order_by_msg_seq_num_symbols_[DOLQ20_WDOQ20].parquet"
    self._read_parquet_file(path)


    symbol = 'MRVE3'
    date = '2019-07-15'

    e.list_files(True)
    e.get_parquet('WDOF20', '2019-12-05', 'events')

    parquet = ad.ParquetCreator()
    parquet.create_book_events(symbol, date)
    parquet.create_trades_files(symbol, date)

    # Carrega dados de level-book, symbol pode ser lista ou str.
    dataframe = e.load_level_book(['WDOG20','DOLG20'], '2020-01-10')

    e.copy_file_to_local('2020-03-23', type_='mirror')
    e.copy_file_to_local('2020-03-23', symbol='DOLJ20', type_='trades')
    e.copy_file_to_local('2020-03-23', symbol='WDOJ20', type_='trades')
    e.copy_file_to_local('2020-03-23', symbol='DOLJ20', type_='events')
    e.copy_file_to_local('2020-03-23', symbol='WDOJ20', type_='events')

    e.copy_file_to_local('2020-04-02', symbol='WINJ20', type_='events')