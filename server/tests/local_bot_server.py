from bot_server import BotServer
from bots.cs_unit import CodeSwitchStrategyName


def db_mock():
    pass


# Translate.__wrapped__.translate_to_eng = lambda self, x: x
# Translate.__wrapped__.translate_to_spa = lambda self, x: x
# Database.__wrapped__.push = lambda self, data_, guid_: db_mock()

server = BotServer(CodeSwitchStrategyName.none)
game_role = 1
guid, welcome_str = server.register(map_index=0, game_role=game_role)

print(f'bot: {welcome_str}')
while True:
    rsp, is_finish = server.call_bot(guid=guid, user_msg=input('user: '),
                                     map_idx=3,
                                     game_role=game_role,
                                     user_state={'r': 3, 'c': 9})
    for r in rsp:
        print(f'bot: {r}')
    if is_finish:
        print('Bot finished!')
        break
