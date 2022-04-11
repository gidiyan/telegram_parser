Script for parsing messages from public group [IT ARMY of UKRAINE](https://t.me/itarmyofukraine2022)


<details>
  <summary> Description </summary>
- Script for automatic parsing messages from official public itarmyofukraine2022
- Is parsing IP,ports,HTTP links
- Creates lst files and pushes to git backuping files .lst before rewriting them
- Publishes messages with predefined formating and text in response to latest message in public
- Fill config.ini with credentials from [API Developers Tools](https://my.telegram.org/auth?to=apps) and ready to start
- Exaples of messages to post are in TXT files
</details>

#### Launch

    python3 -m pip install -r requirements.txt
    python3 telegram_messages_parser.py
    
