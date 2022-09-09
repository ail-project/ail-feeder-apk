import lmdb
from androguard.core.bytecodes.apk import APK
from androguard.misc import AnalyzeAPK
from androguard.session import Session
from androguard.util import get_certificate_name_string
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.analysis.analysis import Analysis
from androguard.decompiler.decompiler import DecompilerJADX
from androguard.core.androconf import show_logging
from lxml import etree
import os
import re
import json
import sys
import hashlib
import binascii
from asn1crypto import x509, keys
from zipfile import ZipFile
import magic
import hashlib
import os
from flor import BloomFilter

import pdb

# Local repository
LOCAL_REPO = "/home/jlouis/Raccoon/content/apps"

# scraping lmdb
read = lmdb.open("./play", readonly = True)

# baseline lmdb
write = lmdb.open("./baseline", map_size=1000000000)

# flor bloom filter
bf = BloomFilter(n=1000000, p=0.0001)

with read.begin() as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        if (key[4:26].decode() == 'eu.europa.publications'):
            # launch androguard session
            androguard_session = Session()
            a: APK

            # Get the local file
            files = os.listdir("{}/{}".format(LOCAL_REPO, key[4:].decode()))
            for file in files:
                if file.endswith('.apk'):
                    filepath = "{}/{}/{}".format(LOCAL_REPO, key[4:].decode(), file)
                    a, _, _ = AnalyzeAPK(filepath, session=androguard_session)

                    apk_sha256 = list(androguard_session.get_all_apks())[0][0]

                    certs = set(a.get_certificates_der_v3() + a.get_certificates_der_v2() + [a.get_certificate_der(x) for x in a.get_signature_names()])
                    pkeys = set(a.get_public_keys_der_v3() + a.get_public_keys_der_v2())

                    certificates = []
                    for cert in certs:
                        x509_cert = x509.Certificate.load(cert)
                        certificates.append({
                            'sha1': "{}".format(hashlib.sha1(cert).hexdigest()),
                            'sha256': "{}".format(hashlib.sha256(cert).hexdigest()),
                            'md5': '{}'.format(hashlib.md5(cert).hexdigest()),
                            'serial': hex(x509_cert.serial_number)[2:],
                            'issuerDN': get_certificate_name_string(x509_cert.issuer, short=True),
                            'subjectDN': get_certificate_name_string(x509_cert.subject, short=True),
                            'not_before': x509_cert['tbs_certificate']['validity']['not_before'].native.strftime("%B %d %H:%M:%S %Y %Z"),
                            'not_after': x509_cert['tbs_certificate']['validity']['not_after'].native.strftime("%B %d %H:%M:%S %Y %Z")
                        })

                    # Check the certificate and continue if valid
                    if certificates[0]['sha256'] == "856475288406c9052c254ac43d8d8171b596ff4c208d20897a3710e063e2136a":
                        # Fingerprint the app
                        print("Signed app: {} - {}".format(a.get_app_name(), key.decode()))

                        public_keys = []
                        for public_key in pkeys:
                            x509_public_key = keys.PublicKeyInfo.load(public_key)
                            #pdb.set_trace()

                            # common stuffs
                            common = {
                                'algorithm': x509_public_key.algorithm,
                                'size': x509_public_key.bit_size,
                                'sha1': binascii.hexlify(x509_public_key.sha256).decode('UTF-8'),
                                'sha256': binascii.hexlify(x509_public_key.sha256).decode('UTF-8')
                            }

                            # rsa stuffs
                            rsa = {}
                            dsa = {}
                            if x509_public_key.native["algorithm"]["algorithm"] == "rsa":
                                rsa = {
                                    'modulus': '{}'.format(x509_public_key.native["public_key"]["modulus"]),
                                    'exponent': '{}'.format(x509_public_key.native["public_key"]["public_exponent"])
                                }

                            # dsa stuffs
                            # TODO
                            elif x509_public_key.native["algorithm"] == "dsa":
                                dsa = {
                                    'pk_hash_algo': x509_public_key.hash_algo
                                }

                            # EC stuffs
                            # TODO

                            public_keys.append({**common, **rsa})

                        # for key, v in certificates[0].items():
                            # print('{}:{}'.format(key, type(v)))

                        # working the xml resources file
                        arsc = a.get_android_resources()
                        if arsc != None:
                            p = arsc.get_packages_names()[0]

                            # get strings and urls
                            r = arsc.get_string_resources(p)
                            e = etree.fromstring(r)
                            strings = []
                            urls = []
                            url_re = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
                            # push url in urls
                            # and the rest to strings
                            for child in e:
                                if child.text is not None:
                                    match = url_re.match(child.text)
                                    if match is None:
                                        strings.append(child.text)
                                    else:
                                        urls.append(match.group())

                        # TODO use the androguard API to get the files 
                        # instead of using magic
                        # get base64 images
                        icon_path = a.get_app_icon()
                        images_sha256 = []
                        icon_sha256 = ""
                        with ZipFile(filepath, 'r') as zipObject:
                            listOfFileNames = zipObject.namelist()
                            # We can hash all images
                            for fileName in listOfFileNames:
                                tmp_bytes = zipObject.read(fileName)
                                if "image" in magic.from_buffer(tmp_bytes[:2048]):
                                    images_sha256.append(hashlib.sha256(tmp_bytes).hexdigest())
                                    bf.add(bytes(hashlib.sha256(tmp_bytes).hexdigest(), 'utf-8'))
                                if fileName == icon_path:
                                    icon_sha256 = hashlib.sha256(tmp_bytes).hexdigest()

                        # TODO analyse all the other files for strings and url

                        # TODO the dex methods ala koodeus
                        #d = DalvikVMFormat(a)
                        #dx = Analysis(d)
                        # Make sure that the jadx executable is found in $PATH
                        # or use the argument jadx="/path/to/jadx" to point to the executable
                        # decompiler = DecompilerJADX(d, dx)
                        #decompiler = DecompilerJADX(d, dx, jadx= "/home/jlouis/Git/jadx/build/jadx/bin/jadx")

                        # propagate decompiler and analysis back to DalvikVMFormat
                        #d.set_decompiler(decompiler)
                        #d.set_vmanalysis(dx)

                        # Now you can do stuff like:
                        #print("Decompilation methods:")
                        # for m in d.get_methods()[:10]:
                        #for m in d.get_methods():
                        #    print(m)
                        #    print(decompiler.get_source_method(m))

                        with open('images.bloom', 'wb') as f:
                            bf.write(f)
                        
                        play = json.loads(value.decode('utf-8'))
                                
                        results = json.dumps({
                            'play_store': play,
                            'app_name': a.get_app_name(),
                            'package_name': a.get_package(),
                            'is_signed:': a.is_signed(),
                            'certificate': certificates,
                            'services': a.get_services(),
                            'permissions': a.get_permissions(),
                            'min_sdk_version': a.get_min_sdk_version(),
                            'max_sdk_version': a.get_max_sdk_version(),
                            'target_sdk_version': a.get_target_sdk_version(),
                            'max_sdk_version': a.get_max_sdk_version(),
                            'min_sdk_version': a.get_min_sdk_version(),
                            'version_code': a.get_androidversion_code(),
                            'displayed_version': a.get_androidversion_name(),
                            'libraries': [x for x in a.get_libraries()],
                            'activities': a.get_activities(),
                            'main_activity': a.get_main_activity(),
                            'providers': a.get_providers(),
                            'receivers': a.get_receivers(),
                            'signature_name': a.get_signature_name(),
                            'wearable': a.is_wearable(),
                            'androidtv': a.is_androidtv(),
                            'sha256': apk_sha256,
                            'publickeys': public_keys,
                            'dexes': [], #TODO
                            'urls': [],
                            'new_permissions': [], # TODO
                            'filters': [], #TODO
                            'icon': icon_path,
                            'icon_sha256': icon_sha256,
                            'strings': strings,
                            'urls': urls,
                            'images_sha256': images_sha256
                        })
                        print(results)


                    else:
                        print("{}: {}".format(a.get_app_name(), certificates))

                    # Output to another lmdb for later use
                    with write.begin(write=True)  as write_txn:
                        write_txn.put(key = key, value = results.encode())


read.close()
write.close()