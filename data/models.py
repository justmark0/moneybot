from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    alias = fields.CharField(max_length=256, null=True)
    language = fields.CharField(max_length=2)
    is_blocked = fields.BooleanField(default=False)
    reg_date = fields.DatetimeField(auto_now=True)
    money = fields.FloatField()

    class Meta:
        table = "user"

    def __str__(self):
        return f"user_id:{self.user_id} alias:{self.alias}"


class Transaction(Model):
    id = fields.IntField(pk=True)
    paying_sys_id = fields.BigIntField(index=True)
    user_id = fields.BigIntField()
    rub_amount = fields.FloatField()
    date = fields.DatetimeField(auto_now=True)
    bot_pay = fields.BooleanField()  # Bot receives money if it is False. Bot sending money if True
    wallet_number = fields.CharField(max_length=512, null=True)

    class Meta:
        table = "transactions"

    def __str__(self):
        return f"user_id:{self.user_id} rub_amount:{self.rub_amount}"
