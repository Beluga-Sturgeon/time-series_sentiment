from bs4 import BeautifulSoup, Tag
import numpy as np
import pandas as pd
import torch
import constants
import secrets
import re
import requests
import matplotlib.pyplot as plt
import pprint
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import certifi
import json

def get_jsonparsed_data(url):

    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

alltickers = (f"{constants.FMP_SYMBOLS_URL}?apikey={secrets.FMP_API_KEY}")
tickers = get_jsonparsed_data(alltickers)
pprint.pprint(tickers[0])
rowOfTickers = {}
for ticker in tickers:
    rowOfTickers[ticker["symbol"]] = np.nan
pprint.pprint(rowOfTickers)

def daily():
    current_df = pd.read_csv("alldata.csv")
    prevdate:str = current_df.iloc[-1]["date"].split("T")[0]
    new_df = pd.DataFrame()

    pageNum = 0
    complete = False
    while not complete:
        url_sentiment = (f"https://financialmodelingprep.com/api/v4/stock-news-sentiments-rss-feed?page={pageNum}&apikey=b0446da02c01a0943a01730dc2343e34")
        sentiment_news = get_jsonparsed_data(url_sentiment)
        if len(sentiment_news) == 0:
            break

        for article in sentiment_news:
            if article["publishedDate"].split("T")[0] != prevdate:
                row = rowOfTickers.copy()
                row["date"] = article["publishedDate"].split("T")[0]
                row[article["symbol"]] = article["sentimentScore"]
                new_df = new_df.append(row, ignore_index=True)
                print("Getting article from: " + row["date"])
            else:
                complete = True
                break
    try:
        new_df.drop(columns=['Unnamed: 0.0'], inplace=True)
        new_df.drop(columns=['Unnamed: 0.1'], inplace=True)
    except:
        pass

    new_df = new_df.groupby("date").mean().reset_index()
    reversed_df = new_df[::-1]
    current_df = current_df.append(reversed_df)
    current_df.fillna(0.0, inplace=True)
    current_df.to_csv("alldata.csv")
    print(current_df.tail(10))


daily()