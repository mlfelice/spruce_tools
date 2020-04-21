# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 07:26:12 2019

@author: Mark
"""
ftp.retrlines()
import os
from ftplib import FTP
from io import StringIO
import re

# Trying to read files from the ftp server to avoid downloading them all


SPRUCEftp = FTP('mnspruce.ornl.gov')

SPRUCEftp.login()

SPRUCEftp.getWelcome()

SPRUCEftp.cwd('/WEW_Environmental_Data/WEW_Complete_Environ_20190402/')

SPRUCEftp.dir()

temp = StringIO()
SPRUCEftp.retrlines('RETR WEW PLOT_04_Complete_Environ_20190402.csv', temp.write)

# We could try to do operation on each file as stringIO object before saving as csv
# Or maybe just have it filter by date and column
with open(OutFile 'w') as f:
  for line in temp:
    f.write(line)
  

SPRUCEftp.quit()
os.path.abspath(os.listdir(FileDir)[0])

######### Original example
## Download the data files for each plot, then merge
## After running this script, you can use the 20191017_SPRUCE_Soil_Temp_mlf.py script to average/interpolate the temps
## All files downloaded from ftp://mnspruce.ornl.gov/WEW_Environmental_Data/WEW_Complete_Environ_20190402/
FileDir = ("C:/Users/Mark/Desktop/wew_files_temp/")

#"C:/Users/Mark/Dropbox/umn_gutknecht_postdoc/spruce_project/"
#              "spruce_website_data/"

InFileList = [FileDir + x for x in os.listdir(FileDir) if 
              x.endswith('csv')]

OutFile = FileDir + 'DPH_all_data.csv'

InFileHeader = ('Year,Year Fraction,DFOY,TIMESTAMP,RECORD,Day_of_Year,'
                'DayFraction,Plot,Temp_target,CO2_trmt,WS_10,WD_10,WD_SD1,'
                'TS_0__A1,TS_-5__A2,TS_-10__A3,TS_-20__A4,'
                'TS_-30__A5,TS_-40__A6,TS_-50__A7,TS_-100__A8,TS_-200__A9,'
                'TS_Hummock_A1,TS_Hummock_A2,TS_Hummock_A3,TS_0__A1_SD,'
                'TS_-5__A2_SD,TS_-10__A3_SD,TS_-20__A4_SD,TS_-30__A5_SD,'
                'TS_-40__A6_SD,TS_-50__A7_SD,TS_-100__A8_SD,TS_-200__A9_SD,'
                'TS_Hummock_A1_SD,TS_Hummock_A2_SD,TS_Hummock_A3_SD,'
                'TS_0__B1,TS_-5__B2,TS_-10__B3,TS_-20__B4,TS_-30__B5,'
                'TS_-40__B6,TS_-50__B7,TS_-100__B8,TS_-200__B9,TS_Hummock_B1,'
                'TS_Hummock_B2,TS_Hummock_B3,TS_0__B1_SD,TS_-5__B2_SD,'
                'TS_-10__B3_SD,TS_-20__B4_SD,TS_-30__B5_SD,TS_-40__B6_SD,'
                'TS_-50__B7_SD,TS_-100__B8_SD,TS_-200__B9_SD,TS_Hummock_B1_SD,'
                'TS_Hummock_B2_SD,TS_Hummock_B3_SD,TS_0__C1,TS_-5__C2,'
                'TS_-10__C3,TS_-20__C4,TS_-30__C5,TS_-40__C6,TS_-50__C7,'
                'TS_-100__C8,TS_-200__C9,TS_0__C1_SD,TS_-5__C2_SD,'
                'TS_-10__C3_SD,TS_-20__C4_SD,TS_-30__C5_SD,TS_-40__C6_SD,'
                'TS_-50__C7_SD,TS_-100__C8_SD,TS_-200__C9_SD,TA_0_5,RH_0_5,'
                'TA_1_0,RH_1_0,TA_2_0__1,RH_2_0__1,TA_2_0__2,RH_2_0__2,'
                'TA_4_0,RH_4_0,TA_0_5_SD,RH_0_5_SD,TA_1_0_SD,RH_1_0_AD,'
                'TA_2_0__1_SD,RH_2_0__1_SD,TA_2_0__2_SD,RH_2_0__2_SD,'
                'TA_4_0_SD,RH_4_0_SD,PAR_2,PREC_6')

 #csv_in = open( ("C:/Users/Mark/Dropbox/umn_gutknecht_postdoc/spruce_project/"
#              "spruce_website_data/DPH_all_data.csv"))

CompiledFile = open(OutFile, 'w')
CompiledFile.write(InFileHeader + '\n')  # added return character 4/21/2020

for file in InFileList:
  f = open(file, 'r')
  line1 = f.readline()
  if InFileHeader not in line1:
    print('Error: ' + file + ' Header does not match')
  for line in f:
    if line.startswith('Year'):
      continue
    else:
      line = re.sub('(?<=[0-9])-', '/', line) # Fix entries with wrong date format
      CompiledFile.write(line)  # This slows things down quite a bit, maybe we use an if/else statement to check only the first few characters, replace if format wrong
      # Or we could split the strings into lists and only search col of interest
  f.close()
  

CompiledFile.close()

csv_in.close()

# NOTE: WEW PLOT_04_Complete_Environ_20190402.csv header doesn't match because col 3 is 'Time Stamp' instead of TIMESTAMP
# WEW PLOT_10_Complete_Environ_20190402.csv header doesn't match because col 2 is DfOY instead of DFOY
# Column order is still identical, so this doesn't pose a problem