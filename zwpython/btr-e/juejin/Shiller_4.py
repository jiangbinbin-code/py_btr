# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta
"""
小市值策略
本策略每个月触发一次，计算当前沪深市场上市值最小的前30只股票，并且等权重方式进行买入。
对于不在前30的有持仓的股票直接平仓。
回测时间为：2018-07-01 08:00:00 到 2020-10-01 16:00:00 
"""
def init(context):
    # 每月第一个交易日的09:40 定时执行algo任务（仿真和实盘时不支持该频率）
    schedule(schedule_func=algo, date_rule='1m', time_rule='09:40:00')
    # 使用多少的资金来进行开仓
    context.ratio = 0.8
    # 定义股票池数量
    context.num = 30
def algo(context):
    # 获取当前时间
    now = context.now
    # 获取筛选时间：date1表示当前日期之前的100天，date2表示当前时间
    date1 = (context.now - timedelta(days=100)).strftime("%Y-%m-%d %H:%M:%S")
    date2 = context.now.strftime("%Y-%m-%d %H:%M:%S")
    # 通过get_instruments获取所有的上市股票代码
    all_stock = get_instruments(exchanges='SHSE, SZSE', sec_types=[1], fields='symbol, listed_date, delisted_date',
                                df=True)
    # 剔除停牌和st股和上市不足100日的新股和退市股和B股
    code = all_stock[(all_stock['listed_date'] < date1) & (all_stock['delisted_date'] > date2) &
                            (all_stock['symbol'].str[5] != '9') & (all_stock['symbol'].str[5] != '2') & (stockall['symbol']['sec_type'] == '1')]
    # 获取所有股票市值
    fundamental = get_fundamentals_n('trading_derivative_indicator', code['symbol'].to_list(),
                                     context.now, fields='TOTMKTCAP', count=1, df=True).sort_values('TOTMKTCAP')
    # 对市值进行排序（升序），并且获取前30个。 最后将这个series 转化成为一个list即为标的池
    trade_symbols = fundamental.reset_index(drop=True).loc[:context.num - 1, 'symbol'].to_list()
    print('本次股票池有股票数目: ', len(trade_symbols))
    # 计算每个个股应该在持仓中的权重
    percent = 1.0 / len(trade_symbols) * context.ratio
    # 获取当前所有仓位
    positions = context.account().positions()
    # 平不在标的池的仓位
    for position in positions:
        symbol = position['symbol']
        if symbol not in trade_symbols:
            order_target_percent(symbol=symbol, percent=0, order_type=OrderType_Market,
                                 position_side=PositionSide_Long)
            print('市价单平不在标的池的', symbol)
    # 将标中已有持仓的和还没有持仓的都调整到计算出来的比例。
    for symbol in trade_symbols:
        order_target_percent(symbol=symbol, percent=percent, order_type=OrderType_Market,
                             position_side=PositionSide_Long）
        print(symbol, '以市价单调整至权重', percent)
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
        backtest_start_time='2005-01-01 08:00:00',
        backtest_end_time='2020-10-01 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=1000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)