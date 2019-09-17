#! /usr/bin/env python

from __future__ import print_function

import os
import json
import yaml
import requests

def get_kwargs_from_config(config_file_name):
    config_file = get_full_path_for_file_name(config_file_name)
    with open(config_file, 'r') as file_obj:
        data = yaml.safe_load(file_obj)
    return data

def get_full_path_for_file_name(file_name):
    src_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(os.path.dirname(src_dir))
    config_file = os.path.join(main_dir, 'config/'+file_name)
    return config_file


class DataHubClient(object):

    """Client for DataHub"""

    def __init__(self, api_info_file_name, **kwargs):
        self._read_api_info_from_file(api_info_file_name)
        self._team_name = kwargs.get('team_name', 'bitbots')
        self._base_url = kwargs.get('base_url', 'http://localhost:5000/')
        self._auth_required = kwargs.get('auth_required', False)
        self._username, self._password = None, None
        if self._auth_required:
            auth_info = kwargs.get('auth_info', None)
            assert isinstance(auth_info, dict) and 'user' in auth_info and 'pass' in auth_info
            self._username = auth_info.get('user')
            self._password = auth_info.get('pass')

    @staticmethod
    def default_init():
        """Default init method
        :returns: DataHubClient obj

        """
        config_file_name = 'datahub.yaml'
        api_info_file_name = get_full_path_for_file_name('rest_api_info.yaml')
        data = get_kwargs_from_config(config_file_name)
        dhc = DataHubClient(api_info_file_name, **data)
        return dhc

    def make_request(self, request_name, **kwargs):
        if request_name not in self._request_types:
            return None

        request_type = self._request_types[request_name]
        url = self._base_url + self._team_name + '/' + request_type['url']
        if request_type['id_required']:
            id_string = str(kwargs.get('url_id', ''))
            url += '/' + id_string
        print(url)
        auth = None
        if self._auth_required:
            auth = requests.auth.HTTPBasicAuth(self._username, self._password)

        arguments = None
        if request_type['type'] == 'POST' or request_type['type'] == 'PUT':
            arguments = kwargs.get('arguments', dict())
            for key in request_type['schema_keys']:
                assert key in arguments
            print(arguments)
        resp = requests.request(request_type['type'], url, json=arguments, auth=auth)

        response = None
        if resp.status_code > 210:
            print("Request failed. Received status code", str(resp.status_code))
            print(resp.text)
        elif resp.status_code == 200:
            print("Request succeeded")
            response = resp.json()
        else:
            print("Received status code", str(resp.status_code))
        return response

    def _read_api_info_from_file(self, api_info_file):
        self._request_types = None
        with open(api_info_file, 'r') as file_obj:
            api_info = yaml.safe_load(file_obj)
        self._request_types = api_info['request_types']
        for request_type_name in self._request_types:
            self._request_types[request_type_name]['schema_keys'] = \
                    api_info['schemas'][self._request_types[request_type_name]['schema_name']]
        

if __name__ == "__main__":
    DHC = DataHubClient.default_init()

    # list inventory items
    # resp = DHC.make_request('list_inventory_items')

    # get shop info
    resp = DHC.make_request('get_shop_info', url_id="ITEM00")
    update_dict = dict()
    for key in resp[0]:
        if str(key)[0] == "_":
            continue
        try:
            update_dict[key.encode('utf-8')] = resp[0][key].encode('utf-8')
        except AttributeError:
            update_dict[key.encode('utf-8')] = resp[0][key]

    print(update_dict)
    update_dict['quantity'] -= 1 # place holder for processing and changing
    # resp = DHC.make_request('set_shop', url_id="ITEM00", **update_dict)
    # resp = DHC.make_request('set_shop', url_id="ITEM00", arguments=update_dict)

    print(resp)
