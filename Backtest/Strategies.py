from backtesting import Strategy
# https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html
import talib

def candlestick_score(df_ohlc):
    candle_names = talib.get_function_groups()['Pattern Recognition']
    for candle in candle_names:
        df_ohlc[candle] = getattr(talib, candle)(df_ohlc['Open'], df_ohlc['High'], df_ohlc['Low'], df_ohlc['Close'])
    df_ohlc['candlestick_score'] = df_ohlc.iloc[:, 8:-1].sum(axis=1)

    return df_ohlc['candlestick_score']

class CP_score(Strategy):
    '''
    Candlestick Pattern Score
    Compute a score that is positive if the candlestick patterns are bullish and negative when they are bearish
    when the score becomes positive: go long
    when the score become negative: go short
    '''
    # Class variables (for optimization)
    isLong = False
    isShort = False

    def init(self):
        # Precompute elements
        self.candlestick_score = self.I(candlestick_score, self.data)
    
    def next(self):
        # long if score is positive and not already long
        if self.candlestick_score > 0 and not isLong:
            self.position.close()
            self.buy()

        # short if score is negative and not already short
        elif self.candlestick_score < 0 and not isShort:
            self.position.close()
            self.sell()




class SRCP(Strategy):
    '''
    SRCP: Support, Resistance and Candestick Patterns

    When we meet an historical support or resistance level, we sell if the candlestick pattern is bearish, we buy if the candlestick pattern is bullish

    '''
    # Class variables (for optimization)
    
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()