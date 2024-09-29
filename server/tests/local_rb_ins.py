from bots.rule_based.rule_based_bot_ins import RuleBasedBotInstructor
from google_cloud.database import Database


def db_mock():
    pass


Database.__wrapped__.save_cs_state = lambda self, g, x, y: db_mock()

map_index = 0
map_id = f'map_{map_index + 1}'
bot = RuleBasedBotInstructor(map_id)

while True:
    rsp, is_finish = bot.call(user_msg=input('user: '),
                              user_state={'r': 3, 'c': 9})
    for r in rsp:
        print(f'bot: {r}')
    if is_finish:
        print('Bot finished!')
        break
