from scrapper import download
import sys
import os
import configparser
import pathlib
import pdb

if __name__ == '__main__':

    parentFolder = pathlib.Path(__file__).resolve().parent.parent
    pathConf = os.path.join(parentFolder, "etc/ail-feeder-apk.cfg")

    ## Config
    if os.path.isfile(pathConf):
        config = configparser.ConfigParser()
        config.read(pathConf)
    else:
        print("[-] No conf file found")
        exit(-1)

    if 'lmdb' in config:
        scrapdb = config['lmdb']['scrapdb']
        if not os.path.isabs(scrapdb):
            scrapdb = os.path.join(parentFolder, scrapdb)
        huntdb = config['lmdb']['huntdb']
        if not os.path.isabs(scrapdb):
            huntdb = os.path.join(parentFolder, huntdb)

    if 'scrapper' in config:
        baselinekeywords = config['scrapper']['baselinekeywords'].split(',')
        huntkeywords = config['scrapper']['huntkeywords'].split(',')
        certificatessha1 = config['scrapper']['certificatessha1'].split(',')
        limit = int(config['scrapper']['max_reviews'])

    if 'raccoon' in config:
        exe = config['raccoon']['exe']

    if len(sys.argv) != 2:
        print("Usage : download_apks mode")
        exit()
    else:
        mode = sys.argv[1]
        if mode:
            download.download_task(mode, scrapdb, huntdb, exe)