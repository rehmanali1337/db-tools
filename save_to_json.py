import json
from users_db import users
import config

user_list = list()

for user in users.all():
    user_dict = user.to_dict()
    user_list.append(user_dict)

with open(f'{config.DATABASE_NAME}.json', 'w') as f:
    json.dump(user_list, f)

print('All data saved to JSON file.')
