import os, os.path
import datetime as dt
import pandas as pd
import re
from datetime import datetime
from datetime import date
from os import listdir
from os.path import isfile, join
import time


class Monitoring:
    def __init__(self):

        start_path = '/bigdata'
        self.start_path = os.getenv("HOME") + start_path if os.path.isdir(os.getenv("HOME") + '/bigdata') else start_path
        
    #Count all files in a given directory
    def _count_file(self, start_path):
        file_count = sum(len(files) for _, _, files in os.walk(start_path))
        return file_count 

    #Lists all _subdirectories
    def _subdirecory(self):
        A = (list([x[0] for x in os.walk(self.start_path)]))
        return A

    #Count all files in a given directory including _subdirecory(discriminated)
    def total_count(self):
        
        for directory in self._subdirecory():
            if '/info' not in directory and '/files' not in directory:
                print(directory, self._count_file(directory), 'Files')

    #Size(gb) of all files in a given directory
    def _get_size(self, start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    #Size(gb) of all files in a given directory including _subdirecory(discriminated)
    def total_size(self):
        for directory in self._subdirecory():
            if self._get_size(directory)/10 ** 9 > 0.5:
                if '/files' not in directory and '/info' not in directory:
                    print(directory, self._get_size(directory)/10 ** 9, 'GygaBytes')
    
    # List of all files per creation date 
    def files_creation(self):
        A =[]
        B=[]  
        D=[]
        for directory in self._subdirecory():
            for file1 in os.listdir(directory):
                if '/info' not in directory and '/files' not in directory:                
                    a = datetime.strptime(time.ctime(os.path.getctime(directory +'/'+ file1)), '%a %b %d %H:%M:%S %Y')
                    A.append(a)
                    B.append(directory)
                    D.append(file1)                  
        C = (A,B,D)
        df = pd.DataFrame(C)
        df = df.T
        df = df.rename(columns = {0: 'Date', 1: 'Directory', 2:'File'}) 
        df['Date'] = (df['Date'].apply(lambda x : datetime.date(x)))
        df = df [df['File'].str.contains('.parquet')]
        return df
    
    def files_per_day(self):
        df =  self.files_creation()
        df = df.drop(['Directory'], axis=1)
        df = df.groupby(['Date']).count().rename(columns={'Directory' : 'Count'})               
        return df

    #Number of files created in a day in a given directory including _subdirecory(discriminated) 
    def files_per_day_per_directory(self):
        df = self.files_creation()
        df.drop(['File'], axis=1)
        df['Counter'] = 1
        df = df.groupby(['Date','Directory'])['Counter'].sum()
        return df
      
    # List of all files per last modification date 
    def files_modification(self): 
        C = []
        D = []
        for directory in self._subdirecory():
            for file1 in os.listdir(directory):
                if '/info' not in directory and '/files' not in directory:
                    c = datetime.strptime(time.ctime(os.path.getmtime(directory +'/'+ file1)), '%a %b %d %H:%M:%S %Y')
                    C.append(file1)
                    D.append(c)    
        df = pd.DataFrame(C,D)
        df = df.reset_index()    
        df = df.rename(columns = {'index': 'Date', 0: 'File'}) 
        df['Date'] = (df['Date'].apply(lambda x : datetime.date(x)))
        df = df [df['File'].str.contains('.parquet')]
        df = df.dropna()
        df = df.reset_index()
        df = df.drop(['index'], axis = 1)
        return df


if __name__ == '__main__':
    import asimov_database as ad

    M = Monitoring()

    M.total_count()
    
    M.total_size()

    M.files_per_day()

    M.files_per_day_per_directory()

    M.files_creation()

    M.files_modification()

