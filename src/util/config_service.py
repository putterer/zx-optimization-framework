import configparser
import os

CONFIG_FILE = "config.ini"

config = configparser.ConfigParser()
if(os.path.isfile(CONFIG_FILE)):
    config.read(CONFIG_FILE)
else:
    config.read(os.path.join("..", CONFIG_FILE))
