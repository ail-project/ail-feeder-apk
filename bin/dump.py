import lmdb
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("apk", help="Database to dump")
args = parser.parse_args()

if not args.apk:
    print("give me a database")

else:
    env = lmdb.open(args.apk, readonly = True)

    with env.begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            print(value.decode('utf-8'))

env.close()