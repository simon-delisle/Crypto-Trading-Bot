import numpy as np
import plotly.graph_objs as go
print('Modules imported')

class technical_analysis:

    def isFarFromLevel(self, l, s, levels):
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        return self.np.sum([abs(l-x) < s  for x in levels]) == 0


    def is_support(low, i):
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        support = low[i] < low[i-1]  and low[i] < low[i+1] and low[i+1] < low[i+2] and low[i-1] < low[i-2] 
        return support
    def is_resistance(high, i):
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        resistance = high[i] > high[i-1]  and high[i] > high[i+1] and high[i+1] > high[i+2] and high[i-1] > high[i-2]
        return resistance


    def find_support(self, high, low):
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        levels = []
        levels_to_now=[]
        for i in range(2,low.shape[0]-2):
            if self.is_support(low,i):
                s =  self.np.mean(high - low)
                l = low[i]
                levels_to_now.append((i, l))
                if self.isFarFromLevel(l, s, levels_to_now):
                    levels.append((i, l))
        return levels

    def find_resistance(self, high, low): 
        '''
        source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        '''
        levels = []
        levels_to_now=[]
        for i in range(2,high.shape[0]-2):
            if self.is_support(high,i):
                s =  self.np.mean(high - low)
                l = high[i]
                levels_to_now.append((i, l))
                if self.isFarFromLevel(l, s, levels_to_now):
                    levels.append((i, l))
                
        return levels

    def candlestick_chart(self, title, time, open, high, low, close, volume, show_support=False, show_resistance=False):
        '''
        inputs: in series format except title which is a string
        returns: plotly fig
        '''
        print('self:', self)
        print('title: ', title)
        fig = go.Figure()

        fig.add_trace(self.go.Candlestick(x=time, # pd.to_datetime(df['datetime'], unit='ns')
                        open=open, high=high,
                        low=low, close=close),
                    secondary_y=False)

        # include a go.Bar trace for volumes
        '''
        fig.add_trace(self.go.Bar(x=time, y=volume),
            secondary_y=True)
        fig.update_traces(marker=dict(opacity=0.3),
                    selector=dict(type="bar"))
        '''


        # Include support if required
        if show_support:
            support_levels = self.find_support(high, low)
            for level in support_levels:
                fig.add_hline(
                    y=level[1],
                    line_color='blue'
                )
        # Include resistance if required
        if show_resistance:
            resistance_levels = self.find_resistance(high, low)
            for level in resistance_levels:
                fig.add_hline(
                    y=level[1],
                    line_color='orange'
                )


        



        fig.layout.yaxis2.showgrid=False
        fig.update_yaxes(title_text="Price (USD)", secondary_y=False)
        fig.update_yaxes(title_text="Volume", secondary_y=True)

        fig.update_layout(
            title=title,
            width=1600, height=800)
        
        return fig
    
    
