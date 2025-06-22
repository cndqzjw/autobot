# 项目名：AutoTrader
## 目标：实现SOL/USDT自动双向量化交易
## 模块：
- main.py：主程序，循环执行策略
- trader.py：封装OKX下单、查询、撤单等功能
- strategy.py：包含趋势判断、开仓平仓策略
- notifier.py：发送Telegram消息通知
...
## 计划：
- 补全日志记录器
- 添加策略回测器
- Flask仪表盘展示收益图
