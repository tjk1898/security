import akshare as ak
import pandas as pd
import datetime as dt
import numpy as np
import talib as tl
import matplotlib.pyplot as plt

def get_price(security,end_date=None,rag=1800):
    if end_date is None:
        end_date = dt.datetime.today()
    
    start_date = end_date - dt.timedelta(days=rag)    
    str_end_date = end_date.strftime('%Y%m%d')
    str_start_date = start_date.strftime('%Y%m%d')
    price = ak.stock_zh_a_hist(symbol=security, period="daily", start_date=str_start_date, end_date=str_end_date, adjust="qfq")
    price.columns = ['date','open','close','high','low','volume','turnover','amp_rate','quote_rate','quote_num','turnover_rate']
    return price



# 添加 均线
def append_ma(df):
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma30'] = df['close'].rolling(window=30).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    df['ma120'] = df['close'].rolling(window=120).mean()
    
# 添加 close和均线是上升还是下降
def append_ma_direction(df):
    ma = ['close','ma5','ma10','ma20','ma30','ma60','ma120']
    y_ma = ['y_'+i for i in ma]
    ma_dir_names = [i+'_dir' for i in ma]
    for i in range(len(ma)):
        df[y_ma[i]] = df[ma[i]].shift(1)
        df.loc[df[ma[i]].notnull() & df[y_ma[i]].notnull() & (df[ma[i]]>df[y_ma[i]]),ma_dir_names[i]] = 1
        df.loc[df[ma[i]].notnull() & df[y_ma[i]].notnull() & (df[ma[i]]==df[y_ma[i]]),ma_dir_names[i]] = 0
        df.loc[df[ma[i]].notnull() & df[y_ma[i]].notnull() & (df[ma[i]]<df[y_ma[i]]),ma_dir_names[i]] = -1
        del df[y_ma[i]]
       
    
def append_line_up_down(df):
    ma = ['close','ma5','ma10','ma20','ma30','ma60','ma120']

    conditions = None
    for i in range(1,len(ma)):
        df.loc[:,'line_'+str(i+1)+'_up'] = -1
        df.loc[:,'line_'+str(i+1)+'_down'] = -1
        current_cond = (df[ma[i-1]] > df[ma[i]]) & (df[ma[i-1]+'_dir']==1) & (df[ma[i]+'_dir']==1)
        if conditions is None:
            conditions = current_cond
        else:
            conditions = conditions & current_cond
        df.loc[df[conditions].index,'line_'+str(i+1)+'_up'] = 1

        current_cond = (df[ma[i-1]] < df[ma[i]]) & (df[ma[i-1]+'_dir']==-1) & (df[ma[i]+'_dir']==-1)
        if conditions is None:
            conditions = current_cond
        else:
            conditions = conditions & current_cond
        df.loc[df[conditions].index,'line_'+str(i+1)+'_down'] = 1

    
def get_limit_date(df,win_s=2):
    '''
    根据收盘价，以win_s为窗口，计算两个窗口期前后的最大值和最小值。
    '''
    max = []
    min = []
    index = df.index.values
    for i in range(win_s,len(index)-win_s):
        if df.loc[index[i-win_s]:index[i-1],'close'].max()<df.loc[index[i],'close'] and df.loc[index[i+1]:index[i+win_s],'close'].max()<df.loc[index[i],'close']:
            max.append(df.loc[index[i],'date'])
        if df.loc[index[i-win_s]:index[i-1],'close'].min()>df.loc[index[i],'close'] and df.loc[index[i+1]:index[i+win_s],'close'].min()>df.loc[index[i],'close']:
            min.append(df.loc[index[i],'date'])
    return {'max':max,'min':min}
    
    
def draw_limit(df,dates,limit='max'):
#     if limit.startswith('max'):
#         label = 'high'
#     elif limit.startswith('min'):
#         label = 'low'
#     else:
    label = 'close'
    plt.figure(num=limit,figsize=(20,10))
    x = pd.to_datetime(df['date'])
    y = df[label].values
    plt.plot(x,y,label=label)
    x0 = pd.to_datetime(dates[limit])
    y0 = []
    for date in dates[limit]:
        y0_value = df[df['date']==date][label].values[0]
        x0_value = dt.datetime.strptime(date,'%Y-%m-%d')
        y0.append(y0_value)
        plt.annotate(date,xy=(x0_value,y0_value),xytext=(+5,+5), textcoords='offset points',rotation=45)
    plt.scatter(x0,y0,s=50,color='b')
    plt.show()
    