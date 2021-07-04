from pyrogram import Client 
import config,getopt,sys,os

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
    
app = Client(
    ":memory:",
    bot_token=config.CONFIG['Token'],
    plugins=dict(root="modules"),
)

app.run()
