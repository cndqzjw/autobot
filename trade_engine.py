from config import config
from trader import Trader
from strategy import Strategy

if __name__ == '__main__':
    trader = Trader(config)
    strategy = Strategy(trader)
    strategy.run_loop()