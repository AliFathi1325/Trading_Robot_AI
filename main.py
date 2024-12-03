import MetaTrader5 as mt5
from datetime import datetime, timedelta, date, timezone
from models import *
import pytz
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os
import tensorflow as tf
import numpy as np
import pandas_ta as ta
import pandas as pd



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
    
    def get_day(self):
        today = date.today()     # گرفتن تاریخ امروز
        day_of_week = today.weekday()     # گرفتن روز هفته (0=دوشنبه, 6=یکشنبه)
        return day_of_week

    def get_hour(self):
        utc_time = datetime.now(timezone.utc)   # گرفتن زمان فعلی به وقت UTC
        hour = utc_time.hour    # استخراج ساعت
        return hour 

    def get_candle(self):
        candle = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        if candle is None or len(candle) == 0:
            return None
        open_candle, close_candle = candle[0][1], candle[0][4]
        trend = open_candle - close_candle
        if trend == 0 :
             return 0
        if trend < 0 :
            return 1
        if trend > 0 :
            return 2

    def get_candle_power(self):
        old_candles = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 2, 9)
        list_all = []
        for old_candle in old_candles:
            open_candle = old_candle[1]
            high_candle = old_candle[2]
            low_candle = old_candle[3]
            close_candle = old_candle[4]
            volume_candle = old_candle[5]
            trend = open_candle - close_candle
            if trend > 0:
                up_shadow = high_candle - open_candle
                down_shadow = close_candle - low_candle
                up_shadow = up_shadow / (high_candle - low_candle) * 100
                down_shadow = down_shadow / (high_candle - low_candle) * 100
                candle_body = 100 - up_shadow
                score = candle_body * volume_candle * trend
                list_all.append(score)
            elif trend < 0:
                up_shadow = high_candle - close_candle
                down_shadow = open_candle - low_candle
                up_shadow = up_shadow / (high_candle - low_candle) * 100
                down_shadow = down_shadow / (high_candle - low_candle) * 100
                candle_body = 100 - down_shadow
                score = candle_body * volume_candle * abs(trend)
                list_all.append(score)
        new_candle = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        open_candle = new_candle[0][1]
        high_candle = new_candle[0][2]
        low_candle = new_candle[0][3]
        close_candle = new_candle[0][4]
        volume_candle = new_candle[0][5]
        trend = close_candle - open_candle
        new_score = 0 
        men_score = sum(list_all) / len(list_all) if list_all else 1  
        if trend > 0:
            up_shadow = high_candle - open_candle
            down_shadow = close_candle - low_candle
            up_shadow = up_shadow / (high_candle - low_candle) * 100
            down_shadow = down_shadow / (high_candle - low_candle) * 100
            candle_body = 100 - up_shadow
            new_score = candle_body * volume_candle * trend
        elif trend < 0:
            up_shadow = high_candle - close_candle
            down_shadow = open_candle - low_candle
            up_shadow = up_shadow / (high_candle - low_candle) * 100
            down_shadow = down_shadow / (high_candle - low_candle) * 100
            candle_body = 100 - down_shadow
            new_score = candle_body * volume_candle * abs(trend)
        if men_score == 0:
            score = 0
        else:
            score = round(new_score / men_score * 100)
        return score
    
    def get_candle_close(self):
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
        elif trend >= 0 :
            up_shadow = high_candel - open_candel
            down_shadow = close_candel - low_candel
        up_shadow = round(up_shadow / (high_candel - low_candel) * 100)
        down_shadow = round(down_shadow / (high_candel - low_candel) * 100)
        return up_shadow, down_shadow

    def get_macd_state(self):
        # دریافت 20 کندل اخیر برای نماد موردنظر
        data = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 20)
        # تبدیل داده‌ها به دیتافریم
        data = pd.DataFrame(data)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        # محاسبه مقادیر MACD
        macd = ta.macd(data['close'], fast=6, slow=13, signal=5)
        data = pd.concat([data, macd], axis=1)  # افزودن ستون‌های MACD به داده‌ها
        # دریافت اطلاعات آخرین کندل
        last_row = data.iloc[-1]
        macd_line = last_row['MACD_6_13_5']
        signal_line = last_row['MACDs_6_13_5']
        macd_histogram = last_row['MACDh_6_13_5']
        # تعیین وضعیت MACD برای آخرین کندل
        if macd_line > 0 and signal_line > 0 and macd_histogram > 0:
            state = 100  # روند صعودی قوی
        elif macd_line < 0 and signal_line < 0 and macd_histogram < 0:
            state = 0  # روند نزولی قوی
        elif macd_line > signal_line and macd_histogram > 0:
            state = 80  # سیگنال صعودی قوی
        elif macd_line > signal_line and macd_histogram < 0:
            state = 60  # سیگنال صعودی ضعیف
        elif macd_line < signal_line and macd_histogram < 0:
            state = 20  # سیگنال نزولی قوی
        elif macd_line < signal_line and macd_histogram > 0:
            state = 40  # سیگنال نزولی ضعیف
        elif (macd_line > signal_line and macd_histogram > 0 and
            last_row['close'] < data['close'].iloc[-2]):
            state = 90  # واگرایی مثبت (معکوس صعودی)
        elif (macd_line < signal_line and macd_histogram < 0 and
            last_row['close'] > data['close'].iloc[-2]):
            state = 10  # واگرایی منفی (معکوس نزولی)
        else:
            state = 50  # حالت خنثی یا نامشخص
        return state  # بازگرداندن وضعیت MACD برای آخرین کندل

    def get_adx_state(self):
        # دریافت ۲۰ کندل اخیر برای محاسبات ADX
        data = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 20)
        # تبدیل داده‌ها به دیتافریم
        data = pd.DataFrame(data)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        # محاسبه ADX
        adx = ta.adx(data['high'], data['low'], data['close'], length=9)
        data = pd.concat([data, adx], axis=1)  # افزودن ستون‌های ADX به داده‌ها
        # دریافت اطلاعات آخرین کندل
        last_row = data.iloc[-1]
        adx_value = last_row['ADX_9']
        di_plus = last_row['DMP_9']
        di_minus = last_row['DMN_9']
        # تعیین وضعیت ADX برای آخرین کندل
        if adx_value > 25:
            if di_plus > di_minus:
                state = 100  # روند قوی صعودی
            elif di_minus > di_plus:
                state = 0  # روند قوی نزولی
        elif adx_value < 25:
            if di_plus > di_minus:
                state = 75  # روند ضعیف صعودی
            elif di_minus > di_plus:
                state = 25  # روند ضعیف نزولی
            else:
                state = 50  # بازار بدون روند
        else:
            state = 50  # حالت نامشخص
        return state  # بازگرداندن وضعیت ADX برای آخرین کندل

    def get_rsi_state(self):
        # دریافت داده‌های کندل‌ها
        data = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 20)
        # تبدیل به DataFrame
        data = pd.DataFrame(data)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        # محاسبه RSI
        data['rsi'] = ta.rsi(data['close'], length=9)
        # دریافت اطلاعات آخرین کندل
        last_row = data.iloc[-1]
        last_rsi = last_row['rsi']
        prev_rsi = data['rsi'].iloc[-2]  # مقدار RSI کندل قبلی
        # تعیین وضعیت RSI
        if last_rsi > 70:
            state = 100  # اشباع خرید
        elif last_rsi < 30:
            state = 0  # اشباع فروش
        elif last_rsi > 50 and last_rsi > prev_rsi:
            state = 75  # روند صعودی
        elif last_rsi < 50 and last_rsi < prev_rsi:
            state = 25  # روند نزولی
        elif last_rsi == 50:
            state = 50  # محدوده میانه
        elif 30 <= last_rsi <= 70:
            state = 50  # حالت خنثی
        else:
            state = 50  # حالت نامشخص
        return state  # بازگرداندن وضعیت RSI برای آخرین کندل

    def get_moving_average(self, period=int):
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, period)
        if rates is None or len(rates) < period:
            return None
        list_price = []
        for rate in rates:
            list_price.append(rate['close'])
        moving_average = sum(list_price)/len(list_price)
        return moving_average

    def get_moving_map(self, moving_average=int):
        candels = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 60)
        if candels is None or len(candels) > 60:
            print(None)
        list_price = []
        for candle in candels:
            list_price.append(candle[2])
            list_price.append(candle[3])
        price_map = max(list_price) - min(list_price)
        moving_map = moving_average - min(list_price)
        anser = round(moving_map / price_map * 100)
        return anser

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

    def open_position(self, order_type, risk_reward=1.0, comment="NULL", strategy=int):
        order = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL
        enter_price = mt5.symbol_info_tick(self.symbol).ask if order == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(self.symbol).bid
        enter_candle = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 1, 1)
        spread = (mt5.symbol_info_tick(self.symbol).ask - mt5.symbol_info_tick(self.symbol).bid)*1.5
        if strategy == 1:
            sl = round(enter_candle[0][3]-(spread) if order == mt5.ORDER_TYPE_BUY else enter_candle[0][2]+(spread), 2)
            tp = round(((enter_price-sl)*risk_reward)+enter_price if order == mt5.ORDER_TYPE_BUY else enter_price-((sl-enter_price)*risk_reward), 2)
        elif strategy == 2:
            tp = round(enter_price+((enter_price-enter_candle[0][1])*risk_reward)+spread if order == mt5.ORDER_TYPE_BUY else enter_price+((enter_candle[0][3]-enter_price)*risk_reward)-spread, 2)
            sl = round(enter_price+((enter_price-enter_candle[0][1]))-spread if order == mt5.ORDER_TYPE_BUY else enter_price-((enter_candle[0][3]-enter_price))+spread, 2)
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
                ticket_out = None
                try:
                    ticket_out = mt5.history_orders_get(position=ticket_in)[1][0]
                except IndexError:
                    ticket_out = None
                except Exception as e:
                    print(f"Error fetching ticket_out: {e}")
                    ticket_out = None
                if ticket_out:
                    for deal_out in deals:
                        if deal_out.profit != 0 and deal_out.entry == mt5.DEAL_ENTRY_OUT:
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
    
