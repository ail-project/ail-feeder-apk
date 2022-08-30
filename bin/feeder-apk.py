import os 
import argparse
import configparser
import lmdb
from pyail import PyAIL

dir_path = os.path.dirname(os.path.realpath(__file__))
uuid = "6afb365f-a0ec-48c2-bed9-1e82942cc0b7"

## Config
pathConf = '../etc/ail-feeder-apk.cfg'

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


def pushToAIl(data, meta):
    """Push json to AIL"""
    default_encoding = 'UTF-8'

    json_pdf = dict()
    json_pdf['data'] = data
    json_pdf['meta'] = meta

    source = 'apk-feeder'
    source_uuid = uuid

    if debug:
        print(json_pdf)
    else:
        pyail.feed_json_item(data, meta, source, source_uuid, default_encoding)


#############
# Arg Parse #
#############

parser = argparse.ArgumentParser()
parser.add_argument("database", help="lmdb folder to open")
parser.add_argument("-v", "--verbose", help="display more info", action="store_true")
args = parser.parse_args()

verbose = args.verbose

## Ail
try:
    pyail = PyAIL(ail_url, ail_key, ssl=False)
except Exception as e:
    print("\n\n[-] Error during creation of AIL instance")
    exit(0)

if not args.database:
    print("Error passing database file")
    exit(0)
elif args.database:
    env = lmdb.open(args.database, readonly = True)
    with env.begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            print(value.decode('utf-8'))

    env.close()

    #pushToAIl(data, meta)
