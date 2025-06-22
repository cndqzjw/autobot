
架构：

sol_auto_trader/

├── main.py                # 启动主程序

├── strategy.py            # 策略模块（含双向交易）

├── trader.py              # 交易封装类（OKX操作）

├── notifier.py            # Telegram通知模块

├── config.py              # 配置文件（账号、策略参数）

├── logs/

│		├── trade_log.jsonl    # 交易日志

│		└── price_log.jsonl    # 行情日志（可选）

├── backtest.py            # 回测与复盘分析工具

├── requirements.txt       # 依赖项列表

└── README.md              # 使用说明文档

项目要求：

做多开平，做空开平
实盘执行OKX现货杠杆，sol-usdt
Telegram通知
交易日志，行情日志，回测接口
费用考虑，费率和最小费用
根据账户内额度进行合理分配交易
