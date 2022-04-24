import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
print('Custom module <technical_indicators> imported')
from importlib import import_module
import math
import pandas as pd
import talib

# TODO: use the find sr weight function to replace the similar code in the candlestick function

class technical_analysis():

    def __init__(self):
        pass
    
    def isFarFromLevel(self, l, s, levels):
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        return np.sum([abs(l-x) < s  for x in levels]) == 0


    def is_support(self, low, i):
        '''

        modified from source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        support = low[i] < low[i-1]  and low[i] < low[i+1] and low[i+1] < low[i+2] and low[i-1] < low[i-2] 
        return support
    def is_resistance(self, high, i):
        '''

        modified from source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        resistance = high[i] > high[i-1]  and high[i] > high[i+1] and high[i+1] > high[i+2] and high[i-1] > high[i-2]
        return resistance

    def is_local_min(self, low, i):
        '''
        The point is a local min if its lowest point is lower that the 3 candles on its right and the 3 candles on its left
        '''
        local_min = low[i] < low[i-1] and low[i] < low[i-2] and low[i] < low[i-3] and low[i] < low[i+1] and low[i] < low[i+2] and low[i] < low[i+3]
        return local_min


    def is_local_max(self, high, i):
        '''
        The point is a local min if its highest point is higher that the 3 candles on its right and the 3 candles on its left
        '''
        local_max = high[i] > high[i-1] and high[i] > high[i-2] and high[i] > high[i-3] and high[i] > high[i+1] and high[i] > high[i+2]and high[i] > high[i+3]
        return local_max

    def find_support(self, high, low):
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        levels = []
        levels_to_now=[]
        for i in range(2,low.shape[0]-2):
            if self.is_support(low,i):
                s =  np.mean(high - low)
                l = low[i]
                levels_to_now.append((i, l))
                # TODO levels do not work, returns an empty list
                if self.isFarFromLevel(l, s, levels_to_now):
                    levels.append((i, l))
        return levels_to_now

    def find_resistance(self, high, low): 
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        levels = []
        levels_to_now=[]
        for i in range(2,high.shape[0]-2):
            if self.is_resistance(high,i):
                s =  np.mean(high - low)
                l = high[i]
                levels_to_now.append((i, l))
                # TODO levels do not work, returns an empty list
                if self.isFarFromLevel(l, s, levels_to_now):
                    levels.append((i, l))
                
        return levels_to_now

    def find_local_min(self, low):
        local_mins = []
        for i in range(3, low.shape[0]-3):
            if self.is_local_min(low, i):
                local_mins.append((i, low[i]))
        return local_mins

    def find_local_max(self, high):
        local_maxs = []
        for i in range(3, high.shape[0]-3):
            if self.is_local_max(high, i):
                local_maxs.append((i, high[i]))
        return local_maxs

    def find_support_and_resistance_weight(self, low, high, weight_support_and_resistance_zones):
        min = low.min()
        max = high.max()
        rectangle_height = (max - min) / weight_support_and_resistance_zones
        # add rectangles to the chart
        sr_weight = []
        for i in range(weight_support_and_resistance_zones):
            # define the zone for support and resistance counting
            y0 = min + i*rectangle_height
            y1 = min + (i+1)*rectangle_height
            y_min_check = min + (i-1)*rectangle_height
            y_max_check = min + (i+2)*rectangle_height
            # get support and resistance in proce data
            support_levels = self.find_support(high, low)
            resistance_levels = self.find_resistance(high, low)
            local_mins = self.find_local_min(low)
            local_maxs = self.find_local_max(high)
            # count the number of support and resistance occurences in each zone
            support = [(x[0], x[1]) for x in support_levels if x[1] >= y_min_check and x[1] <= y_max_check]
            resistance = [(x[0], x[1]) for x in resistance_levels if x[1] >= y_min_check and x[1] <= y_max_check]
            local_min = [(x[0], x[1]) for x in local_mins if x[1] >= y_min_check and x[1] <= y_max_check]
            local_max = [(x[0], x[1]) for x in local_maxs if x[1] >= y_min_check and x[1] <= y_max_check]
            weight = len(support) + len(resistance) + len(local_min) + len(local_max)
            sr_weight.append(y0, y1, weight)
            df_sr = pd.DataFrame(sr_weight, columns=['Lower Bound', 'Higher Bound', 'SR Weight'])
        
        return df_sr, sr_weight

    def find_candlestick_patterns(self, df_ohlc):
        candle_names = talib.get_function_groups()['Pattern Recognition']
        for candle in candle_names:
            df_ohlc[candle] = getattr(talib, candle)(df_ohlc['Open'], df_ohlc['High'], df_ohlc['Low'], df_ohlc['Close'])
    
        return df_ohlc

    def candlestick_chart(self, title, time, open, high, low, close, volume, 
                            show_support=False, show_resistance=False, show_local_mins=False, show_local_maxs=False, 
                            weight_support_and_resistance=False, weight_support_and_resistance_zones=100, candlestick_score=[]):
        '''
        inputs: in series format except title which is a string
        returns: plotly fig
        '''

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        #fig = go.Figure()

        fig.add_trace(go.Candlestick(
                            name='Price (USD)',
                            x=time, 
                            open=open, high=high,
                            low=low, close=close,
                        ),
                        secondary_y=False
                    )
        
        fig.add_trace(go.Bar(
                            name='candlestick score',
                            x=time,
                            y=candlestick_score, 
                        ),
                        secondary_y=False
                    )


        # include a go.Bar trace for volumes
        fig.add_trace(go.Bar(
                            name='Volume (USD)',
                            x=time, 
                            y=volume
                        ),
                        secondary_y=True
                    )
        fig.update_traces(marker=dict(opacity=0.3),
                    selector=dict(type="bar"))


        # Include support if required
        if show_support:
            support_levels = self.find_support(high, low)
            for level in support_levels:
                x0 = time.iloc[level[0]]
                try:
                    x1 = time.iloc[level[0]+3]
                except Exception as e:
                    print(e)
                y0 = int(round(level[1]*0.99, 0))
                y1 = int(round(level[1]*0.99, 0))
                fig.add_shape(type="line",
                    xref="x", yref="y",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(
                        color="blue",
                    )
                )
                
        # Include resistance if required
        if show_resistance:
            resistance_levels = self.find_resistance(high, low)
            for level in resistance_levels:
                x0 = time.iloc[level[0]]
                try:
                    x1 = time.iloc[level[0]+3]
                except Exception as e:
                    print(e)
                y0 = int(round(level[1]*1.01, 0))
                y1 = int(round(level[1]*1.01, 0))
                fig.add_shape(type="line",
                    xref="x", yref="y",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(
                        color="orange",
                    )
                )

        # Include local mins if required
        if show_local_mins:
            local_mins = self.find_local_min(low)
            for min in local_mins:
                x0 = time.iloc[min[0]]
                try:
                    x1 = time.iloc[min[0]+3]
                except Exception as e:
                    print(e)
                y0 = min[1]
                y1 = min[1]
                fig.add_shape(type="line",
                    xref="x", yref="y",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(
                        color="green",
                    )
                )

        # Include local mins if required
        if show_local_maxs:
            local_maxs = self.find_local_max(high)
            for max in local_maxs:
                x0 = time.iloc[max[0]]
                try:
                    x1 = time.iloc[max[0]+3]
                except Exception as e:
                    print(e)
                y0 = max[1]
                y1 = max[1]
                fig.add_shape(type="line",
                    xref="x", yref="y",
                    x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(
                        color="red",
                    )
                )

        # weight support and resistance importance
        if weight_support_and_resistance:
            # split the zone in the chart between min and max data into 100 horizontal rectangles
            min = low.min()
            max = high.max()
            rectangle_height = (max - min) / weight_support_and_resistance_zones
            # add rectangles to the chart
            support_and_resistance_weights = []
            for i in range(weight_support_and_resistance_zones):
                # define rectangles dimensions
                y0 = min + i*rectangle_height
                y1 = min + (i+1)*rectangle_height
                y_min_check = min + (i-1)*rectangle_height
                y_max_check = min + (i+2)*rectangle_height
                # get the rectangles color
                support = [(x[0], x[1]) for x in support_levels if x[1] >= y_min_check and x[1] <= y_max_check]
                resistance = [(x[0], x[1]) for x in resistance_levels if x[1] >= y_min_check and x[1] <= y_max_check]
                local_min = [(x[0], x[1]) for x in local_mins if x[1] >= y_min_check and x[1] <= y_max_check]
                local_max = [(x[0], x[1]) for x in local_maxs if x[1] >= y_min_check and x[1] <= y_max_check]
                rectangle_weight = len(support) + len(resistance) + len(local_min) + len(local_max)
                
                # draw rectangle in figure if higher than treshold
                if rectangle_weight < 4:
                    rectangle_weight=0
                # add rectangles in figure
                fig.add_hrect(
                    y0=y0, y1=y1,
                    fillcolor='purple',
                    opacity=rectangle_weight*0.05
                )

        fig.layout.yaxis2.showgrid=False
        fig.update_yaxes(title_text="Price (USD)", secondary_y=False)
        fig.update_yaxes(title_text="Volume", secondary_y=True)

        fig.update_layout(
            title=title,
            width=1400, height=800)
        
        return fig
    
    
