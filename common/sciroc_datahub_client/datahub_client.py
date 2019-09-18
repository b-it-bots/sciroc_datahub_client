#! /usr/bin/env python

from __future__ import print_function

import os
import json
import yaml
import datetime
import time
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
        self._episode_name = kwargs.get('episode_name', 'EPISODE7')
        self._robot_name = kwargs.get('robot_name', 'youbot')
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

    def update_robot_location(self, x, y):
        """Update the location of robot with x and y floats

        :x: float
        :y: float
        :returns: None

        """
        location_id = self._team_name + "-" + self._robot_name
        request_name = "set_robot_location"
        request_type = self._request_types[request_name]

        arguments = dict()
        for key in request_type['schema_keys']:
            arguments[key] = None
        arguments["@id"] = location_id
        arguments["@type"] = request_type["schema_name"]
        arguments["episode"] = self._episode_name
        arguments["team"] = self._team_name
        arguments["timestamp"] = self._get_current_timestamp()
        arguments["x"] = x
        arguments["y"] = y
        arguments["z"] = 0.0
        resp = self.make_request(request_name, url_id=location_id, arguments=arguments)

    def update_status(self, status_msg, x=0.0, y=0.0):
        """Update the status of robot with given string

        :status_msg: string
        :x: float
        :y: float
        :returns: None

        """
        status_id = self._team_name + "-" + self._robot_name + "-" + str(int(time.time()))
        request_name = "add_status"
        request_type = self._request_types[request_name]

        arguments = dict()
        for key in request_type['schema_keys']:
            arguments[key] = None
        arguments["@id"] = status_id
        arguments["@type"] = request_type["schema_name"]
        arguments["message"] = status_msg
        arguments["episode"] = self._episode_name
        arguments["team"] = self._team_name
        arguments["timestamp"] = self._get_current_timestamp()
        arguments["x"] = x
        arguments["y"] = y
        arguments["z"] = 0.0
        resp = self.make_request(request_name, url_id=status_id, arguments=arguments)

    def update_after_pick(self, item_id):
        """Update the inventory of the datahub after an item has been picked.

        :item_id: str
        :returns: None

        """
        request_name = "get_shop_info"
        items = self.make_request(request_name, url_id=item_id)
        update_dict = dict()
        for key in items[0]:
            if str(key)[0] == "_":
                continue
            try:
                update_dict[key.encode('utf-8')] = items[0][key].encode('utf-8')
            except AttributeError:
                update_dict[key.encode('utf-8')] = items[0][key]

        update_dict['quantity'] -= 1
        resp = DHC.make_request('set_shop', url_id=item_id, arguments=update_dict)

    def get_goal(self):
        """Return order dict obj
        :returns: dict

        Return type example:
            {
                "ORDER001": {
                    "ITEM001": 5,
                    "ITEM003": 3
                }
            }

        """
        request_name = "list_inventory_orders"

        orders = self.make_request(request_name)
        order_dict = dict()
        for order in orders:
            order_name = order["@id"].encode('utf-8')
            item_dict = dict()
            for item in order["items"]:
                item_id = item["inventory-item-id"].encode('utf-8')
                item_quantity = item["quantity"]
                item_dict[item_id] = item_quantity
            order_dict[order_name] = item_dict
        return order_dict

    def get_item_info(self, item_id):
        """Return a dict containing info for given `item_id`

        :item_id: str
        :returns: dict or None

        """
        request_name = "get_shop_info"

        items = self.make_request(request_name, url_id=item_id)
        try:
            item = items[0]
            item_dict = dict()
            item_dict["id"] = item["@id"].encode('utf-8')
            item_dict["name"] = item["label"].encode('utf-8')
            item_dict["shelf"] = item["shelf"].encode('utf-8')
            item_dict["slot"] = item["slot"].encode('utf-8')
            item_dict["quantity"] = item["quantity"]
            return item_dict
        except Exception as e:
            print("Encountered exception while getting item", item_id, "\n", str(e))
            return None

    def get_location_of(self, item_id):
        """Return a dict containing shelf and slot info of `item_id`

        :item_id: str
        :returns: dict or None

        Return example:
            {
                'shelf': '2',
                'slot': '1'
            }

        """
        item_dict = self.get_item_info(item_id)
        if item_dict is not None:
            location = {key: item_dict[key] for key in ('shelf', 'slot')}
        else:
            location = None
        return location

    def make_request(self, request_name, **kwargs):
        if request_name not in self._request_types:
            return None

        request_type = self._request_types[request_name]
        url = self._base_url + self._team_name + '/' + request_type['url']
        if request_type['id_required']:
            id_string = str(kwargs.get('url_id', ''))
            url += '/' + id_string
        # print(url)
        auth = None
        if self._auth_required:
            auth = requests.auth.HTTPBasicAuth(self._username, self._password)

        arguments = None
        if request_type['type'] == 'POST' or request_type['type'] == 'PUT':
            arguments = kwargs.get('arguments', dict())
            for key in request_type['schema_keys']:
                assert key in arguments
            # print(arguments)
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

    def _get_current_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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

    # DHC.update_robot_location(1.0, 1.0)

    # DHC.update_status("Going to Shelf 0", 1.0, 1.0)

    # goals = DHC.get_goal()
    # print(goals)

    ITEM_ID = "ITEM01"
    # info = DHC.get_item_info(ITEM_ID)
    # print(info)

    # location = DHC.get_location_of(ITEM_ID)
    # print(location)

    DHC.update_after_pick(ITEM_ID)