async def send_telegram(text):
    load_dotenv()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    try:
        await bot.send_message(chat_id=os.getenv("CHANEL"), text=text)
    except Exception as e:
        print(f"Failed to send message: {e}")
 
async def run_bot(ACCOUNT, PASSWORD, SERVER, symbol, risk, risk_reward, run):
    trade = AutoTrading(ACCOUNT, PASSWORD, SERVER, symbol, risk)
    init_db()
    modelBuyBuy = tf.keras.models.load_model('BuyBuy.h5')
    modelBuySell = tf.keras.models.load_model('BuySell.h5')
    modelSellSell = tf.keras.models.load_model('SellSell.h5')
    modelSellBuy = tf.keras.models.load_model('SellBuy.h5')
    await send_telegram("conecting to MetaTrader5...")
    last_candle_open_time = trade.get_last_candle_open_time()
    start_time = datetime.strptime("01:30", "%H:%M").time()
    end_time = datetime.strptime("10:30", "%H:%M").time()
    while True:
        if run == 1 and start_time <= last_candle_open_time.time() <= end_time:
            await asyncio.sleep(1)
            current_open_time = trade.get_last_candle_open_time()
            if current_open_time != last_candle_open_time:
                day = trade.get_day()
                hour = trade.get_hour()
                candle = trade.get_candle()
                power = trade.get_candle_power()
                close = trade.get_candle_close()
                up_shadow, down_shadow = trade.get_candle_shadow()
                macd = trade.get_macd_state()
                adx = trade.get_adx_state()
                rsi = trade.get_rsi_state()
                price_map = trade.get_moving_map(trade.get_moving_average(1))
                moving15 = trade.get_moving_map(trade.get_moving_average(15))
                moving30 = trade.get_moving_map(trade.get_moving_average(30))
                moving45 = trade.get_moving_map(trade.get_moving_average(45))
                moving60 = trade.get_moving_map(trade.get_moving_average(60))
                X = np.array([[power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi]])
                last_candle_open_time = trade.get_last_candle_open_time()
                if candle is not None:
                    if candle == 1:
                        id_buy = save_buy_buy(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                        id_sell = save_buy_sell(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                        comment_buy = f"Buy-Buy->{str(id_buy)}"
                        comment_sell = f"Buy-Sell->{str(id_sell)}"
                        ticket_in_buy = trade.open_position("BUY", risk_reward, comment_buy, 1)
                        ticket_in_sell = trade.open_position("SELL", risk_reward, comment_sell, 2)
                        result_Ai = int(np.argmax(modelBuyBuy.predict(X)))
                        if result_Ai == 1:
                            id_buy_AI = save_buy_buy(day, hour, 2, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                            comment_buy_AI = f"Buy-Buy-AI->{str(id_buy)}"
                            ticket_in_buy_AI = trade.open_position("BUY", 2, comment_buy_AI, 1)
                            if ticket_in_buy_AI:
                                update_ticket_buy(id_buy_AI, "opened", ticket_in_buy_AI, None)
                                await send_telegram(f"{comment_buy_AI} order is opened")
                            else:
                                update_ticket_buy(id_buy_AI, "not opened", ticket_in_buy_AI, None)
                                await send_telegram(f"{comment_buy_AI} order not opened")
                        print('--------------------')
                        if ticket_in_buy:
                            update_ticket_buy(id_buy, "opened", ticket_in_buy, result_Ai)
                            await send_telegram(f"{comment_buy} order is opened")
                        else:
                            update_ticket_buy(id_buy, "not opened", ticket_in_buy, result_Ai)
                            await send_telegram(f"{comment_buy} order not opened")
                        result_Ai = int(np.argmax(modelBuySell.predict(X)))
                        if result_Ai == 1:
                            id_sell_AI = save_buy_sell(day, hour, 2, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                            comment_sell_AI = f"Buy-Sell-AI->{str(id_sell_AI)}"
                            ticket_in_sell_AI = trade.open_position("SELL", 2, comment_sell_AI, 2)
                            if ticket_in_sell_AI:
                                update_ticket_sell2(id_sell_AI, "opened", ticket_in_sell_AI, None)
                                await send_telegram(f"{comment_sell_AI} order is opened")
                            else:
                                update_ticket_sell2(id_sell_AI, "not opened", ticket_in_sell_AI, None)
                                await send_telegram(f"{comment_sell_AI} order not opened")
                        print('--------------------')
                        if ticket_in_sell:
                            update_ticket_sell2(id_sell, "opened", ticket_in_sell, result_Ai)
                            await send_telegram(f"{comment_sell} order is opened")
                        else:
                            update_ticket_sell2(id_sell, "not opened", ticket_in_sell, result_Ai)
                            await send_telegram(f"{comment_sell} order not opened")
                        trade.update_tiket_result()
                    elif candle == 2: 
                        id_sell = save_sell_sell(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                        id_buy = save_sell_buy(day, hour, candle, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                        comment_sell = f"Sell-Sell->{str(id_buy)}"
                        comment_buy = f"Sell-Buy->{str(id_sell)}"
                        ticket_in_sell = trade.open_position("SELL", risk_reward, comment_sell, 1)
                        ticket_in_buy = trade.open_position("BUY", risk_reward, comment_buy, 2)
                        result_Ai = result_Ai = int(np.argmax(modelSellSell.predict(X)))
                        if result_Ai == 1:
                            id_sell_AI = save_sell_sell(day, hour, 1, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                            comment_sell_AI = f"Sell-Sell-AI->{str(id_sell_AI)}"
                            ticket_in_sell_AI = trade.open_position("SELL", 2, comment_sell_AI, 1)
                            if ticket_in_sell_AI:
                                update_ticket_sell(id_sell_AI, "opened", ticket_in_sell_AI, None)
                                await send_telegram(f"{comment_sell_AI} order is opened")
                            else:
                                update_ticket_sell(id_sell_AI, "not opened", ticket_in_sell_AI, None)
                                await send_telegram(f"{comment_sell_AI} order not opened")
                        print('--------------------')
                        if ticket_in_sell:
                            update_ticket_sell(id_sell, "opened", ticket_in_sell, result_Ai)
                            await send_telegram(f"{comment_sell} order is opened")
                        else:
                            update_ticket_sell(id_sell, "not opened", ticket_in_sell, result_Ai)
                            await send_telegram(f"{comment_sell} order not opened")
                        result_Ai = result_Ai = int(np.argmax(modelSellBuy.predict(X)))
                        if result_Ai == 1:
                            id_buy_AI = save_sell_buy(day, hour, 1, power, close, up_shadow, down_shadow, price_map, moving15, moving30, moving45, moving60, macd, adx, rsi)
                            comment_buy_AI = f"Sell-Buy-AI->{str(id_buy_AI)}"
                            ticket_in_buy_AI = trade.open_position("BUY", 2, comment_buy_AI, 2)
                            if ticket_in_buy_AI:
                                update_ticket_buy2(id_buy_AI, "opened", ticket_in_buy_AI, None)
                                await send_telegram(f"{comment_buy_AI} order is opened")
                            else:
                                update_ticket_buy2(id_buy_AI, "not opened", ticket_in_buy_AI, None)
                                await send_telegram(f"{comment_buy_AI} order not opened")
                        if ticket_in_buy:
                            update_ticket_buy2(id_buy, "opened", ticket_in_buy, result_Ai)
                            await send_telegram(f"{comment_buy} order is opened")
                        else:
                            update_ticket_buy2(id_buy, "not opened", ticket_in_buy, result_Ai)
                            await send_telegram(f"{comment_sell} order not opened")
                        trade.update_tiket_result()
        else:
            last_candle_open_time = trade.get_last_candle_open_time()
            trade.update_tiket_result()

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(run_bot(int(os.getenv("ACCOUNT")), os.getenv("PASSWORD"), os.getenv("SERVER"), 'XAUUSD', 2.0, 1.0, 1))
