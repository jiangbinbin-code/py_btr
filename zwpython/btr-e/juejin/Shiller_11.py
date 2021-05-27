# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
import numpy as np
from gm.api import *
'''
通过计算两个真实价格序列回归残差的0.9个标准差上下轨,并在价差突破上轨的时候做空价差,价差突破下轨的时候做多价差
并在回归至标准差水平内的时候平仓
回测数据为:DCE.m1801和DCE.m1805的1min数据
回测时间为:2017-09-25 08:00:00到2017-10-01 15:00:00
'''
def init(context):
    context.goods = ['DCE.m1801', 'DCE.m1805']
    # 订阅品种数据
    subscribe(symbols = context.goods,frequency = '1d',count = 31,wait_group = True)
def on_bar(context, bars):
    # 获取历史数据
    close_1801 = context.data(symbol=context.goods[0], frequency='1d', count=31, fields='close')['close'].values
    close_1805 = context.data(symbol=context.goods[1], frequency='1d', count=31, fields='close')['close'].values
    # 计算上下轨
    spread = close_1801[:-2] - close_1805[:-2]
    spread_new = close_1801[-1] - close_1805[-1]
    up = np.mean(spread) + 0.75 * np.std(spread)
    down = np.mean(spread) - 0.75 * np.std(spread)
    up_stop = np.mean(spread) + 2 * np.std(spread)
    down_stop = np.mean(spread) - 2 * np.std(spread)
    # 获取仓位
    position1801_long = context.account().position(symbol = context.goods[0],side =PositionSide_Long)
    position1801_short = context.account().position(symbol = context.goods[0],side =PositionSide_Short)
    # 没有仓位时
    if not position1801_short and not position1801_long:
        # 上穿上轨时，买近卖远
        if spread_new > up:
            order_volume(symbol=context.goods[0], volume=1, order_type=OrderType_Market, side=OrderSide_Buy, position_effect=PositionEffect_Open)
            order_volume(symbol=context.goods[1], volume=1, order_type=OrderType_Market, side=OrderSide_Sell, position_effect=PositionEffect_Open)
            print('上穿上轨，买近卖远')
        # 下穿下轨时，卖近买远
        if spread_new < down:
            order_volume(symbol=context.goods[0], volume=1, order_type=OrderType_Market, side=OrderSide_Sell, position_effect=PositionEffect_Open)
            order_volume(symbol=context.goods[1], volume=1, order_type=OrderType_Market, side=OrderSide_Buy, position_effect=PositionEffect_Open)
            print('下穿下轨，卖近买远')
    # 价差回归到上轨时，平仓
    if position1801_long:
        if spread_new <= np.mean(spread):
            order_close_all()
            print('价差回归，平仓')
        if spread_new > up_stop:
            order_close_all()
            print('达到止损点，全部平仓')
    # 价差回归到下轨时，平仓
    if position1801_short:
        if spread_new >= np.mean(spread):
            order_close_all()
            print('价差回归，平全部仓')
        if spread_new < down_stop:
            order_close_all()
            print('达到止损点，全部平仓')
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
        token='token_id',
        backtest_start_time='2017-07-01 08:00:00',
        backtest_end_time='2017-12-31 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=2000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)