import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
from models import *
import pytz
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os
import tensorflow as tf
import numpy as np


class AutoTrading():
    def __init__(self, ACCOUNT=int, PASSWORD=str, SERVER=str, symbol=str, risk=float,) -> None:
        self.symbol = symbol
        self.risk = risk
        if not mt5.initialize():
            print("MetaTrader5 initialization failed")
            mt5.shutdown()
        if not mt5.login(ACCOUNT, PASSWORD, SERVER):
            print("Login failed")
            mt5.shutdown()
        print("ok")

    def get_last_candle_open_time(self):
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 1)
        if rates is not None and len(rates) > 0:
            return datetime.fromtimestamp(rates[0][0])
        return None

    def position_size(self, sl_price, entry_price):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Failed to get {self.symbol} info")
            return 0.01
        contract_size = symbol_info.trade_contract_size
        point = symbol_info.point
        sl_distance = abs(entry_price - sl_price)
        if sl_distance == 0:
            return 0.01
        if self.symbol == "XAUUSD":
            volume = (self.risk/100) / sl_distance
            volume = round(volume, 2)
            volume = min(max(volume, 0.01), 10.0)
        else:
            pip_value = (contract_size * point)
            if self.symbol.endswith('USD'):
                pip_value = pip_value
            elif self.symbol.startswith('USD'):
                pip_value = pip_value / entry_price
            else:
                pip_value = pip_value
            volume = 10 / (sl_distance / point * pip_value)
            volume = round(volume, 2)
            volume = min(max(volume, 0.01), 10.0)
        return volume

    def get_candle(self):
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 2, 9)
        if rates is None or len(rates) > 9:
            return None
        lis = []
        for rate in rates:
            candle = rate[4] - rate[1]

            rates_dict = {
                'open': rate[1],
                'close': rate[4],
                'candle': candle
            }
            lis.append(rates_dict)
        buy_values = [entry['candle'] for entry in lis if entry['candle'] > 0]
        sell_values = [entry['candle'] for entry in lis if entry['candle'] < 0]
        min_buy = min(buy_values) if buy_values else 0
        sum_buy = sum(buy_values) if buy_values else 0
        len_buy = len(buy_values) if buy_values else 1
        max_buy = max(buy_values) if buy_values else 0
        min_sell = min(sell_values) if sell_values else 0
        sum_sell = sum(sell_values) if sell_values else 0
        len_sell = len(sell_values) if sell_values else 1
        max_sell = max(sell_values) if sell_values else 0

        buy_values_dict = {
            'buy_values_one': min_buy,
            'buy_values_two': ((sum_buy / len_buy) + max_buy) / 2,
            'buy_values_three': sum_buy / len_buy,
            'buy_values_four': ((sum_buy / len_buy) + max_buy) / 2,
            'buy_values_five': max_buy,
        }
        sell_values_dict = {
            'sell_values_one':  min_sell,
            'sell_values_two': ((sum_sell / len_sell) + max_sell) / 2,
            'sell_values_three': sum_sell / len_sell,
            'sell_values_four': ((sum_sell / len_sell) + max_sell) / 2,
            'sell_values_five': max_sell,
        }
        candle_now = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        if candle_now is None or len(candle_now) == 0:
            return None
        candle_now = candle_now[0][4] - candle_now[0][1]
        if candle_now == 0:
            return 0    
        if buy_values_dict['buy_values_five'] < candle_now:
            return 6
        elif buy_values_dict['buy_values_four'] < candle_now <= buy_values_dict['buy_values_five']:
            return 5
        elif buy_values_dict['buy_values_three'] < candle_now <= buy_values_dict['buy_values_four']:
            return 4
        elif buy_values_dict['buy_values_two'] < candle_now <= buy_values_dict['buy_values_three']:
            return 3
        elif buy_values_dict['buy_values_one'] < candle_now <= buy_values_dict['buy_values_two']:
            return 2
        elif 0 < candle_now <= buy_values_dict['buy_values_one']:
            return 1
        elif sell_values_dict['sell_values_five'] < candle_now < 0:
            return -1
        elif sell_values_dict['sell_values_four'] < candle_now <= sell_values_dict['sell_values_five']:
            return -2
        elif sell_values_dict['sell_values_three'] < candle_now <= sell_values_dict['sell_values_four']:
            return -3
        elif sell_values_dict['sell_values_two'] < candle_now <= sell_values_dict['sell_values_three']:
            return -4
        elif sell_values_dict['sell_values_one'] < candle_now <= sell_values_dict['sell_values_two']:
            return -5
        elif candle_now <= sell_values_dict['sell_values_one']:
            return -6

    def get_candle_power(self):
        candle_1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        candle_2 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 2, 1)
        trend = candle_1[0][4] - candle_1[0][1]
        power = candle_1[0][4] - candle_2[0][2] if trend > 0 else candle_2[0][3] - candle_1[0][4] 
        power_candle = 0 if power < 0 else 1
        return power_candle
    
    def get_candle_shadow(self):
        candel = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        open_candel = candel[0][1]
        high_candel = candel[0][2]
        low_candel = candel[0][3]
        close_candel = candel[0][4]
        trend = open_candel - close_candel
        if trend < 0 :
            up_shadow = high_candel - close_candel
            down_shadow = open_candel - low_candel
            up_shadow = up_shadow / (high_candel - low_candel) 
            down_shadow = down_shadow / (high_candel - low_candel)  
            return int(str(up_shadow)[2]), int(str(down_shadow)[2])
        elif trend > 0 :
            up_shadow = high_candel - open_candel
            down_shadow = close_candel - low_candel
            up_shadow = up_shadow / (high_candel - low_candel)  
            down_shadow = down_shadow / (high_candel - low_candel)  
            return int(str(up_shadow)[2]), int(str(down_shadow)[2])
        else:
            up_shadow = 0
            down_shadow = 0
            return up_shadow, down_shadow
        
    def get_moving_average(self, period=int):
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, period)
        if rates is None or len(rates) < period:
            print("Failed to get rates.")
            return None
        list_price = []
        for rate in rates:
            list_price.append(rate['close'])
        moving_average = sum(list_price)/len(list_price)

        candle_now = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 1)
        if candle_now is None or len(candle_now) == 0:
            print("Failed to get current candle")
            return None
        pip_moving = candle_now[0][1] - moving_average
        return pip_moving

    def open_position(self, order_type, risk_reward=1.0, comment="NULL", strategy=int):
        order = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL
        enter_price = mt5.symbol_info_tick(self.symbol).ask if order == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(self.symbol).bid
        enter_candle = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        spread = (mt5.symbol_info_tick(self.symbol).ask - mt5.symbol_info_tick(self.symbol).bid)*1.5
        if strategy == 1:
            sl = round(enter_candle[0][3]-(spread) if order == mt5.ORDER_TYPE_BUY else enter_candle[0][2]+(spread/3), 2)
            tp = round(((enter_price-sl)*risk_reward)+enter_price if order == mt5.ORDER_TYPE_BUY else enter_price-((sl-enter_price)*risk_reward), 2)
        elif strategy == 2:
            tp = round(enter_candle[0][2]+(spread/3) if order == mt5.ORDER_TYPE_BUY else enter_candle[0][3]-spread, 2)
            sl = round(enter_price-((tp-enter_price)*risk_reward) if order == mt5.ORDER_TYPE_BUY else enter_price+((enter_price-tp)*risk_reward), 2)
        volume = self.position_size(sl, enter_price)
        request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": self.symbol,
        "volume": volume,
        "type": order,
        "price": enter_price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Error", result.comment)
            return None
        ticket = result.order
        return ticket

    def update_tiket_result(self):
        utc_now = datetime.now(pytz.utc)
        tz = pytz.timezone('Etc/GMT-2')
        end_date = utc_now.astimezone(tz) + timedelta(days=1)
        start_date = end_date - timedelta(days=2)
        deals = mt5.history_deals_get(start_date, end_date)
        for deal_in in deals:
            if deal_in.profit == 0 and deal_in.entry == mt5.DEAL_ENTRY_IN:
                ticket_in = deal_in.order
                try:
                    ticket_out = mt5.history_orders_get(position = ticket_in)[1][0]
                except:
                    pass
                for deal_out in deals:
                    if deal_out.profit != 0 and deal_out.entry == mt5.DEAL_ENTRY_OUT:
                        if ticket_out:
                            if deal_out.order == ticket_out:
                                profit = deal_out.profit
                                profit = 1 if profit > 0 else 0
                                update_result_buy(profit, ticket_in)
                                update_ticket_out_buy(ticket_out, ticket_in)
                                update_result_sell(profit, ticket_in)
                                update_ticket_out_sell(ticket_out, ticket_in)
                                update_result_buy2(profit, ticket_in)  
                                update_ticket_out_buy2(ticket_out, ticket_in)
                                update_result_sell2(profit, ticket_in)
                                update_ticket_out_sell2(ticket_out, ticket_in)
                                ticket_in = None
                                ticket_out = None
                                profit = None

    def int_moving(self, moving5, moving15, moving60):
        numbers = [0, moving5, moving15, moving60]
        sorted_numbers = sorted(numbers)  
        scores = {value: rank for rank, value in enumerate(sorted_numbers)}
        return [scores[0], scores[moving5], scores[moving15], scores[moving60]]
    
