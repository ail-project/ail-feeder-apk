from google_play_scraper import search, reviews_all, reviews, app
import json
import lmdb
import os

def scrap_task(mode, bk, hk, limit, scrapdb, huntdb, baselinekeywords, huntkeywords, certificatessha1):
    env: lmdb.Environment
    search_terms = []
    if mode == "baselining":
        env = lmdb.open(scrapdb, map_size=1000000000)
        search_terms = baselinekeywords

    elif mode == "hunting":
        search_terms = huntkeywords
        env = lmdb.open(huntdb, map_size=1000000000)

    # Searching for relevant apps
    for term in search_terms:
        # max is 50 - the lib has no pagination on search results (yet)
        print(f"searching {term}")
        results = search(term, lang="en", country="us", n_hits=1000)
        with env.begin(write=True) as txn:
            print(len(results))
            appCtr = 0
            for application in results:
                get_app = txn.get(key = "app:{}".format(application['appId']).encode())
                if get_app == None:
                    # if we don't have it already, let's get some details
                    details = app( application['appId'], lang='en', country='us')
                    count = 0
                    get_reviews = []
                    while count < limit:
                        c = 200 if (limit - count) > 200 else (limit - count)
                        print(f"fetching {c}")

                        if count == 0:
                            result, continuation_token = reviews(
                                application['appId'],
                                count= c
                            )
                        else:
                            result, _ = reviews(
                                application['appId'],
                                count= c,
                                continuation_token = continuation_token
                            )
                        count = count + len(result)
                        for review in result:
                            get_reviews.append(review)
                        if len(result) < c:
                            break

                    details['comments'] = []
                    details['score'] = []
                    for review in get_reviews:
                        if review != None and review['content'] != None:
                            details['comments'].append(review['content'])
                        if review != None and review['score'] != None:
                            details['score'].append(review['score'] )
                    print("appending {}".format(application['appId']))
                    txn.put(key = "app:{}".format(application['appId']).encode(), value = json.dumps(details).encode())
                else:
                    print("already seen {}".format(application['appId']))
                appCtr = appCtr + 1
                print(f"Still {len(results)-appCtr} to go")

    env.close()