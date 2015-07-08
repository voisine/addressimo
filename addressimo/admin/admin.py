__author__ = 'frank'

import json

from flask import request
from redis import Redis
from addressimo.config import config
from addressimo.data import IdObject
from addressimo.plugin import PluginManager
from addressimo.util import create_json_response

redis_conn = Redis.from_url(config.redis_id_obj_uri)

def get_id_objs(id):

    resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)

    if id:
        raw = resolver.get_id_obj(id)

        if not raw:
            return create_json_response(False, 'Object not found for this ID.', 404)

        raw['private_key'] = ''

        result = {'data': raw}
    else:
        result = {'keys': resolver.get_all_keys()}

    return create_json_response(True, '', 200, result)

def update_id_obj(id):

    resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)

    if not id:
        id_obj = IdObject()
    else:
        id_obj = resolver.get_id_obj(id)

    if not id_obj:
        return create_json_response(False, 'Object not found for this ID.', 404)

    rdata = request.get_json()

    if not set(rdata.keys()).issubset(id_obj.keys()):
        return create_json_response(False, 'Unknown key submitted', 400)

    for key, value in rdata.items():
        if key == 'id':
            continue

        if key == 'private_key' and not value:
            continue

        id_obj[key] = value

    try:
        resolver.save(id_obj)
    except:
        return create_json_response(False, 'Exception occurred attempting to save id object', 500)

    return create_json_response(True, 'Update succeeded', 200, {'id': id_obj.id})

def delete_id_obj(id):

    resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)

    id_obj = resolver.get_id_obj(id)

    if not id_obj:
        return create_json_response(False, 'Object not found for this ID.', 404)

    try:
        resolver.delete(id_obj)
    except:
        return create_json_response(False, 'Exception occurred attempting to delete id object', 500)

    return create_json_response(True, 'Delete succeeded', 204)

def delete_id_obj_priv_key(id):

    resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)

    id_obj = resolver.get_id_obj(id)

    if not id_obj:
        return create_json_response(False, 'Object not found for this ID.', 404)

    id_obj.private_key = None

    try:
        resolver.save(id_obj)
    except:
        return create_json_response(False, 'Exception occurred attempting to save id object', 500)

    return create_json_response(True, 'Delete private key succeeded', 204)


if __name__ == '__main__':
    print get_id_objs(None)
