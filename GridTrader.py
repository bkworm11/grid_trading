import defs
import requests
import json
import time
import datetime
import logging

class OandaGrid():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.post_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/orders"
        self.open_trades_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/openTrades"
        self.pending_orders_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/pendingOrders"
        self.take_profiit_list = []

    def trade(self):

        pending_orders_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/pendingOrders"
        pending_trade_response = self.session.get(pending_orders_url, headers=defs.SECURE_HEADER)
        pending_order_list = pending_trade_response.json()["orders"]
        logger.info(f"take_profit_list: {self.take_profiit_list}")
        
        for pending_order in pending_order_list:
            if pending_order["type"] == "TAKE_PROFIT":
                self.take_profiit_list.append(pending_order["id"])
                self.take_profiit_list = list(set(self.take_profiit_list))
                
        for take_profit_order in self.take_profiit_list:
            get_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/orders/{take_profit_order}"
            response = self.session.get(get_url,headers=defs.SECURE_HEADER)
            if response.status_code == 200 and response.json()['order']['state'] == "FILLED":
                logger.info(f"order is filled {response.json()['order']['id']}")
                trade_id = response.json()['order']['tradeID']
                transaction_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/transactions/{trade_id}"
                transaction_response = self.session.get(transaction_url,headers=defs.SECURE_HEADER)
                units = transaction_response.json()['transaction']['units']                

                if int(units) > 0:
                    entry_price = float(response.json()['order']['price']) - defs.GRID_PIPS
                    units = defs.UNITS
                    take_profit_price = entry_price + defs.GRID_PIPS
                    logger.info(f"its a buy order")
                else:
                    entry_price = float(response.json()['order']['price']) + defs.GRID_PIPS
                    units = "-"+defs.UNITS
                    take_profit_price = entry_price - defs.GRID_PIPS
                    logger.info(f"its a sell order")

                limit_order_data = {
                    "order": {
                        "price": str(round(entry_price,5)),
                        "units": units,
                        "instrument": defs.FOREX_PAIR,
                        "timeInForce": "GTC",
                        "type": "LIMIT",
                        "positionFill": "DEFAULT",
                        "takeProfitOnFill": {
                            "price": str(round(take_profit_price,5))
                        }
                    }
                }
                post_response = self.session.post(self.post_url,headers=defs.SECURE_HEADER,data=json.dumps(limit_order_data))
                logger.info(f"creating limit order: {post_response.status_code}")

                self.take_profiit_list.remove(take_profit_order)


if __name__ == "__main__" :
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format, filename='log.txt')
    logger = logging.getLogger()
    trader = OandaGrid()
    counter = 0

    while True:
        try:
            trader.trade()
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=+8)
            print(f"{current_time} - running trade...{counter}")
            counter += 1
            time.sleep(1)

        except Exception as error:
            print(f"catch error: {error}")
            time.sleep(5)