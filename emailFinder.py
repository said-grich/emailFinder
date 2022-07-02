import os
import re
from datetime import date
import dask.dataframe as dd
import dask.bag as bg
import pandas as pd


class EmailFinder:
    def __init__(self,domainListAsText,path_Files):
        self.textFilePath=domainListAsText;
        self.listOfDomain=self.textFileToList();
        self.filesPath=path_Files;
        self.today=date.today().strftime("%d_%m_%Y")

    def textFileToList(self):
        with open(self.textFilePath) as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
        return lines
    def getFilesReady(self):
        obj = os.scandir(self.filesPath)
        for entry in obj:
            if entry.is_file():
                tmp=entry.name;
                if(tmp.endswith('.txt')):
                    dfText=bg.read_text(os.path.join(self.filesPath)+"\\"+tmp, blocksize='128MB')
                    dfText.map_partitions(self.daskCheckEmail).compute(scheduler='threads')
                elif(tmp.endswith('.csv')):
                    df_=pd.read_csv(os.path.join(self.filesPath)+"\\"+tmp, nrows=1);
                    columns=df_.columns
                    del df_
                    dtypes={}
                    for col in columns:
                        dtypes[col]='object'
                    df = dd.read_csv(os.path.join(self.filesPath)+"\\"+tmp,blocksize="128MB",dtype=dtypes,storage_options={"anon": True, 'use_ssl': True})
                    df.map_partitions(self.daskCheckEmail,meta=df._meta).compute(scheduler='threads')


    def daskCheckEmail(self,df):
        for domain in self.listOfDomain:
            part=[]
            for line in df:
                tmp2 = self.checkForDoamin(line, domain);
                if tmp2 == None:
                    continue
                else:
                    for e in tmp2:
                        with open("outputDir/Emails_" + str(domain) + "_" + self.today + ".txt", 'a+',encoding="utf-8") as f:
                            f.writelines(e+ "\n")
    def daskCheckEmailText(self,df):
        for domain in self.listOfDomain:
            part=[]
            for index, row in df.iterrows():
                line = " ".join(str(el) for el in row)
                tmp2 = self.checkForDoamin(line, domain);
                if tmp2 == None:
                    continue
                else:
                    for e in tmp2:
                        with open("outputDir/Emails_" + str(domain) + "_" + self.today + ".txt", 'a+',encoding="utf-8") as f:
                            f.writelines(e+ "\n")

    def checkForDoamin(self,line,domain):
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', line)
        tmpEm=[]
        for emial  in emails:
            if domain in emial:
                tmpEm.append(emial)
        return tmpEm


