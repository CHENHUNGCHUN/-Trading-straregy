
def trade_with_ma(win=0.05,loss=0.03):
    df = pd.read_csv('0050.csv')
    stock_return = [0]
    for i in range(1,len(df['price'])):
        _ = (df['price'][i]-df['price'][i-1]) / df['price'][i-1]
        stock_return.append(_)
    df['stock_return'] = stock_return

    #計算10日均線
    df['10ma'] = df['price'].rolling(window=10).mean()
    df = df.dropna()
    df.reset_index(inplace=True,drop=True)

    #寫入買賣訊號
    buy_singnal = [0]
    for i in range(1,len(df['price'])):
        if (df['price'][i-1] <= df['10ma'][i-1]) and (df['price'][i] > df['10ma'][i]):
            buy_singnal.append(df['price'][i])
        elif (df['price'][i-1] >= df['10ma'][i-1]) and (df['price'][i] < df['10ma'][i]):
            buy_singnal.append(df['price'][i]*-1)
        else:
            buy_singnal.append(0)
    df['buy_singnal'] = buy_singnal
    df['buy_singnal'] =df['buy_singnal'].astype(float)

    #買賣持有
    buy_sell_hold = []
    for i in df['buy_singnal']:
        if i > 0:
            buy_sell_hold.append('buy')
        elif i < 0:
            buy_sell_hold.append('sell')
        else:
            buy_sell_hold.append(0)
    df['buy_sell_hold'] = buy_sell_hold

    #一律將最後一筆設定為賣出
    df.iloc[-1,-1] = 'sell'

    #增加持有標記
    for i in range(len(df['buy_sell_hold'])):
        if df['buy_sell_hold'][i] == 'buy':
            for j in range(1,len(df['buy_sell_hold'])):
                if df['buy_sell_hold'][i+j] == 'sell':
                    break
                else:
                    df['buy_sell_hold'][i+j] = 'holding'
        elif (df['buy_sell_hold'][i] == 'sell') | (df['buy_sell_hold'][i] == 'holding') | (df['buy_sell_hold'][i] == 0):
            pass

    #計算持有期間報酬率
    r = []
    for i in range(len(df['buy_sell_hold'])):
        if df['buy_sell_hold'][i] == 'buy':
            r.append(0)
            for j in range(1,len(df['buy_sell_hold'])):
                if df['buy_sell_hold'][i+j] == 'sell':
                    return_ = (df['price'][i+j]-df['price'][i]) / df['price'][i]
                    r.append(return_)
                    break
                else:
                    return_ = (df['price'][i+j]-df['price'][i]) / df['price'][i]
                    r.append(return_)
        elif (df['buy_sell_hold'][i] == 'holding') | (df['buy_sell_hold'][i] == 'sell'):
            continue
        elif df['buy_sell_hold'][i] == 0:
            r.append('no_position')
    df['return'] = r

    #計算最後報酬率
    total_sell=[]
    for i in range(len(df['buy_sell_hold'])):
        if df.iloc[i,-2] == 'sell':
            total_sell.append(df.iloc[i,-1])
    money=100
    for i in total_sell:
        money *= (1+i)
    #return f'單純用10日均線出場,最後資金為{money:.2f}'

    #將交易測略改為一樣用10日均線進場 但改成盈虧比出場
    df['trading_with_win/loss_ratio']=0
    for i in range(len(df['buy_singnal'])):
        if df.iloc[i,-3] == 'buy':
            df.iloc[i,-1] = 'buy' 
    df['return_win/loss'] = 0
    df2=df.copy()
    df2.tail(20)

    #確保最後一筆不是buy
    if df2.iloc[-1,-2] == 'buy':
        df2.drop(len(df2['trading_with_win/loss_ratio'])-1,0)
        
    #加入盈虧比
    for i in range(len(df2['trading_with_win/loss_ratio'])):
        if df2.iloc[i,-2] == 'buy':
            for j in range(1,len(df2['trading_with_win/loss_ratio'])):
                if i+j < len(df2['trading_with_win/loss_ratio'])-1:   #一個是試算"個數",一個是算index,所以個數要-1
                    Return = (df2.iloc[i+j,2] - df2.iloc[i,2]) / df2.iloc[i,2]
                    if (Return >= win):
                        df2.iloc[i+j,-2] = win
                        df2.iloc[i+j,-1] = 'sell'
                        break
                    elif (Return <= -loss):
                        df2.iloc[i+j,-2] = -loss
                        df2.iloc[i+j,-1] = 'sell'
                        break
                    else:
                        df2.iloc[i+j,-2] = Return
                        #print(i,j)
                elif i+j == len(df2['trading_with_win/loss_ratio'])-1:
                    df2.iloc[i+j,-2] = Return
                    df2.iloc[i+j,-1] = 'sell'
                    break
        else:
            pass

    #計算用盈虧比當出場;原始資金100 最後金額
    sell_return_2 = []
    for i in range(len(df2['return_win/loss'])):
        if df2['return_win/loss'][i] == 'sell':
            sell_return_2.append(df2['trading_with_win/loss_ratio'][i])
    money2=100
    for i in sell_return_2:
        money2 *= (1+i)
    return f"單純用10日均線進出場,最後資金為{money:.2f},總交易次數為{len(total_sell)} \n用10日均線進場,出場用盈虧比,最後資金為{money2:.2f},總交易次數為{len(sell_return_2)}"
###########################################
import pandas as pd
win,loss = eval(input('請輸入停利,停損(不用加負號).ex:0.05,0.02\n=> '))
a=trade_with_ma(win,loss)
print(a)