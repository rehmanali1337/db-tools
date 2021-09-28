import json
from users_db import users
import motor
import asyncio
from beanie import Document, Indexed, init_beanie
import config


class User(Document):
    id: int
    username: str = None
    invite_links: list = list()
    invited_by: int = None
    join_time: int = None
    old_invites: int = 0


class InsertAsBeanieDocs:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            "mongodb://localhost:27017")
        self.init_done = False
        asyncio.get_event_loop().create_task(self._async_init())

    async def wait_until_ready(self):
        while not self.init_done:
            await asyncio.sleep(0.2)

    async def _async_init(self):
        await init_beanie(database=self.client[config.DATABASE_NAME], document_models=[User])
        self.init_done = True

    async def start(self):
        users = json.load(open('users.json'))
        for user in users:
            # print(user.to_dict())
            new_user = User(id=user["id"])
            new_user.username = user["username"]
            new_user.join_time = user["join_time"]
            new_user.invite_links = user["invite_links"]
            new_user.invited_by = user["invited_by"]
            new_user.old_invites = user["old_invites"]
            inserted = await new_user.insert()
            print(f'{inserted.id} inserted')


async def main():
    db = InsertAsBeanieDocs()
    await db.wait_until_ready()
    await db.start()

if __name__ == '__main__':
    asyncio.run(main())
