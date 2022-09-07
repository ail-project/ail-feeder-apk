from fingerprinter import androguard_fingerprinter
import sys
import os

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage : generate_report file.apk")
        exit()
    else:
        filepath = sys.argv[1]
        if os.path.isfile(filepath):
            try:
                report = androguard_fingerprinter.generate_report(filepath)
                print(report)
            except:
                print("File seems not to be an apk {}".format(filepath))

