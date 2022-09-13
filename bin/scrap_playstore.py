from scrapper import scrap
import sys
import os
import configparser
import pathlib

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

    if 'scrapper' in config:
        bk = config['scrapper']['baselinekeywords']
        hk = config['scrapper']['huntkeywords']
        limit = int(config['scrapper']['max_reviews'])

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

    if len(sys.argv) != 2:
        print("Usage : scrap_playstore mode")
        exit()
    else:
        mode = sys.argv[1]
        if mode:
            scrap.scrap_task(mode, bk, hk, limit, scrapdb, huntdb, baselinekeywords, huntkeywords)

