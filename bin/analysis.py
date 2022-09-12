from fingerprinter import androguard_fingerprinter
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

    if 'lmdb' in config:
        scrapdb = config['lmdb']['scrapdb']
        if not os.path.isabs(scrapdb):
            scrapdb = os.path.join(parentFolder, scrapdb)
        huntdb = config['lmdb']['huntdb']
        if not os.path.isabs(scrapdb):
            huntdb = os.path.join(parentFolder, huntdb)
        baselinedb = config['lmdb']['baselinedb']
        if not os.path.isabs(baselinedb):
            baselinedb = os.path.join(parentFolder, baselinedb)
    
    if 'filter' in config:
        certificate = config['filter']['certificatessha256'].split(',')
        publisher = config['filter']['publisher'].split(',')

    if 'scrapper' in config:
        bk = config['scrapper']['baselinekeywords']
        hk = config['scrapper']['huntkeywords']

    if 'bloomfilter' in config:
        bfpath = config['bloomfilter']['bfpath']
        if not os.path.isabs(bfpath):
            bfpath = os.path.join(parentFolder, bfpath)
        case = config['bloomfilter']['case']

    if 'raccoon' in config:
        homefolder = config['raccoon']['homefolder']

    if len(sys.argv) != 2:
        print("Usage : analysis mode")
        exit()
    else:
        mode = sys.argv[1]
        if mode:
            androguard_fingerprinter.generate_lmdb_report(mode, bk, hk, certificate, scrapdb, huntdb, baselinedb, certificate, publisher, bfpath, case, homefolder)