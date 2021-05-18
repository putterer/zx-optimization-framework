import configparser
import os

CONFIG_FILE = "config.ini"

path = CONFIG_FILE
config = configparser.ConfigParser()
for i in range(10):
    if os.path.isfile(path):
        break
    path = os.path.join("..", path)

config.read(path)
