from datetime import datetime, timezone
from data.config import *
from tortoise import Tortoise
from .logging import logging
from loader import payeer, bot
from data.models import *
import requests
import asyncio
import hashlib
import json
import time


class AsyncUpdate:
    def __init__(self):
        pass

    async def update(self):
        counter = 0
        work_time = 0
        await Tortoise.init(db_url=DB_URL, modules={"models": ["data.models"]})  # Connecting new process to Database
        while True:  # main loop
            start_time = time.time()
            counter += 1
            # Fkwallet updater
            sign_str = FKWALLET_WALLET_CODE + FKWALLET_API_KEY
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            data = {"wallet_id": FKWALLET_WALLET_CODE, "sign": sign, "action": "get_balance"}
            res_str = requests.post("https://www.fkwallet.ru/api_v1.php", data=data)
            res = json.loads(res_str.text)
            last_amount_fk = await FkHistory.all().order_by('-id').first()
            rub_now = None
            if str(type(res)) == "<class 'dict'>":
                if "data" in res.keys():
                    rub_now = float(res['data']['RUR'])
            if rub_now is None:
                logging.error(f"{datetime.now(tz=None)} Error recieving data from Fkwallet. Response starts with "
                              f"{res_str.text[:max(len(res_str.text) - 1, 100):]}")
            else:
                # TODO add several transactions may be made between receiving updates
                if last_amount_fk.amount != float(res['data']['RUR']):
                    await FkHistory(amount=res['data']['RUR']).save()
                if last_amount_fk.amount > float(res['data']['RUR']):
                    increase = last_amount_fk.amount - float(res['data']['RUR'])
                    current_transaction = await CurrentTrans.get_or_none(amount=increase)

                    if current_transaction is None:  # Didn't found user
                        all_current_message = "FkWallet received money but didn't find person who sent money. All " \
                                              "current transactions:"
                        all_current = await CurrentTrans.all()
                        for current in all_current:
                            all_current_message += "\n" + str(current)
                        for admin in admins:
                            await bot.send_message(admin, all_current_message)
                    else:  # Found user
                        await Transaction(user_id=current_transaction.user_id, rub_amount=increase, bot_pay=False).\
                            save()
                        user = await User.get(user_id=current_transaction.user_id)
                        await User.filter(user_id=current_transaction.user_id).update(amount=(user.money + increase))
                #  If Fkwallet lost money
                elif last_amount_fk.amount < float(res['data']['RUR']):
                    if SEND_MESSAGE_IF_LOST:
                        lost = float(res['data']['RUR']) - last_amount_fk.amount
                        for admin in admins:
                            await bot.send_message(admin, f"From Fkwallet was transaction from rubles!!! Amount {lost}")

            # Payeer updater
            history = payeer.history()
            if str(type(history)) == "<class 'dict'>":
                for transaction_id in history.keys():
                    if 'comment' not in history[transaction_id].keys() or "from" not in history[transaction_id].keys():
                        continue
                    db_transaction = await Transaction.get_or_none(paying_sys_id=transaction_id)
                    if db_transaction is not None or (history[transaction_id]['from'] == PAYEER_WALLET_CODE):
                        # If transaction exists we do not process it
                        continue

                    user = await User.get_or_none(user_id=history[transaction_id]['comment'])
                    if user:
                        bot_pay = True
                        if history[transaction_id]['to'] == PAYEER_WALLET_CODE:
                            bot_pay = False
                            await User.filter(user_id=history[transaction_id]['comment']). \
                                update(money=float(user.money) + float(history[transaction_id]['creditedAmount']))

                        await Transaction(paying_sys_id=transaction_id, user_id=history[transaction_id]['comment'],
                                          rub_amount=float(history[transaction_id]['creditedAmount']), bot_pay=bot_pay). \
                            save()

            # Deleting old transactions
            all_trans = await CurrentTrans.all()
            for current in all_trans:
                now = datetime.now(timezone.utc)
                tim = str(now - current.date).split(" days, ")
                if len(tim) > 1:
                    minutes = int(tim[0] * 24 * 60) + int(tim[1].split(":")[0] * 60) + int(tim[1].split(":")[1])
                else:
                    minutes = int(tim[0].split(":")[0] * 60) + int(tim[0].split(":")[1])
                if minutes > TTL_TRANSACTION - 1:
                    await OldTrans(user_id=current.user_id, amount=current.amount, date=current.date).save()
                    await CurrentTrans.filter(id=current.id).delete()

            work_time += time.time() - start_time
            if counter % 100 == 0:
                #  Deposit updater
                config_user = await User.get(user_id=1000)
                times = ((datetime.now(timezone.utc) - config_user.reg_date).days - int(config_user.money))
                await User.filter(user_id=1000).update\
                    (money=int((datetime.now(timezone.utc) - config_user.reg_date).days))
                if times > 0:
                    users = await User.all()
                    for i in range(times):
                        for user in users:
                            if user.id == 1000:
                                continue
                            await User.filter(user_id=user.user_id).\
                                update(income=user.money * DEPOSIT_COEFFICIENT + user.income)
                # End of deposit updater

                logging.info(f"Average run for {work_time / 100}; Average sleep sleep for "
                             f"{request_each - (work_time / 100)}")
                work_time = 0

            time.sleep(request_each - (time.time() - start_time))

    def run(self):
        asyncio.run(self.update())
