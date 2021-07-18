import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import requests
import pandas as pd
import webbrowser

access = "4XJ0xegCx1iTlI7EJq0jxvP3YW1NXnjmxutPLQAO"
secret = "xfQYWVxTXl8nolwLumpxXeleIxxSfzdLHXgKdPIB"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)

    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
#predict_price("KRW-BTC")
#schedule.every().hour.do(lambda: predict_price("KRW-BTC"))
rsi = 0
def rsiindex(symbol):
    global rsi
    url = "https://api.upbit.com/v1/candles/minutes/10"

    querystring = {"market":symbol,"count":"500"}

    response = requests.request("GET", url, params=querystring)

    data = response.json()

    df = pd.DataFrame(data)

    df=df.reindex(index=df.index[::-1]).reset_index()

    df['close']=df["trade_price"]

    def rsi(ohlc: pd.DataFrame, period: int = 14):
        ohlc["close"] = ohlc["close"]
        delta = ohlc["close"].diff()

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        _gain = up.ewm(com=(period - 1), min_periods=period).mean()
        _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")

    rsi = rsi(df, 14).iloc[-1]
    print(symbol)
    print('Upbit 10 minute RSI:', rsi)
    print('')

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-ETH')
all_coin.remove('KRW-DOT')
all_coin.remove('KRW-ETC')
all_coin.remove('KRW-SRM')
all_coin.remove('KRW-BTC')
all_coin.remove('KRW-SXP')
all_coin.remove('KRW-BTT')
all_coin.remove('KRW-KNC')
all_coin.remove('KRW-REP')
all_coin.remove('KRW-MBL')
all_coin.remove('KRW-XRP')
all_coin.remove('KRW-XEM')
all_coin.remove('KRW-SNT')
all_coin.remove('KRW-CHZ')
all_coin.remove('KRW-DAWN')
all_coin.remove('KRW-JST')
all_coin.remove('KRW-ENJ')
all_coin.remove('KRW-VET')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-ARK')
all_coin.remove('KRW-GAS')
# 자동매매 시작
#while True:
rsi_name = [] #상승예상코인명
rsi_list = [] #상승예상수치
rsi_list_desc = []