async def send_telegram(text):
    load_dotenv()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await bot.send_message(chat_id=os.getenv("CHANEL"), text=text)  
 
async def run_bot(ACCOUNT, PASSWORD, SERVER, symbol, risk, risk_reward, run):
    trade = AutoTrading(ACCOUNT, PASSWORD, SERVER, symbol, risk)
    init_db()
    model_buy = tf.keras.models.load_model('buy.h5')
    model_sell = tf.keras.models.load_model('sell.h5')
    await send_telegram('Connecting to MetaTrader5')
    last_candle_open_time = trade.get_last_candle_open_time()
    start_time = datetime.strptime("01:00", "%H:%M").time()
    end_time = datetime.strptime("04:00", "%H:%M").time()
    day = 5
    while True:
        if run == 1 and start_time <= last_candle_open_time.time() <= end_time:
            await asyncio.sleep(1)
            current_open_time = trade.get_last_candle_open_time()
            candle = trade.get_candle()
            power = trade.get_candle_power()
            up_shadow, down_shadow = trade.get_candle_shadow()
            moving5 = trade.get_moving_average(5)
            moving15 = trade.get_moving_average(15)
            moving60 = trade.get_moving_average(60)
            int_moving = trade.int_moving(moving5, moving15, moving60)
            if current_open_time != last_candle_open_time:
                if candle is not None:
                    if candle > 0 and moving15 > 0:
                        trade_id = save_buy1(candle, power, int(int_moving[0]), int(int_moving[1]), int(int_moving[2]), int(int_moving[3]))
                        X = np.array([[candle, power, int(int_moving[0]), int(int_moving[1]), int(int_moving[2]), int(int_moving[3])]])
                        result_Ai = model_buy.predict(X)
                        result_Ai = int(np.argmax(result_Ai))
                        comment = f"Buy-{str(trade_id)}"
                        ticket_in = trade.open_position("BUY", risk_reward, comment, 1)
                        if ticket_in:
                            update_ticket_buy(trade_id, "opened", ticket_in, result_Ai, day)
                            await send_telegram(f"{comment} order is opened")
                        else:
                            update_ticket_buy(trade_id, "not opened", ticket_in, result_Ai, day)
                            await send_telegram(f"{comment} order not opened")
                        if result_Ai == 0:
                            trade_id = save_sell2(candle, power, up_shadow, down_shadow, int(int_moving[0]), int(int_moving[1]), int(int_moving[2]), int(int_moving[3]))
                            comment = f"Sell-{str(trade_id)} and Strategy-2"
                            ticket_in = trade.open_position("SELL", risk_reward, comment, 2)
                            if ticket_in:
                                update_ticket_sell2(trade_id, "opened", ticket_in, None, day)
                            else:
                                update_ticket_sell2(trade_id, "not opened", ticket_in, None, day)

                    elif candle < 0 and moving15 < 0:
                        trade_id = save_sell1(abs(candle), power, int(int_moving[0]), int(int_moving[1]), int(int_moving[2]), int(int_moving[3]))
                        X = np.array([[candle, power, int(int_moving[0]), int(int_moving[1]), int(int_moving[2]), int(int_moving[3])]])
                        result_Ai = model_sell.predict(X)
                        result_Ai = int(np.argmax(result_Ai))
                        comment = f"Sell-{str(trade_id)}"
                        ticket_in = trade.open_position("SELL", risk_reward, comment, 1)
                        if ticket_in:
                            update_ticket_sell(trade_id, "opened", ticket_in, result_Ai, day)
                            await send_telegram(f"{comment} order is opened")
                        else:
                            update_ticket_sell(trade_id, "not opened", ticket_in, result_Ai, day)
                            await send_telegram(f"{comment} order not opened")
                        if result_Ai == 0:
                            trade_id = save_buy2(candle, power, up_shadow, down_shadow, int(int_moving[0]), int(int_moving[1]), int(int_moving[2]), int(int_moving[3]))
                            comment = f"Buy-{str(trade_id)} and Strategy-2"
                            ticket_in = trade.open_position("BUY", risk_reward, comment, 2)

                            if ticket_in:
                                update_ticket_buy2(trade_id, "opened", ticket_in, None, day)
                            else:
                                update_ticket_buy2(trade_id, "not opened", ticket_in, None, day)

                    else:
                        trade.update_tiket_result()
                last_candle_open_time = current_open_time
        else:
            last_candle_open_time = trade.get_last_candle_open_time()
            trade.update_tiket_result()

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(run_bot(int(os.getenv("ACCOUNT")), os.getenv("PASSWORD"), os.getenv("SERVER"), 'XAUUSD', 2.0, 1.0, 1))
