#! /usr/bin/env python

from __future__ import print_function

import os
import json
from flask import Flask
from flask_restful import Api, Resource, reqparse

DATA = None

# users = [
#     {
#         "name": "Nicholas",
#         "age": 42,
#         "occupation": "Network Engineer"
#     },
#     {
#         "name": "Elvin",
#         "age": 32,
#         "occupation": "Doctor"
#     },
#     {
#         "name": "Jass",
#         "age": 22,
#         "occupation": "Web Developer"
#     },
# ]

# class User(Resource):
#     def get(self, name):
#         for user in users:
#             if(name == user["name"]):
#                 return user, 200
#         return "User not found", 404

#     def post(self, name):
#         parser = reqparse.RequestParser()
#         parser.add_argument("age")
#         parser.add_argument("occupation")
#         args = parser.parse_args()

#         for user in users:
#             if(name == user["name"]):
#                 return "User with name {} already exists".format(name), 400

#         user = {
#             "name": name,
#             "age": args["age"],
#             "occupation": args["occupation"]
#         }
#         users.append(user)
#         return user, 201

#     def delete(self, name):
#         global users
#         users = [user for user in users if user["name"] != name]
#         return "{} is deleted.".format(name), 200
      
class InventoryItemList(Resource):
    def get(self, team_name):
        if 'inventoryItems' not in DATA:
            return "Internal Server Error", 500
        return DATA['inventoryItems'], 200

class InventoryItem(Resource):

    def get(self, team_name, item_id):
        if 'inventoryItems' not in DATA:
            return "Internal Server Error", 500
        for inventory_item in DATA['inventoryItems']:
            if(item_id == inventory_item["@id"]):
                return inventory_item, 200
        return "Item not found", 400

    def put(self, team_name, item_id):
        parser = self._get_parser()
        args = parser.parse_args()
        if 'inventoryItems' not in DATA:
            return "Internal Server Error", 500
        for inventory_item in DATA['inventoryItems']:
            if(item_id == inventory_item["@id"]):
                inventory_item["@type"] = args["@type"]
                inventory_item["label"] = args["label"]
                inventory_item["description"] = args["description"]
                inventory_item["shelf"] = args["shelf"]
                inventory_item["slot"] = args["slot"]
                inventory_item["quantity"] = args["quantity"]
                inventory_item["timestamp"] = args["timestamp"]
                return inventory_item, 204

        inventory_item = {
            "@id": item_id,
            "@type": args["@type"],
            "label": args["label"],
            "description": args["description"],
            "shelf": args["shelf"],
            "slot": args["slot"],
            "quantity": args["quantity"],
            "timestamp": args["timestamp"]
        }
        DATA['inventoryItems'].append(inventory_item)
        return inventory_item, 201

    def post(self, team_name, item_id):
        parser = self._get_parser()
        args = parser.parse_args()

        if 'inventoryItems' not in DATA:
            return "Internal Server Error", 500
        for inventory_item in DATA['inventoryItems']:
            if(item_id == inventory_item["@id"]):
                inventory_item["@type"] = args["@type"]
                inventory_item["label"] = args["label"]
                inventory_item["description"] = args["description"]
                inventory_item["shelf"] = args["shelf"]
                inventory_item["slot"] = args["slot"]
                inventory_item["quantity"] = args["quantity"]
                inventory_item["timestamp"] = args["timestamp"]
                return inventory_item, 204
        return "Not found", 404

    def _get_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument("@id")
        parser.add_argument("@type")
        parser.add_argument("label")
        parser.add_argument("description")
        parser.add_argument("shelf")
        parser.add_argument("slot")
        parser.add_argument("quantity")
        parser.add_argument("timestamp")
        return parser

def main():
    global DATA
    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(os.path.dirname(code_dir))
    data_file = os.path.join(main_dir, 'config/test_data.json')
    with open(data_file, 'r') as file_obj:
        try:
            DATA = json.load(file_obj)
        except Exception as e:
            print('Encountered following exception while loading data file')
            print(str(e))
            return
    # print(json.dumps(DATA, indent=2))
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(InventoryItemList, "/<string:team_name>/sciroc-episode7-inventory-item")
    api.add_resource(InventoryItem, "/<string:team_name>/sciroc-episode7-inventory-item/<string:item_id>")
    app.run(debug=True)

if __name__ == "__main__":
    main()
