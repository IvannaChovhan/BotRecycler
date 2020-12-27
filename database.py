import pymongo
from data import *

client = pymongo.MongoClient(db_connection)
db = client.firstdb

collection = db.group

def init_user(user_id):
    global collection
    obj = {'user_name': '', 'user_id': int(user_id), 'state': 'init', 'user_phone': '', 'menu_message': 0, 'pos_lon': 0.0, 'pos_lat': 0.0}
    res = collection.find_one({'user_id': int(user_id)})
    if res:
        return False
    collection.insert_one(obj)
    return True


def get_user(user_id):
    global collection
    res = collection.find_one({'user_id': int(user_id)})
    if res:
        return res
    else:
        return False


def update_user(user_id, col, val):
    global collection
    collection.update_one({'user_id': int(user_id)}, {'$set': {str(col): val}})


def update_state(user_id, state):
    update_user(user_id, 'state', state)


def init_request(user_id):
    global collection
    collection.insert_one({'requester_id': int(user_id), 'type': '', 'amount': '', 'pos_lon': '', 'pos_lat': ''})


def update_request(user_id, col, val):
    global collection
    collection.update_one({'requester_id': int(user_id), str(col): ''}, {'$set': {str(col): val}})


def get_user_requests(user_id):
    global collection
    res = collection.find({'requester_id': int(user_id)})
    return res

# def get_group(group):
#     global collection
#     res = collection.find_one({'group': str(group)})
#     if res:
#         return res
#     else:
#         obj = {'group': str(group), 'admin': 'none'}
#         collection.insert_one(obj)
#         return obj


# def get_groups():
#     global collection
#     res = collection.find({'group': {'$ne': 'test'}})
#     ans = []
#     for one in res:
#         ans.append(one['group'])
#     return ans


# def get_q_names(group):
#     global collection
#     res = []
#     grp = get_group(group)
#     for strg in grp:
#         if strg != '_id' and strg != 'admin' and strg != 'group' and strg != 'members':
#             res.append(strg)
#     return res


# def update_admin(group, admin):
#     global collection
#     collection.update_one({'group': str(group)}, {
#                           '$set': {'admin': str(admin)}})


# def create_group(group):
#     global collection
#     obj = {'group': str(group), 'admin': 'none'}
#     collection.insert_one(obj)


# def create_q(group, qname):
#     global collection
#     collection.update_one({'group': str(group)}, {'$set': {str(qname): {}}})


# def delete_q(group, qname):
#     global collection
#     collection.update_one({'group': str(group)}, {'$unset': {str(qname): {}}})


# def add_to_q(group, qname, name, num='0'):
#     global collection
#     str_from = str(qname) + '.' + str(num)
#     collection.update_one({'group': str(group)}, {
#                           '$set': {str_from: str(name)}})


# def remove_from_q(group, qname, num):
#     global collection
#     str_from = str(qname) + '.' + str(num)
#     collection.update_one({'group': str(group)}, {'$unset': {str_from: ''}})


# def update_q(group, qname, obj):
#     global collection
#     collection.update_one({'group': str(group)}, {'$set': {str(qname): obj}})


# def add_user(group, id, name):
#     global collection
#     str_from = 'members.' + str(id)
#     collection.update_one({'group': str(group)}, {
#                           '$set': {str_from: str(name)}})


#     global collection
#     grp = collection.find_one({'group': str(group)})
#     return grp['members']
