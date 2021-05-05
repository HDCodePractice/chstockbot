from telegram.ext import Updater
import mysystemd
import os
import getopt
import sys
import config


def help():
    return "'bot.py -c <configpath>'"


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg          

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    updater = Updater(CONFIG['Token'], use_context=True)
    dispatcher = updater.dispatcher

    me = updater.bot.get_me()
    CONFIG['ID'] = me.id
    CONFIG['Username'] = '@' + me.username
    config.set_default()
    print(f"Starting... ID: {str(CONFIG['ID'])} , Username: {CONFIG['Username']}")

    commands = []
    # 在这里加入功能
    # from cmdproc import admincmd
    # commands += admincmd.add_dispatcher(dispatcher)
    from cmdproc import groupcmd
    commands += groupcmd.add_dispatcher(dispatcher)

    updater.bot.set_my_commands(commands)

    updater.start_polling()
    print('Started...')
    mysystemd.ready()

    updater.idle()
    print('Stopping...')
    print('Stopped.')