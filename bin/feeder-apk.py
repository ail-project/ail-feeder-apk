import os 
import argparse
import configparser
import lmdb
from pyail import PyAIL
from pathlib import Path

parentFolder = Path(__file__).resolve().parent.parent
pathConf = os.path.join(parentFolder, "etc/ail-feeder-apk.cfg")

uuid = "6afb365f-a0ec-48c2-bed9-1e82942cc0b7"

if os.path.isfile(pathConf):
    config = configparser.ConfigParser()
    config.read(pathConf)
else:
    print("[-] No conf file found")
    exit(-1)

if 'general' in config:
    uuid = config['general']['uuid']

if 'ail' in config:
    ail_url = config['ail']['url']
    ail_key = config['ail']['apikey']
else:
    print("Need AIL config")
    exit()

if 'lmdb' in config:
    huntdb = config['lmdb']['huntdb']
    if not os.path.isabs(huntdb):
        huntdb = os.path.join(parentFolder, huntdb)
else:
    print("Need huntting database")
    exit()
    

def pushToAil(data, meta):
    """Push json to AIL"""
    default_encoding = 'UTF-8'

    source = 'apk-feeder'
    source_uuid = uuid

    pyail.feed_json_item(meta, data, source, source_uuid, default_encoding)

try:
    pyail = PyAIL(ail_url, ail_key, ssl=False)
except Exception as e:
    print("\n\n[-] Error during creation of AIL instance")
    exit(0)

env = lmdb.open(huntdb, readonly = True)
with env.begin() as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        pushToAil(key.decode('utf-8'),value.decode('utf-8'))

env.close()