# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import numpy as np
def init(context):
    # 选择的两个合约
    context.symbol = ['DCE.j1901', 'DCE.jm1901']
    # 订阅历史数据
    subscribe(symbols=context.symbol,frequency='1d',count=11,wait_group=True)
def on_bar(context, bars):
    # 数据提取
    j_close = context.data(symbol=context.symbol[0],frequency='1d',fields='close',count=31).values
    jm_close = context.data(symbol=context.symbol[1],frequency='1d',fields='close',count=31).values
    # 提取最新价差
    new_price = j_close[-1] - jm_close[-1]
    # 计算历史价差,上下限，止损点
    spread_history = j_close[:-2] -  jm_close[:-2]
    context.spread_history_mean = np.mean(spread_history)
    context.spread_history_std = np.std(spread_history)
    context.up = context.spread_history_mean + 0.75 * context.spread_history_std
    context.down = context.spread_history_mean - 0.75 * context.spread_history_std
    context.up_stoppoint = context.spread_history_mean + 2 * context.spread_history_std
    context.down_stoppoint = context.spread_history_mean - 2 * context.spread_history_std
    # 查持仓
    position_jm_long = context.account().position(symbol=context.symbol[0],side=1)
    position_jm_short = context.account().position(symbol=context.symbol[0],side=2)
    # 设计买卖信号
    # 设计开仓信号
    if not position_jm_short and not position_jm_long:
        if new_price > context.up:
            print('做空价差组合')
            order_volume(symbol=context.symbol[0],side=OrderSide_Sell,volume=1,order_type=OrderType_Market,position_effect=1)
            order_volume(symbol=context.symbol[1], side=OrderSide_Buy, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Open)
        if new_price < context.down:
            print('做多价差组合')
            order_volume(symbol=context.symbol[0], side=OrderSide_Buy, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Open)
            order_volume(symbol=context.symbol[1], side=OrderSide_Sell, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Open)
    # 设计平仓信号
    # 持jm多仓时
    if position_jm_long:
        if new_price >= context.spread_history_mean:
            # 价差回归到均值水平时，平仓
            print('价差回归到均衡水平，平仓')
            order_volume(symbol=context.symbol[0], side=OrderSide_Sell, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
            order_volume(symbol=context.symbol[1], side=OrderSide_Buy, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
        if new_price < context.down_stoppoint:
            # 价差达到止损位，平仓止损
            print('价差超过止损点，平仓止损')
            order_volume(symbol=context.symbol[0], side=OrderSide_Sell, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
            order_volume(symbol=context.symbol[1], side=OrderSide_Buy, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
    # 持jm空仓时
    if position_jm_short:
        if new_price <= context.spread_history_mean:
            # 价差回归到均值水平时，平仓
            print('价差回归到均衡水平，平仓')
            order_volume(symbol=context.symbol[0], side=OrderSide_Buy, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
            order_volume(symbol=context.symbol[1], side=OrderSide_Sell, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
        if new_price > context.up_stoppoint:
            # 价差达到止损位，平仓止损
            print('价差超过止损点，平仓止损')
            order_volume(symbol=context.symbol[0], side=OrderSide_Buy, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
            order_volume(symbol=context.symbol[1], side=OrderSide_Sell, volume=1, order_type=OrderType_Market, position_effect=PositionEffect_Close)
if __name__ == '__main__':
    '''
    strategy_id策略ID,由系统生成
    filename文件名,请与本文件名保持一致
    mode实时模式:MODE_LIVE回测模式:MODE_BACKTEST
    token绑定计算机的ID,可在系统设置-密钥管理中生成
    backtest_start_time回测开始时间
    backtest_end_time回测结束时间
    backtest_adjust股票复权方式不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
    backtest_initial_cash回测初始资金
    backtest_commission_ratio回测佣金比例
    backtest_slippage_ratio回测滑点比例
    '''
    run(strategy_id='strategy_id',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='token',
        backtest_start_time='2018-02-01 08:00:00',
        backtest_end_time='2018-12-31 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=2000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)