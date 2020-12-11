from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    alias = fields.CharField(max_length=256, null=True)
    language = fields.CharField(max_length=2)
    is_blocked = fields.BooleanField(default=False)
    reg_date = fields.DatetimeField(auto_now=True)
    money = fields.IntField()

    class Meta:
        table = "user"

    def __str__(self):
        return f"user_id:{self.user_id} alias:{self.alias}"

#
# class Transaction(Model):
#     id = fields.IntField(pk=True)
#     user: fields.ForeignKeyRelation[User] = fields.ForeignKeyRelation("models.User", related_name='transactions',
#                                                                       to_field="user_id")
#     amount = fields.FloatField()
#     date = fields.DatetimeField(auto_now=True)
#
#     class Meta:
#         table = "transactions"
#
#     def __str__(self):
#         return f"amount:{self.amount}"