price_name = [] #상승예상코인명
price_gap = [] #상승예상수치
price_gap_desc = []
#price_gap_high = []
# 자동매매 시작
count = 0
count1 = 'true'
count2 = 'true'
count3 = 'true'
web1_1 = 'false'
web1_2 = 'false'
web2_1 = 'false'
web2_2 = 'false'
web3_1 = 'false'
web3_2 = 'false'
while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]
            predict_price(coin)
            #schedule.every().hour.do(lambda: predict_price(coin))
            #schedule.run_pending()

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time + datetime.timedelta(seconds=600) < now < end_time - datetime.timedelta(seconds=60):
                print("진행중... :",  coin)
                #target_price = get_target_price(coin, 0.5)
                current_price = get_current_price(coin)
                rsiindex(coin)
                if rsi < 25 and predicted_close_price/current_price > 1.10 and (count1 == 'true' or count2 == 'true' or count3 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    if count1 == 'true':
                        upbit.buy_market_order(coin, 100000)
                        buycoin_0 = coin
                        buy_price_0 = current_price
                        water_buy_price_0 = current_price
                        print("구매완료 코인 1:",  buycoin_0)
                        count1 = 'false'
                        time.sleep(5)
                    elif count2 == 'true':
                        upbit.buy_market_order(coin, 100000)
                        buycoin_1 = coin
                        buy_price_1 = current_price
                        water_buy_price_1 = current_price
                        print("구매완료 코인 2:",  buycoin_1)
                        count2 = 'false'
                        time.sleep(5)
                    elif count3 == 'true':
                        upbit.buy_market_order(coin, 100000)
                        buycoin_2 = coin
                        buy_price_2 = current_price
                        water_buy_price_2 = current_price
                        print("구매완료 코인 3:",  buycoin_2)
                        count3 = 'false'
                        time.sleep(5)

                if (count1 == 'false') and ((water_buy_price_0 * 1.05) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                #물타기
                elif (count1 == 'false') and ((buy_price_0 * 0.97) > (get_current_price(buycoin_0))) and (web1_1 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_0, 100000)
                        water_current_price1_1 = get_current_price(buycoin_0)
                        water_buy_price_0 = (buy_price_0 + water_current_price1_1)/2
                    web1_1 = 'true'
                elif (count1 == 'false') and ((buy_price_0 * 0.94) > (get_current_price(buycoin_0))) and (web1_2 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_0, 100000) 
                        water_current_price1_2 = get_current_price(buycoin_0)
                        water_buy_price_0 = (buy_price_0 + water_current_price1_1 + water_current_price1_2)/3
                    web1_2 = 'true'
                #물타기 종료
                elif (count1 == 'false') and ((buy_price_0 * 0.90) > (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    all_coin.remove(buycoin_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'

                if (count2 == 'false') and ((water_buy_price_1 * 1.05) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                #물타기
                elif (count2 == 'false') and ((buy_price_1 * 0.97) > (get_current_price(buycoin_1))) and (web2_1 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_1, 100000)
                        water_current_price2_1 = get_current_price(buycoin_1)
                        water_buy_price_1 = (buy_price_1 + water_current_price2_1)/2
                    web2_1 = 'true'
                elif (count2 == 'false') and ((buy_price_1 * 0.94) > (get_current_price(buycoin_1))) and (web2_2 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_1, 100000)
                        water_current_price2_2 = get_current_price(buycoin_1)
                        water_buy_price_1 = (buy_price_1 + water_current_price2_1 + water_current_price2_2)/3
                    web2_2 = 'true'
                #물타기 종료
                elif (count2 == 'false') and ((buy_price_1 * 0.90) > (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    all_coin.remove(buycoin_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    
                if (count3 == 'false') and ((water_buy_price_2 * 1.05) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                #물타기
                elif (count3 == 'false') and ((buy_price_2 * 0.97) > (get_current_price(buycoin_2))) and (web3_1 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_2, 100000)
                        water_current_price3_1 = get_current_price(buycoin_2)
                        water_buy_price_2 = (buy_price_2 + water_current_price3_1)/2
                    web3_1 = 'true'
                elif (count3 == 'false') and ((buy_price_2 * 0.94) > (get_current_price(buycoin_2))) and (web3_2 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_2, 100000)
                        water_current_price3_2 = get_current_price(buycoin_2)
                        water_buy_price_2 = (buy_price_2 + water_current_price3_1 + water_current_price3_2)/3
                    web3_2 = 'true'
                #물타기 종료
                elif (count3 == 'false') and ((buy_price_2 * 0.90) > (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    all_coin.remove(buycoin_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'

                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'

            else:
                print("판매중...")
                if (count1 == 'false') :
                    btc0 = get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                if (count2 == 'false') :
                    btc1 = get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                if (count3 == 'false') :
                    btc2 = get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc2)
                    count2 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'

                #코인리스트 리셋(손해매도 코인 remove 대응)    
                all_coin = pyupbit.get_tickers('KRW')
                all_coin.remove('KRW-ETH')
                all_coin.remove('KRW-DOT')
                all_coin.remove('KRW-ETC')
                all_coin.remove('KRW-SRM')
                all_coin.remove('KRW-BTC')
                all_coin.remove('KRW-SXP')
                all_coin.remove('KRW-BTT')
                all_coin.remove('KRW-KNC')
                all_coin.remove('KRW-REP')
                all_coin.remove('KRW-MBL')
                all_coin.remove('KRW-XRP')
                all_coin.remove('KRW-XEM')
                all_coin.remove('KRW-SNT')
                all_coin.remove('KRW-CHZ')
                all_coin.remove('KRW-DAWN')
                all_coin.remove('KRW-JST')
                all_coin.remove('KRW-ENJ')
                all_coin.remove('KRW-VET')
                all_coin.remove('KRW-MED')
                all_coin.remove('KRW-ARK')
                all_coin.remove('KRW-GAS')

                #price_name.append(coin)
                #price_gap.append(predicted_close_price/current_price)
                #price_gap_desc.append(predicted_close_price/current_price)
                #print("종가 : ", predicted_close_price, "예상가 : ", predicted_close_price_kcm, "현재가 : ", current_price) #kcm
            
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
""" 
price_gap_desc.sort(reverse=True) #내림차순 정렬

price_gap_index_0 = price_gap.index(price_gap_desc[0]) #1번 상승코인
price_gap_index_1 = price_gap.index(price_gap_desc[1]) #2번 상승코인
price_gap_index_2 = price_gap.index(price_gap_desc[2]) #3번 상승코인
print("price_gap_index_0", price_gap_index_0)

print("제일높은수치0 : " ,price_name[price_gap_index_0], " : ", price_gap_desc[0])
print("제일높은수치1 : " ,price_name[price_gap_index_1], " : ", price_gap_desc[1])
print("제일높은수치2 : " ,price_name[price_gap_index_2], " : ", price_gap_desc[2])

while True:
    try:
        rsiindex(price_name[price_gap_index_0])
        if rsi < 25 and price_gap_desc[0] > 1.05 :
            upbit.buy_market_order(price_name[price_gap_index_0], 10000)
            print("1번구매")

        rsiindex(price_name[price_gap_index_1])
        if rsi < 25 and price_gap_desc[1] > 1.05 :
            upbit.buy_market_order(price_name[price_gap_index_1], 10000)
            print("2번구매")

        rsiindex(price_name[price_gap_index_2])
        if rsi < 25 and price_gap_desc[2] > 1.05 :
            upbit.buy_market_order(price_name[price_gap_index_2], 10000)
            print("3번구매")

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)

n = 0
while n < 112 : #총 코인 갯수
    try:
        coin = all_coin[n]
        now = datetime.datetime.now()
        start_time = get_start_time(coin)
        end_time = start_time + datetime.timedelta(days=1)
        print("진행중... :",  coin)
        rsiindex(coin)
        rsi_name.append(coin)
        rsi_list.append(rsi)
        rsi_list_desc.append(rsi)
        
        n = n+1
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)

rsi_list_desc.sort() #오름차순 정렬
price_gap_index_0 = rsi_list.index(rsi_list_desc[0])
price_gap_index_1 = rsi_list.index(rsi_list_desc[1])
price_gap_index_2 = rsi_list.index(rsi_list_desc[2])

print("rsi_row_1 : " ,rsi_name[price_gap_index_0], " : ", rsi_list_desc[0])
print("rsi_row_2 : " ,rsi_name[price_gap_index_1], " : ", rsi_list_desc[1])
print("rsi_row_3 : " ,rsi_name[price_gap_index_2], " : ", rsi_list_desc[2])
 """