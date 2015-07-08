__author__ = 'Matt David'

from addressimo.plugin import BasePlugin

class BaseResolver(BasePlugin):

    def get_config(self, id):
        raise NotImplementedError

    def get_all_keys(self):
        raise NotImplementedError

    def save(self, id_obj):
        raise NotImplementedError

    def delete(self, id_obj):
        raise NotImplementedError

    @classmethod
    def get_plugin_category(cls):
        return 'RESOLVER'

    @classmethod
    def get_plugin_name(cls):
        raise NotImplementedError