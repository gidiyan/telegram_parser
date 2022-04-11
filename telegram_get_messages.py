import configparser
import json
from datetime import date, datetime, timedelta

import pytz
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)


def main():
    # some functions to parse json date
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()

            if isinstance(o, bytes):
                return list(o)

            return json.JSONEncoder.default(self, o)

    # Reading Configs
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Setting configuration values
    api_id = int(config['Telegram']['api_id'])
    api_hash = config['Telegram']['api_hash']

    api_hash = str(api_hash)

    phone = config['Telegram']['phone']
    username = config['Telegram']['username']

    # Create the client and connect
    client = TelegramClient(username, api_id, api_hash)

    all_id = []
    last_id = 0
    new_line = 'Команди з актуальними цілями на ' + datetime.now().strftime("%Y-%h-%d %H:%M:%S") + '\n'
    with open('./commands.txt', 'r') as f:
        lines = f.readlines()

    with open('./commands.txt', 'w') as f:
        for line in lines:
            if "Команди з актуальними цілями" in line:
                old_line = line
                line = line.replace(old_line, new_line)
            f.write(line)

    # Get last message id
    def get_last_id():
        id_data = json.load(open('channel_messages.json', 'r'))
        for item in id_data:
            all_id.append(item['id'])
        last_id = max(all_id)
        if last_id == '':
            last_id = 0
        return last_id

    print("Getting last today's messages fro channel\n")

    # main script
    async def start(phone):
        await client.start()
        print("Client For Getting Today's Messages Created")
        print('------------------')
        # Ensure you're authorized
        if await client.is_user_authorized() == False:
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Password: '))
        me = await client.get_me()
        user_input_channel = '1601423054'  # input('enter entity(telegram URL or entity id):')
        if user_input_channel.isdigit():
            entity = PeerChannel(int(user_input_channel))
        else:
            entity = user_input_channel
        my_channel = await client.get_entity(entity)

        offset_id = 0
        limit = 100
        all_messages = []
        total_count_limit = 0

        while True:
            # print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
            history = await client(GetHistoryRequest(
                peer=my_channel,
                offset_id=offset_id,
                offset_date=datetime.now(),
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                if str(date.today() - timedelta(days=0)) in str(message.date.astimezone(pytz.UTC)):
                    if message.id >= last_id:
                        all_messages.append(message.to_dict())
            offset_id = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break

        with open('channel_messages.json', 'w') as outfile:
            json.dump(all_messages, outfile, cls=DateTimeEncoder, ensure_ascii=False)

    with client:
        client.loop.run_until_complete(start(phone))

    filein = open('channel_messages.json', 'r')
    data = json.load(filein)
    for item in data:
        if 'message' in item.keys():
            print(item['date'])
            print(item['message'])
            print(item['id'])
            print('------------------')

    async def send_message(phone):
        await client.start()
        print("Client For Sending Messages Created")
        print('------------------')
        if await client.is_user_authorized() == False:
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Password: '))
        user_input_channel = '1601423054'  # input('enter entity(telegram URL or entity id):')
        if user_input_channel.isdigit():
            entity = PeerChannel(int(user_input_channel))
        else:
            entity = user_input_channel
        print(get_last_id())
        commands = open('commands.txt', 'r').read()
        script = open('script.txt', 'r').read()
        await client.send_message(entity, commands, comment_to=get_last_id())
        await client.send_message(entity, script, comment_to=get_last_id())

    with client:
        client.loop.run_until_complete(send_message(phone))


if __name__ == '__main__':
    main()
