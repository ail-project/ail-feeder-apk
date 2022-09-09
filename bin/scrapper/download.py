import lmdb
import subprocess
import time

def download_task(mode, scrapdb, huntdb, exe):
    env: lmdb.Environment
    if mode == "baselining":
        env = lmdb.open(scrapdb, readonly = True)

    elif mode == "hunting":
        env = lmdb.open(huntdb, readonly = True)

    with env.begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            process = subprocess.Popen(['java', '-jar', exe, '--gpa-download', key[4:].decode()], 
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
            while True:
                output = process.stdout.readline()
                print(output.strip())
                # Do something else
                return_code = process.poll()
                if return_code is not None:
                    print('RETURN CODE', return_code)
                    # Process has finished, read rest of the output 
                    for output in process.stdout.readlines():
                        print(output.strip())
                        time.sleep(5)
                    break
    env.close()