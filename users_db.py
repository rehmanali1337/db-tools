from pymodm.manager import Manager
from pymodm.queryset import QuerySet
from pymodm.connection import connect
import config
from pymodm import MongoModel, fields


db = connect(f"mongodb://localhost:27017/{config.DATABASE_NAME}")


class UsersQuerySet(QuerySet):
    def get_link_owner(self, link):
        return self.raw({"invite_links": {'$eq': link}}).first()

    def get_users_after(self, timestamp):
        return list(self.raw({"join_time": {"$gte": timestamp}}))

    def get_user_by_id(self, user_id):
        return self.raw(dict(_id=user_id)).first()

    def get_new_invites(self, user):
        if isinstance(user, int):
            user = self.get_user_by_id(user)
        new = len(list(self.raw(dict(invited_by=user.pk))))
        return new

    def get_user_invites(self, user):
        if isinstance(user, int):
            user = User(id=user)
        return list(self.raw(dict(invited_by=user.pk)))

    def erase_invites(self, user_id):
        users = self.raw(dict(invited_by=user_id))
        for user in users:
            user.invited_by = None
            user.save()

    def erase_everything(self):
        self.delete()


UsersQuerySetManager = Manager.from_queryset(UsersQuerySet)


class User(MongoModel):
    id = fields.IntegerField(primary_key=True)
    username = fields.CharField()
    invite_links = fields.ListField()
    invited_by = fields.ReferenceField('User', blank=True)
    join_time = fields.IntegerField(blank=True)
    old_invites = fields.IntegerField(default=0)
    objects: UsersQuerySet = UsersQuerySetManager()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "invite_links": self.invite_links,
            "invited_by": self.invited_by.id if self.invited_by is not None else None,
            "join_time": self.join_time,
            "old_invites": self.old_invites,
        }


users = User.objects
