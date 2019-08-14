#! /usr/bin/env python

from __future__ import print_function

import requests

class DataHubClient(object):

    """Client for DataHub"""

    def __init__(self, **kwargs):
        # auth = requests.auth.HTTPBasicAuth('dharmin', '123456')
        # url = base_url + team_id + '/' + request_type
        # print(url)
        # resp = requests.get(url=url, auth=auth)
        resp = requests.get("http://localhost:5000/b-it-bots/sciroc-episode7-inventory-item")
        print(resp)
        print(resp.status_code)
        if resp.status_code != 200:
            print("Request failed. Received status code", str(resp.status_code))
            print(resp.text)
        else:
            print(resp.json())
        


if __name__ == "__main__":
    DHC = DataHubClient()
