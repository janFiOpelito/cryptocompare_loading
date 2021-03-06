import requests
import datetime
import pandas as pd
import psycopg2
from pprint import pprint
import urllib
import io
import sqlalchemy
from sqlalchemy import create_engine
import re
import time
from datetime import timedelta
import cryptocompare as cc
import ccxt
from datetime import timedelta
from pytz import timezone
import pytz
import os
#import boto as aws
from pathlib import Path

utc = pytz.utc
from datetime import datetime
from datetime import timezone
dt = datetime(2020, 3, 25)
timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
print(int(timestamp))
import datetime

import logging
import boto3
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')

s3 = boto3.client('s3',aws_access_key_id= AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
response = s3.list_buckets()

bucket_name=''
# Output the bucket names
print('Existing buckets:')
for bucket in response['Buckets']:
    bucket_name=bucket["Name"]
    print(f'  {bucket["Name"]}')

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = s3
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def daily_price_historical(symbol, comparison_symbol, limit, aggregate, toTs='', exchange='' ):

    url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}&aggregate={}'\
            .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)

    if toTs:
        url += '&toTs={}'.format(toTs)
    if exchange:
        url += '&e={}'.format(exchange)

    page = requests.get(url)
    data = page.json()['Data']
    df = pd.DataFrame(data)

    return df

def add_columns_sort (df, key, crypto_base, crypto_quote):
    if not df.empty:
        df['timestamp'] = [datetime.datetime.utcfromtimestamp(d) for d in df.time]
        df['timestamp_france'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
        df['symbol'] = key
        df['crypto_base'] = crypto_base
        df['crypto_quote'] = crypto_quote
        df=df.sort_values(by=['time'], ascending=False)
    return df

"""
def create_table_to_postgresql(tablename, df):

    if not sql_db.has_table(tablename) and not df.empty:
        args = [tablename, sql_db]
        kwargs = {
                "frame" : df,
                "index" : True,
                "index_label" : "crypto_id",
                "keys" : "crypto_id"
            }

        sql_table = pd.io.sql.SQLTable(*args, **kwargs)
        sql_table.create()
"""

time_delta=1
ohlcv_all = []#pd.DataFrame()
exchanges = ['bitfinex','okex']
#exchanges = ['bibox']
#exchanges = ['binance']
#time_base = '2015-01-01'
time_base = '2019-05-01'
nb_lignes = 47 # une année, 365 jours (0-364)

for exchange in exchanges:

    #engine = create_engine('postgresql+psycopg2://postgres:password@localhost/'+exchange+'_dev')

    #conn = engine.connect()
    #sql_db = pd.io.sql.SQLDatabase(engine)

    if exchange=='bitfinex':
        exchange_ccxt = ccxt.bitfinex()
    if exchange=='binance':
        exchange_ccxt = ccxt.binance()
    if exchange=='okex':
        exchange_ccxt = ccxt.okex()
    if exchange=='okcoinusd':
        exchange_ccxt = ccxt.okcoinusd()
        exchange = 'okcoin'
    #if exchange=='bibox':
    #   exchange_ccxt = ccxt.bibox()

    exchange_ccxt_markets = exchange_ccxt.load_markets()

    time_base_sans_apostrophe= time_base.replace("'", "")
    print('time_base_sans_apostrophe',time_base_sans_apostrophe)

    time_base_annee, time_base_mois, time_base_jour = re.split("[-]", time_base_sans_apostrophe)
    dt = datetime.datetime(int(time_base_annee), int(time_base_mois), int(time_base_jour))
    dt = dt + timedelta(days=nb_lignes+1)

    first_time = int(dt.replace(tzinfo=timezone.utc).timestamp())
    print ("first_time",first_time)

    data_folder = Path("../out/data")
    filename='days_' + exchange + '_'+ '2015'+'_2020'
    #filename=data_folder/filename

    for symbol in exchange_ccxt_markets.keys():

        crypto_base, crypto_quote=re.split("[/]", symbol)

        ohlcv = daily_price_historical(crypto_base, crypto_quote, nb_lignes, time_delta, toTs=first_time, exchange= exchange)
        ohlcv = add_columns_sort (ohlcv, symbol, crypto_base, crypto_quote )

        print('-------------------------------')
        print(symbol)
        if not ohlcv.empty:
            print('###close timestamp debut###', ohlcv.iloc[-1]['close'],ohlcv.iloc[-1]['timestamp'])
            print('###close timestamp fin###',ohlcv.iloc[0]['close'], ohlcv.iloc[0]['timestamp'])
            with open(filename, 'a') as f:
                ohlcv.to_csv(f, header=f.tell()==0)

    upload_file(filename, bucket_name, object_name=None)
        #table_name = 'days_' + exchange + '_'+ '2015'+'_2019'
        #create_table_to_postgresql (table_name, ohlcv)

        #if not ohlcv.empty and sql_db.has_table(table_name):

            #ohlcv.to_sql(table_name, conn, if_exists='append', index=False)

    #time.sleep(2000)


#with open("FILE_NAME", "rb") as f:
#    s3.upload_fileobj(filename, "BUCKET_NAME", "OBJECT_NAME")
