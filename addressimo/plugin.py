__author__ = 'Matt David'
import inspect
import os
import sys
from importlib import import_module

from addressimo.config import config
from addressimo.util import LogUtil

log = LogUtil.setup_logging()

class BasePlugin:

    @classmethod
    def register_plugin(cls):
        PluginManager.register(cls.get_plugin_category(), cls.get_plugin_name(), cls)

    @classmethod
    def get_plugin_category(cls):
        raise NotImplementedError

    @classmethod
    def get_plugin_name(cls):
        raise NotImplementedError

class PluginManager:

    plugins = {}

    @classmethod
    def register(cls, category, name, clazz):
        log.info('Registering Plugin [CATEGORY: %s | NAME: %s | CLASS: %s]' % (category, name, clazz.__name__))
        cls.plugins['%s|%s' % (category, name)] = clazz

    @classmethod
    def get_plugin(cls, category, name):
        clazz = cls.plugins.get('%s|%s' % (category, name), None)
        if not clazz:
            return None

        return clazz()

    @classmethod
    def register_plugins(cls):
        log.info('Registering Available Plugins')
        for dir in config.plugin_directories:

            # Homedir doesn't exist, let's make an effort to see if we can find the homedir
            if not os.path.exists(config.home_dir):
                log.warn('Configured Home Directory DOES NOT Exist, trying to recover... [CONFIGURED HOMEDIR: %s]' % config.home_dir)
                cwd = os.getcwd()
                if cwd.endswith('addressimo'):
                    if os.path.exists(os.path.join(cwd, 'addressimo')):
                        config.home_dir = os.path.join(cwd, 'addressimo')
                    else:
                        config.home_dir = cwd

                    log.warn('Setting Discovered Home Directory [NEW HOMEDIR: %s]' % config.home_dir)

            log.info('Searching for Plugins in %s' % os.path.join(config.home_dir, dir))
            for f in os.listdir(os.path.join(config.home_dir, dir)):
                if not f.endswith('.py'):
                    continue
                try:
                    clean_name = f.replace('.py', '')
                    module_name = 'addressimo.%s.%s' % (dir, clean_name)
                    import_module(module_name, clean_name)
                    for name, obj in inspect.getmembers(sys.modules[module_name], lambda member: inspect.isclass(member)):
                        if issubclass(obj, BasePlugin):
                            try:
                                obj.register_plugin()
                            except NotImplementedError:
                                # This is used to skip base classes
                                pass
                except ImportError as e:
                    print e