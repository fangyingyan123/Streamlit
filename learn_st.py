from ctypes.wintypes import SIZE
import re
from turtle import color, down
import streamlit as st
import numpy as np
import pandas as pd
from loglog.connect import Connect
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import cufflinks as cf
import plotly.offline as plyo
from pyecharts.charts import Bar
from pyecharts.faker import Faker
import streamlit_echarts
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from typing import List, Union
from pyecharts.charts import Kline, Line, Bar, Grid
import streamlit.components.v1 as components

st.title("my first app")
# @st.cache
def load_data():
    #读取数据
    data1 = pd.read_excel('C:/Users/Administrator/Desktop/工作表单/_100.xlsx')
    #将数据转化成目标格式
    data2 = data1[['end_date','open','highest','lowest','close','volume']]
    data2.columns=['trade_date','open','high','low','close','volume']
    return data2

def plot_cand_volume(data,dt_breaks):
    data.columns=['date','open','high','low','close','volume']
    # Create subplots and mention plot grid size
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                   vertical_spacing=0.03, subplot_titles=('', '成交量'), 
                   row_width=[0.2, 0.7])

    # 绘制k数据
    fig.add_trace(go.Candlestick(x=data["date"], open=data["open"], high=data["high"],
                    low=data["low"], close=data["close"], 
                    increasing=dict(line=dict(color = '#ef232a')),
                    decreasing=dict(line=dict(color = '#14b143')),
                    name=""), 
                    row=1, col=1
    )

    # 绘制成交量数据
    fig.add_trace(go.Bar(x=data['date'], y=data['volume'], showlegend=False), row=2, col=1)

    fig.update_xaxes(
        title_text = 'k线图',
        rangeslider_visible = True, # 下方滑动条缩放
        rangeselector = dict(
            # 增加固定范围选择
            buttons = list([
                dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
                dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
                dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
                dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
                dict(step = 'all')])))
    # Do not show OHLC's rangeslider plot 
    fig.update(layout_xaxis_rangeslider_visible=False)
    # 去除休市的日期，保持连续
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
    return fig

def plt_kline_echart(data):
    data2 = data[['date','open','close','high','low']]
    data2.columns=['t','open','close','high','low']

    date = data2["t"].apply(lambda x: str(x)).tolist()
    k_plot_value = data2[['open','close','high','low']].values.tolist()


    kline11 = (
        Kline()
        .add_xaxis(xaxis_data=date)
        .add_yaxis(
            series_name="",
            y_axis=k_plot_value,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
        )

        .set_global_opts(
            title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),#有操作工具
            
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
                ),
                opts.DataZoomOpts(
                    is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100
                ),
                opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
            ],
            # 三个图的 axis 连在一块
            # axispointer_opts=opts.AxisPointerOpts(
            #     is_show=True,
            #     link=[{"xAxisIndex": "all"}],
            #     label=opts.LabelOpts(background_color="#777"),
            # ),
        )
        
    )

    return kline11




def calculate_ma(day_count: int, data):
    result: List[Union[float, str]] = []
    for i in range(len(data["values"])):
        if i < day_count:
            result.append("-")
            continue
        sum_total = 0.0
        for j in range(day_count):
            sum_total += float(data["values"][i - j][1])
        result.append(abs(float("%.3f" % (sum_total / day_count))))
    return result


def draw_charts(data):
    category_data =pd.to_datetime(data['trade_date']).dt.strftime("%Y-%m-%d").tolist()
    data2 = data[['trade_date','open','close','high','low','volume']]
    data2.columns=['t','open','close','high','low','volume']
    values = data2[['t','open','close','high','low','volume']].values.tolist()
    volumes = []
    for i, tick in enumerate(values):
        volumes.append([i, tick[4], 1 if tick[1] > tick[2] else -1])
    chart_data = {"categoryData": category_data, "values": values, "volumes": volumes}

    kline_data = [data[1:-1] for data in chart_data["values"]]
    kline = (
        Kline()
        .add_xaxis(xaxis_data=chart_data["categoryData"])
        .add_yaxis(
            series_name="Dow-Jones index",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
            markpoint_opts=opts.MarkPointOpts(
            label_opts=opts.LabelOpts(
                color = '#fff'
            ),
            data = [opts.MarkPointItem(
                type_ = 'max',
                name = '最大值'
            ),opts.MarkPointItem(
                type_ = 'min',
                name = '最小值'
            )]
        )

        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(
                is_show=False, pos_bottom=10, pos_left="center"
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 1],
                    range_start=98,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1],
                    type_="slider",
                    pos_top="85%",
                    range_start=98,
                    range_end=100,
                ),
            ],
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True),#有操作工具
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                dimension=2,
                series_index=5,
                is_piecewise=True,
                pieces=[
                    {"value": 1, "color": "#00da3c"},
                    {"value": -1, "color": "#ec0000"},
                ],
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            brush_opts=opts.BrushOpts(
                x_axis_index="all",
                brush_link="all",
                out_of_brush={"colorAlpha": 0.1},
                brush_type="lineX",
            ),
        )
    )

    line = (
        Line()
        .add_xaxis(xaxis_data=chart_data["categoryData"])
        .add_yaxis(
            series_name="MA5",
            y_axis=calculate_ma(day_count=5, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA10",
            y_axis=calculate_ma(day_count=10, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA20",
            y_axis=calculate_ma(day_count=20, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA30",
            y_axis=calculate_ma(day_count=30, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )

    bar = (
        Bar()
        .add_xaxis(xaxis_data=chart_data["categoryData"])
        .add_yaxis(
            series_name="Volume",
            y_axis=chart_data["volumes"],
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="k线图", subtitle={'688208'}),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                grid_index=1,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                is_scale=True,
                split_number=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    # Kline And Line
    overlap_kline_line = kline.overlap(line)

    # Grid Overlap + Bar
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1000px",
            height="800px",
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    grid_chart.add(
        overlap_kline_line,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="50%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="63%", height="16%"
        ),
    )
    return grid_chart




if __name__ == '__main__':
    #读取数据
    df = load_data()
    # 展示数据的前五行
    st.table(df.head())
    # 右侧选项
    event_list = ['688208']
    event_type = st.sidebar.selectbox(
        "Which kind of event do you want to explore?",
        event_list
    )

    # 剔除不交易日期 解决k线不连续的现象
    dt_all = pd.date_range(start=df['trade_date'].iloc[0],end=df['trade_date'].iloc[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    trade_date = list(pd.to_datetime(df['trade_date']).dt.strftime('%Y-%m-%d'))
    dt_breaks = list(set(dt_all) - set(trade_date))
    # 画第一个k线，这里是用plotly画的
    fig1 = plot_cand_volume(df,dt_breaks)
    st.plotly_chart(fig1, use_container_width=True)

    #画第二个图  用streamlit_echarts画
    kline1 = plt_kline_echart(df)
    streamlit_echarts.st_pyecharts(kline1,theme=ThemeType.DARK)
    # st.line_chart(df[['open','close','high','low']])

    #画第三个图  用streamlit_echarts画不一样的
    df = load_data()
    kline2 = draw_charts(df)
    streamlit_echarts.st_pyecharts(kline2,height="1000px")
    kline2.render('k线.html')


    


