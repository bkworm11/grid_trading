import defs
import requests
import json


session = requests.Session()
post_url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/orders"
get_recent_price_url = f"{defs.OANDA_URL}/instruments/{defs.INSTRUMENT}/candles?count=1&price=M&granularity=S5"
result = session.get(get_recent_price_url,headers=defs.SECURE_HEADER)
current_price = float(result.json()['candles'][0]['mid']['o'])
print(current_price)


current_grid = current_price + defs.GRID_PIPS
while current_grid < defs.GRID_MAX:
    print(f"current grid price: {current_grid}")
    limit_order_data = {
            "order": {
                "price": str(round(current_grid, 5)),
                "units": "-"+defs.UNITS,
                "instrument": defs.FOREX_PAIR,
                "timeInForce": "GTC",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "takeProfitOnFill": {
                    "price": str(round(current_grid-defs.GRID_PIPS, 5))
                }
            }
        }
    post_response = session.post(post_url,headers=defs.SECURE_HEADER,data=json.dumps(limit_order_data))
    current_grid += defs.GRID_PIPS


current_grid_min = current_price - defs.GRID_PIPS
while current_grid_min > defs.GRID_MIN:
    print(f"current grid price: {current_grid_min}")
    limit_order_data = {
            "order": {
                "price": str(round(current_grid_min, 5)),
                "units": defs.UNITS,
                "instrument": defs.FOREX_PAIR,
                "timeInForce": "GTC",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "takeProfitOnFill": {
                    "price": str(round(current_grid_min+defs.GRID_PIPS, 5))
                }
            }
        }
    post_response = session.post(post_url,headers=defs.SECURE_HEADER,data=json.dumps(limit_order_data))
    current_grid_min -= defs.GRID_PIPS