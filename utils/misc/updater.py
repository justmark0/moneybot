from datetime import datetime, timezone
from aiogram import Bot, types
from tortoise import Tortoise
from .logging import logging
from data.config import *
from data.models import *
from loader import payeer
from loader import _
import requests
import asyncio
import hashlib
import json
import time


class AsyncUpdate:
    def __init__(self):
        pass

    def divide_users(self, div, index, a, n, ans, sum_l):
        if index == n:
            loc_ans = []
            loc_sum = 0
            for i in range(n):
                if div[i] == 1:
                    loc_ans.append(a[i])
                    loc_sum += a[i]
            if loc_sum == sum_l:
                ans.append(loc_ans)
        else:
            for i in range(2):
                div[index] = i
                self.divide_users(div, index + 1, a, n, ans, sum_l)

    async def update(self, bot):
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
            if last_amount_fk is None:
                am = res['data']['RUR'] or 0
                await FkHistory(amount=am).save()
                last_amount_fk = await FkHistory.all().order_by('-id').first()
            rub_now = None
            if str(type(res)) == "<class 'dict'>":
                if "data" in res.keys():
                    rub_now = float(res['data']['RUR'])
            if rub_now is None:
                logging.error(f"{datetime.now(tz=None)} Error recieving data from Fkwallet. Response starts with "
                              f"{res_str.text[:max(len(res_str.text) - 1, 100):]}")
            else:
                if last_amount_fk.amount != float(res['data']['RUR']):
                    await FkHistory(amount=res['data']['RUR']).save()
                if last_amount_fk.amount < float(res['data']['RUR']):
                    increase = float(res['data']['RUR']) - last_amount_fk.amount

                    all_trans = await CurrentTrans.all()
                    div_n = len(all_trans)
                    div_list = []
                    divided = []
                    div_index = 0
                    div_working_list = [0] * div_n
                    for a in all_trans:
                        div_list.append(a.amount)
                    self.divide_users(div_working_list, div_index, div_list, div_n, divided, increase)

                    print(f"divided {divided}")

                    # current_transaction = await CurrentTrans.get_or_none(amount=float(increase))
                    if len(divided) == 0:  # Could't find users
                        all_current_message = "#warning\nFkWallet received {} rubles  but didn't find users who sent" \
                                              "money. All current transactions: ".format(increase)
                        all_current = await CurrentTrans.all()
                        for current in all_current:
                            all_current_message += "\n" + str(current)
                        for admin in admins:
                            await bot.send_message(admin, all_current_message)
                    elif len(divided) == 1:  # Found one way t divide users
                        for i in divided[0]:
                            current_transaction = await CurrentTrans.get(amount=i)
                            await Transaction(user_id=current_transaction.user_id, rub_amount=increase, bot_pay=False,
                                              system="fkwallet").save()
                            user = await User.get(user_id=current_transaction.user_id)
                            await User.filter(user_id=current_transaction.user_id).update(money=(user.money + increase))
                            await bot.send_message(current_transaction.user_id, _("Ваш счет пополнен на {} рублей").
                                                   format(increase))
                    else:  # Found more than one way to divide users
                        await bot.send_message("#error\nFkwalet got money({} rubles) and found several ways to "
                                               "distribute them between users. Here they are:".format(increase))
                        for div in divided:
                            message = ""
                            for amount in div:
                                cur_usr = await CurrentTrans.get(amount=amount)
                                usr = await User.get(user_id=cur_usr.user_id)
                                message += f"Alias: {usr.alias or ' '}; amount: {cur_usr.amount}"
                            for admin_l in admins:
                                await bot.send_message(admin_l, message)

                #  If Fkwallet lost money
                elif last_amount_fk.amount > float(res['data']['RUR']):
                    if SEND_MESSAGE_IF_LOST:
                        lost = last_amount_fk.amount - float(res['data']['RUR'])
                        for admin in admins:
                            await bot.send_message(admin, f"#info\nFrom Fkwallet was transaction from wallet in "
                                                          f"rubles!!! Amount: -{lost}")

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
                                          rub_amount=float(history[transaction_id]['creditedAmount']),
                                          bot_pay=bot_pay, system='payeer').save()

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
                counter = 0
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
            if request_each - (time.time() - start_time) > 0.5:
                time.sleep(request_each - (time.time() - start_time))

    def run(self):
        bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
        asyncio.run(self.update(bot))
