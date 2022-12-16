import psycopg2
import pandas as pd
import numpy as np
import gc
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta
import os
import shutil
import time
import asimov_database as ad
import json
import subprocess


class ParquetCreator:
    def __init__(self, ram_memory=16, connection_settings={}, chunksize=50000000, default_timedelta=24*60):
        self.RAM_AVAILABLE = ram_memory
        self.conn = None
        self.valid_dates = {}
        self.database_params = None
        self.consult = ad.Consultor()
        self.paths = self._get_paths()
        self.connection_settings = connection_settings
        self.chunksize = chunksize
        self.default_timedelta = default_timedelta

    def _add_timedelta(self, date, delta):
        date = date + ' 00:00:00' if len(date) < 12 else date
        return (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(**delta)).strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_datetime(self, date):
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    def _get_paths(self):
        if not 'asimov_config.txt' in os.listdir(os.getenv("HOME")):
            print('[ PARQUET CREATOR ] Creating config files: ~/asimov_config.txt')
            with open(os.getenv("HOME") + '/asimov_config.txt', "w") as path_files:
                path_files.write("LOCAL=/bigdata\n")
                path_files.write("MOUNTED=/bigdata")
            path_files.close()

        with open(os.getenv("HOME") + '/asimov_config.txt', "r") as path_files:
            paths = {line.split('=')[0]: line.split('=')[1].replace('(user)', os.getenv("HOME")).replace('~', os.getenv("HOME")).replace('\n', '') for line in path_files.readlines()}
        return paths

    def _create_sql_connection(self, database='md_rt'):

        if self.connection_settings == {}: 
            databases = {'asimov_mirror': '10.243.7.8',
                        'asimov_dropcopy': '10.243.7.8',
                        'silicontrader': '10.243.7.9',
                        'new_mirror': '10.243.7.9'}

            if database == 'market_data':
                params = {
                            'database': 'market_data',
                            'user': 'readonly',
                            'password': 'readonly',
                            'host': '10.112.1.19',
                            'port': 5432,
                            }

            elif database == 'new_mirror':
                params = {
                            'database': 'mirror',
                            'user': 'readonly',
                            'password': 'readonly',
                            'host': '10.243.7.9',
                            'port': 5431,
                            }
            else:
                params = {
                    'database': database,
                    'user': 'asimov',
                    'password': 'asimov',
                    'host': databases.get(database, '10.112.1.20'),
                    'port': 5432 ,
                    }

        else:
            params = self.connection_settings
        self._connect(params)
         
    def _connect(self, params, retries=2):
        database_params = json.dumps(params, sort_keys=True)

        if database_params == self.database_params and not self.conn is None and self.conn.closed == 0:
            return self.conn
        else:

            count = 0
            while True:
                try:
                    self.conn = psycopg2.connect(**params, connect_timeout=2)
                    self.database_params = database_params
                    break
                except:
                    print('[ PARQUET ] Error on connection creation. Trying again...')
                    self.conn = None
                    time.sleep(1)
                count += 1
                if count > retries:
                    print('[ PARQUET ] Could not establish connection {}'.format(database_params))
                    break

    def _valid_connection(self):
        if self.conn is None:
            print(' [ PARQUET ] Invalid connection to database')
            return False
        return True

    def _query_with_retries(self, symbol, date, next_date, table, db):

        from_ = date
        until_ = self._add_timedelta(date, {'minutes': self.default_timedelta})

        md_incremental = []

        while True:
            if self._get_datetime(until_) > self._get_datetime(next_date):
                until_ = next_date
            string_ = "SELECT * FROM {} WHERE ts >= '{}' AND ts < '{}' AND symbol = '{}'".format(table, from_, until_, symbol)

            error = 0
            while True:
                try:
                    data = pd.read_sql_query(string_, self.conn)
                    md_incremental += [data]
                    break
                except Exception as e:
                    error += 1
                    if error > 4:
                        print('[ PARQUET ] Query error', e)
                        return (pd.DataFrame(), pd.DataFrame())
                    # print('[ PARQUET ] Query error. Retrying...', e)
                    time.sleep(5 * error)
                    self._create_sql_connection(db)

            from_ = self._add_timedelta(from_, {'minutes': self.default_timedelta})
            until_ = self._add_timedelta(until_, {'minutes': self.default_timedelta})

            if self._get_datetime(from_) >= self._get_datetime(next_date):
                break
        
        return pd.concat(md_incremental)

    def _load_postgres_data_for_incremental(self, symbol, date, next_date=None, db='market_data'):
        self._create_sql_connection(db)
        if not self._valid_connection():
            return (pd.DataFrame(), pd.DataFrame())

        date = self._add_timedelta(date, {'days': 0})
        next_date = self._add_timedelta(date, {'days': 1}) if next_date is None else next_date

        md_incremental = self._query_with_retries(symbol, date, next_date, 'md_incremental', db)

        if len(md_incremental) > 0:
            md_incremental.symbol = md_incremental.symbol.astype(str)
            md_incremental.event_type = md_incremental.event_type.astype(str)
            md_incremental.side = md_incremental.side.astype(str)
            md_incremental.order_ts = md_incremental.order_ts.astype(str)
            md_incremental.status = md_incremental.status.astype(str)

            md_incremental.index = pd.to_datetime(md_incremental.ts, utc=True)
            del md_incremental['ts']
            md_incremental = md_incremental.sort_values(by=['id'])
            md_incremental['i'] = np.arange(0, md_incremental.shape[0])

        md_snapshot = self._query_with_retries(symbol, date, next_date, 'md_snapshot', db)
        if len(md_snapshot) > 0:
            md_snapshot.index = pd.to_datetime(md_snapshot.ts, utc=True)
            del md_snapshot['ts']
            md_snapshot.sort_values(['msg_seq_num', 'position'], inplace=True)

        return (md_incremental, md_snapshot)

    def _load_postgres_data_for_trades(self, symbol, date, next_date=None, db='market_data'):
        self._create_sql_connection(db)

        date = self._add_timedelta(date, {'days': 0})
        next_date = self._add_timedelta(date, {'days': 1}) if next_date is None else next_date

        md_trades = self._query_with_retries(symbol, date, next_date, 'md_trade', db)

        if len(md_trades) > 0:
            md_trades.index = pd.to_datetime(md_trades.ts, utc=True)
            del md_trades['ts']
            md_trades = md_trades.sort_values(by=['trade_id'])
        return md_trades
    
    def _load_order_mirror_data(self, date, next_date=None, db='mirror', load_test_symbol=True, new_mirror=False):

        from asimov_tools.simplifiers.supplement import NextActive
        na = NextActive()

        table = "fix_message" if new_mirror else "order_mirror"
        col_name = "ts_nano" if new_mirror else "ts"

        db = "new_mirror" if new_mirror else db
        
        self._create_sql_connection(db)
        next_date = date + 60 * 60 * 24 * 1000 * 1000 * 1000 if next_date is None else next_date

        date_str = datetime.utcfromtimestamp(date / (1000 * 1000 * 1000)).strftime('%Y-%m-%d')
        symbols = ["DOL", "WDO", "IND", "WIN"]
        symbols = ["'{}'".format(na.next_active(date_str, s)) for s in symbols]
        symbols = "( symbol = {} )".format(' OR symbol = '.join(symbols))

        if load_test_symbol:
            string_ = "SELECT * FROM {} WHERE {} >= '{}' AND {} < '{}'".format(table, col_name, date, col_name, next_date)
        else:
            string_ = "SELECT * FROM {} WHERE {} >= '{}' AND {} < '{}' AND {}".format(table, col_name, date, col_name, next_date, symbols)

        if not self._valid_connection():
            return pd.DataFrame()
        md_mirror = pd.read_sql_query(string_, self.conn)
        return md_mirror
    
    def _load_dropcopy_execution_report(self, date, next_date=None, db='silicontrader', trades_only=True):
        self._create_sql_connection(db)

        date = date + ' 00:00:00' if len(date) < 12 else date
        next_date = (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S") if next_date is None else next_date
        string_ = "SELECT * FROM {} WHERE insert_timestamp >= '{}' AND insert_timestamp < '{}'".format('"EXECUTION_REPORT"', date, next_date)
        if trades_only: string_ = string_ + " AND unique_trade_id IS NOT NULL"
        if not self._valid_connection():
            return pd.DataFrame()
        md_mirror = pd.read_sql_query(string_, self.conn)
        return md_mirror

    def _load_dropcopy_trades(self, date, next_date=None, db='silicontrader'):
        self._create_sql_connection(db)

        date = date + ' 00:00:00' if len(date) < 12 else date
        next_date = (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S") if next_date is None else next_date
        string_ = "SELECT * FROM {} WHERE timestamp >= '{}' AND timestamp < '{}'".format('"TRADE"', date, next_date)
        if not self._valid_connection():
            return pd.DataFrame()
        md_mirror = pd.read_sql_query(string_, self.conn)
        return md_mirror
    
    def _load_dropcopy_position(self, db='silicontrader'):
        self._create_sql_connection(db)
        string_ = "SELECT * FROM {}".format('"POSITION"')
        if not self._valid_connection():
            return pd.DataFrame()
        md_mirror = pd.read_sql_query(string_, self.conn)
        return md_mirror

    def _save_parquet(self, where, data, ns_index=False, append=False):
        where_temp = where.replace('.parquet', 'temp.parquet')
        writer = None

        if not append or not os.path.isfile(where):

            chunksize = self.chunksize
            chuncks = int(len(data) / chunksize) + 1

            
            for i in range(chuncks):
                data_ = data.iloc[i * chunksize: (i + 1) * chunksize, :]
                table = pa.Table.from_pandas(data_)
                if writer is None:
                    writer = pq.ParquetWriter(where, table.schema, use_deprecated_int96_timestamps=ns_index)     
                writer.write_table(table)
        
            writer.close()

            
        else:
            old_parquet = pq.ParquetFile(where)
            min_msg_seq = data['msg_seq_num'].min()

            chunksize = self.chunksize

            groups = []
            summed_rows = 0
            for group in range(old_parquet.num_row_groups):
                summed_rows += old_parquet.read_row_group(group).num_rows
                if summed_rows > chunksize or len(groups) == 0:
                    summed_rows = old_parquet.read_row_group(group).num_rows
                    groups += [[group]]
                else:
                    groups[-1] += [group]

            for group in groups:
                old_data = old_parquet.read_row_groups(group).to_pandas()
                if len(data) > 0:
                    data_to_write = old_data[old_data['msg_seq_num'] < min_msg_seq]
                else:
                    data_to_write = old_data
                if len(data_to_write) > 0:
                    table = pa.Table.from_pandas(data_to_write)
                    if writer is None:
                        writer = pq.ParquetWriter(where_temp, table.schema, use_deprecated_int96_timestamps=ns_index)
                    writer.write_table(table)
                    if old_data['msg_seq_num'].max() >= min_msg_seq:
                        break
            
            if writer is not None and len(data) > 0:
                for col in data:
                    if data[col].dtype != old_data[col].dtype:
                        data[col] = data[col].astype(old_data[col].dtype)

            not_created = False
            chuncks = int(len(data) / chunksize) + 1

            for i in range(chuncks):
                table = pa.Table.from_pandas(data.iloc[i * chunksize: (i + 1) * chunksize, :])
                if writer is None:
                    writer = pq.ParquetWriter(where_temp, table.schema, use_deprecated_int96_timestamps=ns_index)
                    not_created = True
                if len(data) > 0 or not_created:
                    writer.write_table(table)
            
            writer.close()
            os.system('cp {} {}'.format(where_temp, where))
            os.remove(where_temp)

        try:
            subprocess.call(['chmod', '0666', where])
        except Exception as e:
            print('[ PARQUET ] Error setting permission.', e)


    # Data creators
    def create_book_events(self, symbol, date, db="market_data", custom_path=None, update=False):

        try:
            
            mounted = self.paths['MOUNTED']
            next_date = None
            if custom_path is None: custom_path = f"{mounted}/events"
            incremental_path = custom_path + f"/{symbol}-incremental-{date}.parquet"
            snapshot_path = custom_path + f"/{symbol}-snapshot-{date}.parquet"
            if update and os.path.isfile(incremental_path):
                try:
                    old_parquet = pq.ParquetFile(incremental_path)
                    last_group = old_parquet.num_row_groups - 1
                    old_data = old_parquet.read_row_group(last_group).to_pandas()
                    date = (old_data.index.max() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
                    next_date = (old_data.index.max() + timedelta(minutes=120)).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    print('[ PARQUET ] Error loading old parquet', symbol, date)
                    update = False


            md_incremental, md_snapshot = self._load_postgres_data_for_incremental(symbol, date, next_date, db=db)
            if len(md_incremental) > 0:
                print('[ PARQUET ] Fetching incremental data for', symbol, date)
                self._save_parquet(incremental_path, md_incremental, append=update)
                print('[ PARQUET ] Fetching snapshot data for', symbol, date)
                self._save_parquet(snapshot_path, md_snapshot, append=update)

            else:
                print('[ PARQUET ] Data not found in md_incremental', symbol, date)
            
            gc.collect()
        
        except Exception as e:
            print('[ PARQUET ] Error in create_book_events', symbol, date, e)

    def create_trades_files(self, symbol, date, db="market_data", custom_path=None):
        try:
            print('[ PARQUET ] Fetching trades data for', symbol, date)
            md_trades = self._load_postgres_data_for_trades(symbol, date, db=db)
            mounted = self.paths['MOUNTED']

            if len(md_trades) > 0:
                if custom_path is None: custom_path = f"{mounted}/trades"
                self._save_parquet(custom_path + f"/{symbol}-{date}.parquet", md_trades)

            else:
                print('[ PARQUET ] Data not found in md_trade', symbol, date)

        except Exception as e:
            print('[ PARQUET ] Error in create_trades_files', symbol, date, e)

    def create_mirror_files(self, date):
        print('[ CREATOR ] | create_mirror_files for date {}'.format(date))
        from asimov_tools.mirror.mirror import BaseMirror
        mirror = BaseMirror(date, load_test_symbol=False, load_log=True, load_from_file=False)
        if len(mirror.raw_data) > 0:
            mounted = self.paths['MOUNTED']
            self._save_parquet("{}/mirror/{}.parquet".format(mounted, date), mirror.raw_data, True)
        else:
            print('[ CREATOR ] | create_mirror_files | No data found for date {}'.format(date))
    
    def create_processed_mirror_files(self, date):
        print('[ CREATOR ] | create_processed_mirror_files for date {}'.format(date))
        from asimov_tools.mirror.mirror import BaseMirror
        mirror = BaseMirror(date, load_test_symbol=False, load_log=True, load_from_file=False)
        mirror.add_idx(True)
        if len(mirror.raw_data) > 0:
            mounted = self.paths['MOUNTED']
            self._save_parquet("{}/mirror/{}_processed.parquet".format(mounted, date), mirror.raw_data, True)
        else:
            print('[ CREATOR ] | create_processed_mirror_files | No data found for date {}'.format(date))
    
    def create_complete_mirror_files(self, date):
        print('[ CREATOR ] | create_complete_mirror_files for date {}'.format(date))
        from asimov_tools.mirror.mirror import BaseMirror
        mirror = BaseMirror(date, load_test_symbol=True, load_log=False, load_from_file=False)
        if len(mirror.raw_data) > 0:
            mounted = self.paths['MOUNTED']
            self._save_parquet("{}/mirror/{}_complete.parquet".format(mounted, date), mirror.raw_data, True)
        else:
            print('[ CREATOR ] | create_complete_mirror_files | No data found for date {}'.format(date))
   
    def create_order_book_files(self, symbol, date, db='market_data'):
        md_incremental, md_snapshot = self._load_postgres_data_for_incremental(symbol, date, db=db)
        # Se não há STARTED no dia, return
        if 'OPEN' not in md_incremental['status'].values:
            return

        # Altera order ids para indexes
        md_incremental['order_id'] = md_incremental['order_id'].fillna(0)
        dict_ = {j:i  for i, j in enumerate(md_incremental['order_id'].unique())}
        md_incremental['order_id'] = md_incremental['order_id'].apply(lambda x: dict_[x]).astype(np.float32)

        md_incremental['inc_code'] = np.arange(md_incremental.shape[0])
        md_incremental['acum'] = 0
        md_incremental['acum'][md_incremental['event_type'] == 'INSERT'] = 1
        md_incremental['acum'][md_incremental['event_type']== 'DELETE'] = -1
        md_incremental['acum'][md_incremental['event_type'] == 'DELETE_FROM'] = -md_incremental['position'][md_incremental['event_type'] == 'DELETE_FROM']
        md_incremental_data = {'bid': md_incremental[md_incremental['side']!='A'], 'ask': md_incremental[md_incremental['side']!='B']}
        col_map = {md_incremental.columns[i]: i for i in range(len(md_incremental.columns))}

        # Check se há snapshots para tratar
        if len(md_snapshot):
            snap_type = True
            idx_snap = md_snapshot.index.unique()
        else:
            snap_type = False

        c = 0
        for side in md_incremental_data.keys():
            mounted = self.paths['MOUNTED']
            price_file = f"{mounted}/order-book/{symbol}-price-{side}-{date}.parquet"
            quantity_file = f"{mounted}/order-book/{symbol}-quantity-{side}-{date}.parquet"
            broker_file = f"{mounted}/order-book/{symbol}-broker-{side}-{date}.parquet"
            inc_code_file = f"{mounted}/order-book/{symbol}-inc_code-{side}-{date}.parquet"
            order_id_file = f"{mounted}/order-book/{symbol}-order_id-{side}-{date}.parquet"

            print('Working on {} {} data'.format(side, symbol))
            np_incr = md_incremental_data[side].values.copy()
            ts_index = md_incremental_data[side].index.copy()

            max_levels = int(max(md_incremental_data[side]['position'].max(), md_incremental_data[side]['acum'].cumsum().max())) + 10
            matrix_size = (max_levels *  4 *  np_incr.shape[0] * 4) / (1024 * 1024 * 1024)
            splits = int(matrix_size / self.RAM_AVAILABLE * 4) + 1
            list_inc_code = []

            # Splitting data to fit RAM
            split_size = int(np_incr.shape[0] / splits) + 1
            np_data = np.zeros((max_levels, 3, split_size), dtype=np.float32)
            np_order_id = np.zeros((max_levels, split_size), dtype=np.float32)

            j = 0
            order_book_index = []
            msn_to_ignore = 0

            for i in range(len(np_incr)):
                # IGNORE MSG_SEQ_NUM
                if np_incr[i, col_map['msg_seq_num']] == msn_to_ignore:
                    if np_incr[i, col_map['event_type']] != 'STATUS' and np_incr[i, col_map['event_type']] != 'STARTED': 
                        continue

                if j > 0:
                    np_data[:, :, j] = np_data[:, :, j-1]
                    np_order_id[:, j] = np_order_id[:, j-1]

                # =========================================================================
                try:
                    pos = int(np_incr[i, col_map['position']]) - 1
                except:
                    pos = 0

                # SNAPSHOT
                if snap_type and ts_index[i] in idx_snap and np_incr[i, col_map['event_type']] == 'STARTED':
                    print('Working on snapshot data')
                    msn_to_ignore = np_incr[i, col_map['msg_seq_num']]
                    snap_side = 'B' if side == 'bid' else 'A'
                    md_snap_slice = md_snapshot[md_snapshot.index == ts_index[i]].copy()
                    np_snap_slice = md_snap_slice[md_snap_slice['side'] == snap_side].values
 
                    col_map_snap = {md_snap_slice.columns[i]: i for i in range(len(md_snap_slice.columns))}
                    np_data[:, :, j] = 0
                    np_order_id[:, j] = 0
                    print('msn_to_ignore: {} - Snap shape: {}'.format(msn_to_ignore, np_snap_slice.shape[0]))

                    for k in range(len(np_snap_slice)):
                        pos = np_snap_slice[k, col_map_snap['position']] - 1
                        np_data[pos, 0, j] = np_snap_slice[k, col_map_snap['price']]
                        np_data[pos, 1, j] = np_snap_slice[k, col_map_snap['quantity']]
                        np_data[pos, 2, j] = np_snap_slice[k, col_map_snap['broker']]
                        np_order_id[pos, j] = np_snap_slice[k, col_map_snap['order_id']]

                # INSERT
                if np_incr[i, col_map['event_type']] == 'INSERT':
                    # Caso ordem não tenha sido inserida
                    if np_data[pos, 2, j] != 0:
                        np_data[pos+1:, :, j] = np_data[pos:-1, :, j]
                        np_order_id[pos+1:, j] = np_order_id[pos:-1, j]
                    np_data[pos, 0, j] = np_incr[i, col_map['price']]
                    np_data[pos, 1, j] = np_incr[i, col_map['quantity']]
                    np_data[pos, 2, j] = np_incr[i, col_map['broker']]
                    np_order_id[pos, j] = np_incr[i, col_map['order_id']]

                # DELETE
                if np_incr[i, col_map['event_type']] == 'DELETE':
                    np_data[pos:-1, :, j] = np_data[pos+1:, :, j]
                    np_order_id[pos:-1, j] = np_order_id[pos+1:, j]
                    np_data[-1, :, j] = np.zeros(3)
                    np_order_id[-1, j] = 0

                # CHANGE
                if np_incr[i, col_map['event_type']] == 'CHANGE':
                    np_data[pos, 0, j] = np_incr[i, col_map['price']]
                    np_data[pos, 1, j] = np_incr[i, col_map['quantity']]
                    np_data[pos, 2, j] = np_incr[i, col_map['broker']]
                    np_order_id[pos, j] = np_incr[i, col_map['order_id']]

                # DELETE_FROM
                if np_incr[i, col_map['event_type']] == 'DELETE_FROM':
                    a = np_data.shape[0]
                    b = pos + 1
                    c_ = a - b
                    np_data[:c_, :, j] = np_data[pos+1:, :, j]
                    np_data[c_:, :, j] = 0
                    np_order_id[:c_, j] = np_order_id[pos+1:, j]
                    np_order_id[c_:, j] = 0

                # DELETE_THRU
                if np_incr[i, col_map['event_type']] == 'DELETE_THRU':
                    np_data[:, :, j] = np.zeros((max_levels, 3))
                    np_order_id[:, j] = np.zeros((max_levels))

                order_book_index += [ts_index[i]]
                list_inc_code += [np_incr[i, col_map['inc_code']]]
                j += 1

                # Resetting numpy
                if j == split_size - 1 or i == len(np_incr) - 1:
                    last_data = np_data[:, :, j-1].copy()
                    last_order_id = np_order_id[:, j-1].copy()

                    price_data = pd.DataFrame(np_data[:, 0, :j].transpose(), index=order_book_index, columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                    quantity_data = pd.DataFrame(np_data[:, 1, :j].transpose(), index=order_book_index, columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                    broker_data = pd.DataFrame(np_data[:, 2, :j].transpose(), index=order_book_index, columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                    order_id_data = pd.DataFrame(np_order_id[:, :j].transpose(), index=order_book_index, columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                    inc_code_data = pd.DataFrame(list_inc_code, index=order_book_index)

                    price_data = pa.Table.from_pandas(price_data)
                    quantity_data = pa.Table.from_pandas(quantity_data)
                    broker_data = pa.Table.from_pandas(broker_data)
                    order_id_data = pa.Table.from_pandas(order_id_data)
                    inc_code_data = pa.Table.from_pandas(inc_code_data)

                    if c == 0:
                        price_writer = pq.ParquetWriter(price_file, price_data.schema)
                        quantity_writer = pq.ParquetWriter(quantity_file, quantity_data.schema)
                        broker_writer = pq.ParquetWriter(broker_file, broker_data.schema)
                        order_id_writer = pq.ParquetWriter(order_id_file, order_id_data.schema)
                        inc_code_writer = pq.ParquetWriter(inc_code_file, inc_code_data.schema)
                        c = 1

                    price_writer.write_table(price_data)
                    quantity_writer.write_table(quantity_data)
                    broker_writer.write_table(broker_data)
                    order_id_writer.write_table(order_id_data)
                    inc_code_writer.write_table(inc_code_data)

                    np_data = np.zeros((max_levels, 3, split_size), dtype=np.float32)
                    np_data[:, :, 0] = last_data.copy()
                    np_order_id = np.zeros((max_levels, split_size), dtype=np.float32)
                    np_order_id[:, 0] = last_order_id.copy()
                    list_inc_code = []
                    order_book_index = []
                    j = 0
            
            price_writer.close()
            quantity_writer.close()
            broker_writer.close()
            order_id_writer.close()
            inc_code_writer.close()
            c = 0
            del np_data, np_incr
            gc.collect()

    def create_simple_level_book_files(self, symbol, date, max_levels=50, update=False):
        from asimov_simulator.modules.utils import IDX, TIMESTAMP, MSG_SEQ_NUM, ID, SIDE, NOTIFY, TYPE
        from asimov_simulator import MarketData
        from asimov_tools.simplifiers.supplement import get_min_tick

        mktdata = MarketData({'date' : date, 'symbols' : [symbol], 'reload': True}) 

        chunck_size = 100000
        clear = True

        min_tick = get_min_tick(symbol)

        idx_count = -1
        first_idx = -1

        starting_aggr_price = []
        starting_aggr_quantity = []
        starting_aggr_level_len = []

        mounted = self.paths['MOUNTED']
        output_price_file = [mounted + "/simple-level-book/{}-price-{}-{}.parquet".format(symbol, side, date) for s, side in enumerate(["bid", "ask"])]
        output_quantity_file = [mounted + "/simple-level-book/{}-quantity-{}-{}.parquet".format(symbol, side, date) for s, side in enumerate(["bid", "ask"])]
        output_level_len_file = [mounted + "/simple-level-book/{}-level_len-{}-{}.parquet".format(symbol, side, date) for s, side in enumerate(["bid", "ask"])]
        output_price_file_cache = [mounted + "/simple-level-book/cache_{}-price-{}-{}.parquet".format(symbol, side, date) for s, side in enumerate(["bid", "ask"])]
        output_quantity_file_cache = [mounted + "/simple-level-book/cache_{}-quantity-{}-{}.parquet".format(symbol, side, date) for s, side in enumerate(["bid", "ask"])]
        output_level_len_file_cache = [mounted + "/simple-level-book/cache_{}-level_len-{}-{}.parquet".format(symbol, side, date) for s, side in enumerate(["bid", "ask"])]

        writers = {}
        dtypes = {'bid': {}, 'ask': {}}

        if update:
            for s, side in enumerate(["bid", "ask"]):

                for file, cache, file_type in [[output_price_file[s], output_price_file_cache[s], 'price'],
                                                [output_quantity_file[s], output_quantity_file_cache[s], 'quantity'],
                                                [output_level_len_file[s], output_level_len_file_cache[s], 'level_len']]:
                    
                    if os.path.isfile(file) and pq.ParquetFile(file).num_row_groups > 1:
                        old_parquet = pq.ParquetFile(file)
                        for group in range(old_parquet.num_row_groups - 1):
                            old_data = old_parquet.read_row_groups([group]).to_pandas()
                            table = pa.Table.from_pandas(old_data)
                            if not cache in writers:
                                writers[cache] = pq.ParquetWriter(cache, table.schema)
                            if 'idx_symbol' in old_data:
                                first_idx = old_data['idx_symbol'].max()
                                writers[cache].write_table(table)
                                if not file_type in dtypes[side]:
                                    dtypes[side][file_type] = {col: old_data[col].dtype for col in old_data}

                                if group == old_parquet.num_row_groups - 2:
                                    if file_type == 'price':
                                        starting_aggr_price += [old_data[['{}_{}'.format(side, i) for i in range(max_levels)]].to_numpy()[-1][:].copy()] 
                                    if file_type == 'quantity':
                                        starting_aggr_quantity += [old_data[['{}_{}'.format(side, i) for i in range(max_levels)]].to_numpy()[-1][:].copy()] 
                                    if file_type == 'level_len':
                                        starting_aggr_level_len += [old_data[['{}_{}'.format(side, i) for i in range(max_levels)]].to_numpy()[-1][:].copy()] 

        while mktdata.data_store.next():
            idx_count += 1

            if idx_count > first_idx:
                if clear:
                    data_shape = (chunck_size, max_levels)
                    aggr_price = [np.zeros(data_shape, dtype=np.float32), np.zeros(data_shape, dtype=np.float32)]
                    aggr_quantity = [np.zeros(data_shape, dtype=np.uint32), np.zeros(data_shape, dtype=np.uint32)]
                    aggr_level_len = [np.zeros(data_shape, dtype=np.uint16), np.zeros(data_shape, dtype=np.uint16)]
                    if not starting_aggr_price == []:
                        for side in [0, 1]:
                            aggr_price[side][0][:] = starting_aggr_price[side][:]
                            aggr_quantity[side][0][:] = starting_aggr_quantity[side][:]
                            aggr_level_len[side][0][:] = starting_aggr_level_len[side][:]

                    list_ts = []
                    list_msg_seq_num = []
                    list_id = []
                    list_notify = []
                    print("[ PARQUET CREATOR ] {} - Reached row {} / {}".format(datetime.now(), int(idx_count), int(mktdata.data_store.data_size)))
                    clear = False
                    row = -1

                row += 1
                list_msg_seq_num += [mktdata.last_message[MSG_SEQ_NUM]]
                list_ts += [mktdata.last_message[TIMESTAMP]]
                list_id += [mktdata.last_message[ID]]
                list_notify += [mktdata.last_message[NOTIFY]]
                
                s = mktdata.last_message[SIDE]
                s = s if isinstance(s, int) else 0
                s_alt = 0 if s == 1 else 1

                if mktdata.last_message[TYPE] == "incremental":
                    try: 
                        best_price = mktdata.book[symbol][s][0, 0]
                        if s == 0:
                            limit_price = best_price - min_tick * (max_levels * 2)
                            cut_idx = np.where(mktdata.book[symbol][s][:, 0] < limit_price)[0][0]
                        else:
                            limit_price = best_price + min_tick * (max_levels * 2)
                            cut_idx = np.where(mktdata.book[symbol][s][:, 0] > limit_price)[0][0]
                        if cut_idx == 0:
                            print("Error: cut_idx: {}".format(cut_idx))
                    except:
                        cut_idx = mktdata.book[symbol][s][:, 0].shape[0]

                    price_line = mktdata.book[symbol][s][:cut_idx, 0]
                    quantity_line = mktdata.book[symbol][s][:cut_idx, 1]
                    
                    i = np.nonzero(np.diff(price_line))[0] + 1
                    i = np.insert(i, 0, 0)
                    c1 = price_line[i][:max_levels]
                    c2 = np.add.reduceat(quantity_line, i)[:max_levels]
                    
                    uniques, idx, count = np.unique(price_line, return_counts=True, return_inverse=True)
                    c4 = count[idx][i][:max_levels]
                    aggr_price[s][row, :len(c1)] = c1
                    aggr_quantity[s][row, :len(c2)] = c2
                    aggr_level_len[s][row, :len(c4)] = c4
                    
                    if row > 0:
                        aggr_price[s_alt][row, :] = aggr_price[s_alt][row-1, :]
                        aggr_quantity[s_alt][row, :] = aggr_quantity[s_alt][row-1, :]
                        aggr_level_len[s_alt][row, :] = aggr_level_len[s_alt][row-1, :]
                
                else:
                    aggr_price[s_alt][row, :] = aggr_price[s_alt][row-1, :]
                    aggr_quantity[s_alt][row, :] = aggr_quantity[s_alt][row-1, :]
                    aggr_level_len[s_alt][row, :] = aggr_level_len[s_alt][row-1, :]

                    aggr_price[s][row, :] = aggr_price[s][row-1, :]
                    aggr_quantity[s][row, :] = aggr_quantity[s][row-1, :]
                    aggr_level_len[s][row, :] = aggr_level_len[s][row-1, :]


                if row == chunck_size - 1 or idx_count == mktdata.data_store.length - 2:
                    
                    clear = True
                    ts_index = pd.to_datetime(np.array(list_ts), unit="ms")
                    print("[ PARQUET CREATOR ] {} - Saving chunk...".format(datetime.now()))

                    for s, side in enumerate(["bid", "ask"]):

                        df_price_data = pd.DataFrame(aggr_price[s][:(row + 1), :], index=ts_index, 
                                        columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                        df_quantity_data = pd.DataFrame(aggr_quantity[s][:(row + 1), :], index=ts_index, 
                                        columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                        df_level_len_data = pd.DataFrame(aggr_level_len[s][:(row + 1), :], index=ts_index, 
                                        columns=['{}_{}'.format(side, i) for i in range(max_levels)])

                        df_price_data["msg_seq_num"] = list_msg_seq_num
                        df_quantity_data["msg_seq_num"] = list_msg_seq_num
                        df_level_len_data["msg_seq_num"] = list_msg_seq_num
                        df_price_data["id"] = list_id
                        df_quantity_data["id"] = list_id
                        df_level_len_data["id"] = list_id
                        df_price_data["notify"] = list_notify
                        df_quantity_data["notify"] = list_notify
                        df_level_len_data["notify"] = list_notify
                        df_price_data["idx_symbol"] = np.arange(len(df_price_data)) + (first_idx + 1)
                        df_quantity_data["idx_symbol"] = np.arange(len(df_price_data)) + (first_idx + 1)
                        df_level_len_data["idx_symbol"] = np.arange(len(df_price_data)) + (first_idx + 1)


                        if 'price' in dtypes[side]:
                            for col in df_price_data:
                                if df_price_data[col].dtype != dtypes[side]['price'][col]:
                                    df_price_data[col] = df_price_data[col].astype(dtypes[side]['price'][col])
                        if 'quantity' in dtypes[side]:
                            for col in df_quantity_data:
                                if df_quantity_data[col].dtype != dtypes[side]['quantity'][col]:
                                    df_quantity_data[col] = df_quantity_data[col].astype(dtypes[side]['quantity'][col])
                        if 'level_len' in dtypes[side]:
                            for col in df_level_len_data:
                                if df_level_len_data[col].dtype != dtypes[side]['level_len'][col]:
                                    df_level_len_data[col] = df_level_len_data[col].astype(dtypes[side]['level_len'][col])

                        table_price_data = pa.Table.from_pandas(df_price_data)
                        table_quantity_data = pa.Table.from_pandas(df_quantity_data)
                        table_level_len_data = pa.Table.from_pandas(df_level_len_data)

                        if not output_price_file_cache[s] in writers:
                            writers[output_price_file_cache[s]] = pq.ParquetWriter(output_price_file_cache[s], table_price_data.schema)
                        if not output_quantity_file_cache[s] in writers:
                            writers[output_quantity_file_cache[s]] = pq.ParquetWriter(output_quantity_file_cache[s], table_quantity_data.schema)
                        if not output_level_len_file_cache[s] in writers:

                            writers[output_level_len_file_cache[s]] = pq.ParquetWriter(output_level_len_file_cache[s], table_level_len_data.schema)
                        writers[output_price_file_cache[s]].write_table(table_price_data)
                        writers[output_quantity_file_cache[s]].write_table(table_quantity_data)
                        writers[output_level_len_file_cache[s]].write_table(table_level_len_data)

                    first_idx = len(df_price_data) + first_idx

                    starting_aggr_price = [aggr_price[0][-1][:].copy(), aggr_price[1][-1][:].copy()]
                    starting_aggr_quantity = [aggr_quantity[0][-1][:].copy(), aggr_quantity[1][-1][:].copy()]
                    starting_aggr_level_len = [aggr_level_len[0][-1][:].copy(), aggr_level_len[1][-1][:].copy()]

                    del aggr_price
                    del aggr_quantity
                    del aggr_level_len
                    del df_price_data
                    del df_quantity_data
                    del df_level_len_data
                    del list_msg_seq_num
                    del list_id
                    del list_notify
                    del table_price_data
                    del table_quantity_data
                    del table_level_len_data
                    gc.collect()

        for name in writers:
            writers[name].close()
        
        for s, side in enumerate(["bid", "ask"]):
            os.system('cp {} {}'.format(output_price_file_cache[s], output_price_file[s]))
            os.remove(output_price_file_cache[s])
            os.system('cp {} {}'.format(output_quantity_file_cache[s], output_quantity_file[s]))
            os.remove(output_quantity_file_cache[s])
            os.system('cp {} {}'.format(output_level_len_file_cache[s], output_level_len_file[s]))
            os.remove(output_level_len_file_cache[s])

            try:
                subprocess.call(['chmod', '0666', output_price_file[s]])
                subprocess.call(['chmod', '0666', output_quantity_file[s]])
                subprocess.call(['chmod', '0666', output_level_len_file[s]])
            except Exception as e:
                print('[ PARQUET ] Error setting permission.', e)

        print('{} {} {}'.format(idx_count, mktdata.data_store.length, idx_count == mktdata.data_store.length - 1))

    def create_level_book_files(self, symbol, date, max_levels=100):
        for side in ['bid', 'ask']:
            print('Working {} side of {} level book'.format(side, symbol))
            price_file = "{}-price-{}-{}.parquet".format(symbol, side, date)
            quantity_file = "{}-quantity-{}-{}.parquet".format(symbol, side, date)
            broker_file = "{}-broker-{}-{}.parquet".format(symbol, side, date)
            level_len_file = "{}-level_len-{}-{}.parquet".format(symbol, side, date)

            mounted = self.paths['MOUNTED']

            output_price_file = mounted + "/level-book/" + price_file
            output_quantity_file = mounted + "/level-book/" + quantity_file
            output_broker_file = mounted + "/level-book/" + broker_file
            output_level_len_file = mounted + "/level-book/" + level_len_file

            price_pf = pq.ParquetFile(mounted + '/order-book/' + price_file)
            quantity_pf = pq.ParquetFile(mounted + '/order-book/' + quantity_file)
            broker_pf = pq.ParquetFile(mounted + '/order-book/' + broker_file)
            num_rows = price_pf.metadata.num_row_groups

            c = 0
            for read_row in range(num_rows):
                price_data = price_pf.read_row_group(read_row).to_pandas()
                quantity_data = quantity_pf.read_row_group(read_row).to_pandas()
                broker_data = broker_pf.read_row_group(read_row).to_pandas()

                aggr_price = np.zeros(price_data.shape)
                aggr_quantity = np.zeros(quantity_data.shape)
                aggr_broker = np.zeros(broker_data.shape)
                aggr_level_len = np.zeros(price_data.shape)

                np_price = price_data.values
                np_quantity = quantity_data.values
                np_broker = broker_data.values
                ts_index = price_data.index

                #  ==================
                for row in range(aggr_price.shape[0]):
                    price_line = np_price[row, :]
                    quantity_line = np_quantity[row, :]
                    broker_line = np_broker[row, :]

                    i = np.nonzero(np.diff(price_line))[0] + 1
                    i = np.insert(i, 0, 0)

                    # Compute the result columns
                    c1 = price_line[i]
                    c2 = np.add.reduceat(quantity_line, i)
                    c3 = broker_line[i]
                    
                    uniques, idx, count = np.unique(price_line, return_counts=True, return_inverse=True)
                    c4 = count[idx][i]

                    # Concatenate the columns
                    aggr_price[row, :c1.shape[0]] = c1
                    aggr_quantity[row, :c2.shape[0]] = c2
                    aggr_broker[row, :c3.shape[0]] = c3
                    aggr_level_len[row, :c1.shape[0]] = c4

                df_price_data = pd.DataFrame(aggr_price[:, :max_levels], index=[ts_index], columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                df_quantity_data = pd.DataFrame(aggr_quantity[:, :max_levels], index=[ts_index], columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                df_broker_data = pd.DataFrame(aggr_broker[:, :max_levels], index=[ts_index], columns=['{}_{}'.format(side, i) for i in range(max_levels)])
                df_level_len_data = pd.DataFrame(aggr_level_len[:, :max_levels], index=[ts_index], columns=['{}_{}'.format(side, i) for i in range(max_levels)])

                df_price_data = pa.Table.from_pandas(df_price_data)
                df_quantity_data = pa.Table.from_pandas(df_quantity_data)
                df_broker_data = pa.Table.from_pandas(df_broker_data)
                df_level_len_data = pa.Table.from_pandas(df_level_len_data)

                if c == 0:
                    price_writer = pq.ParquetWriter(output_price_file, df_price_data.schema)
                    quantity_writer = pq.ParquetWriter(output_quantity_file, df_quantity_data.schema)
                    broker_writer = pq.ParquetWriter(output_broker_file, df_broker_data.schema)
                    level_len_writer = pq.ParquetWriter(output_level_len_file, df_level_len_data.schema)
                    c = 1

                price_writer.write_table(df_price_data)
                quantity_writer.write_table(df_quantity_data)
                broker_writer.write_table(df_broker_data)
                level_len_writer.write_table(df_level_len_data)
                del df_price_data, df_quantity_data, df_broker_data, df_level_len_data
                del aggr_price, aggr_quantity, aggr_broker, aggr_level_len
                gc.collect()

            price_writer.close()
            quantity_writer.close()
            broker_writer.close()
            broker_writer.close()
            level_len_writer.close()
    
    # Viewers
    def list_db_tables(self):
        # self._create_sql_connection()
        cursor = self.conn.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        return [table[0] for table in cursor.fetchall()]
    
    def list_columns_in_table(self, table_name):
        self._create_sql_connection()
        tables = self.list_db_tables()
        if table_name in tables:
            cursor = self.conn.cursor()
            cursor.execute("Select * FROM {} LIMIT 0".format(table_name))
            return [column[0] for column in cursor.description]
        else:
            print(' [ PARQUET ] Table not found. Valid tables: ', ', '.join(tables))
            return []

    def get_distinct_item_from_table(self, item, table_name, where=None, db="market_data"):
        self._create_sql_connection(db)
        tables = self.list_db_tables()
        if table_name in tables:
            # columns = self.list_columns_in_table(table_name)
            # if item in columns:
            cursor = self.conn.cursor()
            if where is None:
                cursor.execute("SELECT DISTINCT {} FROM {}".format(item, table_name))
                return [column[0] for column in cursor.fetchall()]
            elif isinstance(where, dict):
                w = ' AND '.join(["{} '{}'".format(key, where[key]) for key in where])
                cursor.execute("SELECT DISTINCT {} FROM {} WHERE {}".format(item, table_name, w))
                return [column[0] for column in cursor.fetchall()]
            else:
                cursor.execute("SELECT DISTINCT {} FROM {} WHERE {}".format(item, table_name, where))
                return [column[0] for column in cursor.fetchall()]
            # else:
            #     print(' [ PARQUET ] Item not found. Valid items: ', ', '.join(columns))
            #     return []
        else:
            print(' [ PARQUET ] Table not found. Valid tables: ', ', '.join(tables))
            return []

    def create_missing_inc(self, db = 'market_data', initial_date=None, final_date=None, symbol=None, type_=None):
        A = self.consult.diff_events(initial_date=initial_date, final_date=final_date, symbol=symbol, type_=type_)
        for keys in A:
            for keys2 in A[keys]:
                if (bool(A[keys][keys2])) is True:
                    if keys2 == 'incremental':
                        for date in A[keys][keys2]:
                            self.create_book_events(keys, date, db=db)
                            
    def create_missing_trade(self, db ='market_data', initial_date=None, final_date=None, symbol=None):
        A = self.consult.diff_trades(initial_date=initial_date, final_date=final_date, symbol=symbol)
        for keys in A:
            if bool(A[keys]) is True:
                for date in A[keys]:
                    self.create_trades_files(keys, date, db=db)

    def create_missing_mirror(self, db ='mirror', initial_date=None, final_date=None):
        A = self.consult.diff_mirror(initial_date=None, final_date=None)
        for date in A:
            self.create_mirror_files(date, db)

    def _hunts_daily_incremental(self, db ='mirror'):
        self._create_sql_connection(database=db)
        date_a = str(date.today())
        since = int(datetime.strptime(date_a, "%Y-%m-%d").strftime("%s")) * (1000 ** 3)
        until = (int(datetime.strptime(date_a, "%Y-%m-%d").strftime("%s")) + 24 * 60 * 60) * (1000 ** 3)
        string_mirror = "SELECT distinct symbol FROM {} WHERE ts between '{}' AND '{}'".format('order_mirror', since, until)
        self.mirror = pd.read_sql_query(string_mirror, self.conn)
        # wdo = parquet.mirror['symbol'][0]
        A = list(self.mirror['symbol'][0])

        if A[0] == 'W':
            wdo = self.mirror['symbol'][0]
            dol = "DOL" + A[3] + A[4] + A[5]

        elif A[0] == 'D':
            dol = self.mirror['symbol'][0]
            wdo = 'WDO' + A[3] + A[4] + A[5]

        return [dol, wdo]

    def create_daily_incremental(self, db ='market_data'):
        symbols = self._hunts_daily_incremental()
        date_ = date.today().strftime("%Y-%m-%d")        
        for keys in symbols:
            self.create_book_events(keys, date_, db=db)
            self.create_trades_files(keys, date_, db=db)


if __name__ == '__main__':
    
    # from asimov_database import ParquetCreator
    self = ParquetCreator()
    self.create_processed_mirror_files("2020-09-04")

    from asimov_tools import LProfiler
    @LProfiler.do_profile(follow=[self.create_simple_level_book_files])
    def profile(self):
        self.create_simple_level_book_files("INDJ20", "2020-04-03")
    profile(self)
  


    parquet._create_sql_connection('silicontrader')
    cursor = parquet.conn.cursor()
    cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")

    #     return [table[0] for table in cursor.fetchall()]

    def create(symbol, parq):
        parq.create_all_book_events_files_for_symbol(symbol, overwrite=False)
        parq.create_all_trade_files_for_symbol(symbol, overwrite=False)

    symbols = ['WDOH19',
            'DOLJ19', 'WDOJ19',
            'DOLK19', 'WDOK19',
            'DOLM19', 'WDOM19',
            'DOLN19', 'WDON19',
            'DOLQ19', 'WDOQ19',
            'DOLU19', 'WDOU19',
            'DOLV19', 'WDOV19',
            'DOLX19', 'WDOX19',
            'DOLZ19', 'WDOZ19']
    for symbol in symbols:
        create(symbol, parquet)
        # parquet.create_book_events(symbol, '2019-10-14')
        # parquet.create_trades_files(symbol, '2019-10-14')

    #parquet.create_missing_inc(symbol=['DOL', 'WDO'])

    #parquet.create_missing_inc(symbol=['DOL', 'WDO'])
    #parquet.create_missing_mirror()
