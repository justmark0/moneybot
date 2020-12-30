from data.config import *
from tortoise import Tortoise
from .logging import logging
from loader import payeer, bot
from data.models import *
from datetime import datetime
import requests
import asyncio
import hashlib
import json
import time


class AsyncUpdate:
    def __init__(self):
        pass

    async def update(self):
        await Tortoise.init(db_url=DB_URL, modules={"models": ["data.models"]})  # Connecting new process to Database
        while True:  # main loop
            start_time = time.time()

            # Fkwallet updater
            sign_str = FKWALLET_WALLET_CODE + FKWALLET_API_KEY
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            data = {"wallet_id": FKWALLET_WALLET_CODE, "sign": sign, "action": "get_balance"}
            res_str = requests.post("https://www.fkwallet.ru/api_v1.php", data=data)
            res = json.loads(res_str.text)
            last_amount_fk = await FkHistory.all().order_by('-id').first()
            all = await FkHistory.all()
            print(all)
            rub_now = None
            if str(type(res)) == "<class 'dict'>":
                if "data" in res.keys():
                    rub_now = float(res['data']['RUR'])
            if rub_now is None:
                logging.error(f"{datetime.now(tz=None)} Error recieving data from Fkwallet. Response starts with "
                              f"{res_str.text[100::]}")
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
                    # TODO make getting money by user (Change amount of user and create transaction)
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

            # TODO check if users can reg several times. If yes. Delete duplicates each 100 cycles

            logging.info(f"run for {time.time() - start_time} will sleep for {request_each - (time.time() - start_time)}")
            time.sleep(request_each - (time.time() - start_time))

    def run(self):
        asyncio.run(self.update())
