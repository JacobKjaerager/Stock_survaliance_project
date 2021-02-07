import pandas as pd
from exchangeratesapi import Api as valutaApi
import yfinance as yf
import datetime as dt
import numpy as np
def get_stock_data():
   df = pd.read_csv("controlsheet/Controlsheet.csv", delimiter=";")
   exchangeApi = valutaApi()
   base_valuta = "DKK"
   df["acquiringDate"] = pd.to_datetime(df["acquiringDate"])
   df["buyPriceLocalValuta"] =  df["buyPriceLocalValuta"].str.replace(',', '.').astype(float)
   for index, row in df.iterrows():
      df.at[index, "stockData"] = yf.Ticker(row["stockName"])

   for index, row in df.iterrows():
      your_precentage = 100/(row["stockData"].info["floatShares"]/row["quantity"])
      time = df["acquiringDate"].loc[index]
      currency_symbol = row["stockData"].info["currency"]
      df.at[index, "yourOwnership"] = f"{your_precentage:.9f}"
      df.at[index, "realName"] = row["stockData"].info["shortName"]
      df.at[index, "symbol"] = row["stockData"].info["symbol"]
      df.at[index, "timezone"] = row["stockData"].info["exchangeTimezoneShortName"]
      df.at[index, "localCurrency"] = row["stockData"].info["currency"]
      df.at[index, "stockExchange"] = row["stockData"].info["exchange"]

      exchange_info = exchangeApi.get_rates(
                            base_valuta,
                            [currency_symbol],
                            start_date=time.strftime("%Y-%d-%m"),
                            end_date=(time + pd.Timedelta("1d")).strftime("%Y-%d-%m")
                       )
      df.at[index, "BaseToValuta"] = 1/exchange_info["rates"][time.strftime("%Y-%d-%m")][currency_symbol]
   df["buyPriceInBaseValuta"] = df["BaseToValuta"] * df["buyPriceLocalValuta"]
   df["totalValueOfPositionInBaseValutaAtAcquiringDate"] = df["buyPriceInBaseValuta"] * df["quantity"]
   return df

if __name__ == '__main__':
   test = get_stock_data()
   print("waef")