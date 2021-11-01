import vk_bots

TOKEN = 'TOKEN'

lp = vk_bots.LongPollManager.LongPollServer(TOKEN, 204308254, wait=90)

while True:
    print(lp.update())
    print('──────────')
