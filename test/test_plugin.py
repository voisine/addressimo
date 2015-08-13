__author__ = 'Matt David'

from mock import patch, Mock
from test import AddressimoTestCase

from addressimo.plugin import *

class EmptyClass:
            pass

class Plugin1(BasePlugin):

    register_called = False

    @classmethod
    def register_plugin(cls):
        cls.register_called = True

class Plugin2(BasePlugin):

    register_called = False

    @classmethod
    def register_plugin(cls):
        cls.register_called = True

class NotPlugin(BasePlugin):

    register_called = False

    @classmethod
    def register_plugin(cls):
        cls.register_called = True

class TestPluginManagerFunctions(AddressimoTestCase):

    def test_register(self):

        ret_val = PluginManager.register('CATEGORY', 'NAME', EmptyClass)

        self.assertIsNone(ret_val)
        self.assertIn('CATEGORY|NAME', PluginManager.plugins)
        self.assertEqual(EmptyClass, PluginManager.plugins['CATEGORY|NAME'])

        PluginManager.plugins.clear()

    def test_get_plugin(self):

        PluginManager.plugins['CATEGORY|NAME'] = EmptyClass

        ret_val = PluginManager.get_plugin('CATEGORY', 'NAME')
        self.assertTrue(isinstance(ret_val, EmptyClass))

        PluginManager.plugins.clear()

    def test_get_plugin_no_such_plugin(self):

        ret_val = PluginManager.get_plugin('CATEGORY', 'NAME')
        self.assertIsNone(ret_val)

        PluginManager.plugins.clear()

class TestRegisterPlugins(AddressimoTestCase):

    def setUp(self):

        self.patcher1 = patch('addressimo.plugin.os', wraps=os)
        self.patcher2 = patch('addressimo.plugin.import_module')
        self.patcher3 = patch('addressimo.plugin.inspect')
        self.patcher4 = patch('addressimo.plugin.sys')

        self.mockOs = self.patcher1.start()
        self.mockImportModule = self.patcher2.start()
        self.mockInspect = self.patcher3.start()
        self.mockSys = self.patcher4.start()

        # Setup GoRight Data
        self.mockOs.path.exists.return_value = True
        self.mockOs.listdir.return_value = [
            'one.py',
            'two.py',
            'random.txt'
        ]

        self.mockInspect.getmembers.side_effect = [(('name1', Plugin1),), (('name2', Plugin2),)]

        self.mockInspect.isclass.return_value = True

        config.plugin_directories = ['dir1']

        self.mockSys.modules = {
            'addressimo.dir1.one': 1,
            'addressimo.dir1.two': 1
        }

        Plugin1.register_called = False
        Plugin2.register_called = False

    def test_go_right(self):

        PluginManager.register_plugins()

        self.assertEqual(1, self.mockOs.path.exists.call_count)
        self.assertEqual(config.home_dir, self.mockOs.path.exists.call_args[0][0])

        self.assertEqual(1, self.mockOs.listdir.call_count)
        self.assertEqual('%s/dir1' % config.home_dir, self.mockOs.listdir.call_args[0][0])

        self.assertEqual(2, self.mockImportModule.call_count)
        self.assertEqual('addressimo.dir1.one', self.mockImportModule.call_args_list[0][0][0])
        self.assertEqual('addressimo.dir1.two', self.mockImportModule.call_args_list[1][0][0])

        self.assertEqual(2, self.mockInspect.getmembers.call_count)
        self.assertTrue(Plugin1.register_called)
        self.assertTrue(Plugin2.register_called)
        self.assertFalse(NotPlugin.register_called)

    def test_import_error(self):

        self.mockImportModule.side_effect = [ImportError('Testing Import Error'), None]

        PluginManager.register_plugins()

        self.assertEqual(1, self.mockOs.path.exists.call_count)
        self.assertEqual(config.home_dir, self.mockOs.path.exists.call_args[0][0])

        self.assertEqual(1, self.mockOs.listdir.call_count)
        self.assertEqual('%s/dir1' % config.home_dir, self.mockOs.listdir.call_args[0][0])

        self.assertEqual(2, self.mockImportModule.call_count)
        self.assertEqual('addressimo.dir1.one', self.mockImportModule.call_args_list[0][0][0])
        self.assertEqual('addressimo.dir1.two', self.mockImportModule.call_args_list[1][0][0])

        self.assertEqual(1, self.mockInspect.getmembers.call_count)
        self.assertTrue(Plugin1.register_called)
        self.assertFalse(Plugin2.register_called)
        self.assertFalse(NotPlugin.register_called)

    def test_homedir_doesnt_exist_and_cwd_not_addressimo_end(self):

        self.mockOs.path.exists.return_value = False
        self.mockOs.getcwd.return_value = '/my/test/dir'
        self.mockOs.listdir.return_value = []

        PluginManager.register_plugins()

        self.assertEqual(2, self.mockOs.path.exists.call_count)
        self.assertEqual(config.home_dir, self.mockOs.path.exists.call_args_list[0][0][0])
        self.assertEqual('/my/test/dir/../addressimo', self.mockOs.path.exists.call_args_list[1][0][0])

        self.assertEqual(1, self.mockOs.listdir.call_count)
        self.assertEqual('%s/dir1' % config.home_dir, self.mockOs.listdir.call_args[0][0])

        self.assertEqual(0, self.mockImportModule.call_count)
        self.assertEqual(0, self.mockInspect.getmembers.call_count)
        self.assertFalse(Plugin1.register_called)
        self.assertFalse(Plugin2.register_called)
        self.assertFalse(NotPlugin.register_called)

    def test_homedir_doesnt_exist_and_cwd_double_addressimo_end(self):

        self.mockOs.path.exists.side_effect = [False, True]
        self.mockOs.getcwd.return_value = '/my/test/addressimo'

        PluginManager.register_plugins()

        self.assertEqual(2, self.mockOs.path.exists.call_count)
        self.assertEqual(config.home_dir, self.mockOs.path.exists.call_args[0][0])

        self.assertEqual(1, self.mockOs.listdir.call_count)
        self.assertEqual('/my/test/addressimo/addressimo/dir1', self.mockOs.listdir.call_args[0][0])

        self.assertEqual(2, self.mockImportModule.call_count)
        self.assertEqual('addressimo.dir1.one', self.mockImportModule.call_args_list[0][0][0])
        self.assertEqual('addressimo.dir1.two', self.mockImportModule.call_args_list[1][0][0])

        self.assertEqual(2, self.mockInspect.getmembers.call_count)
        self.assertTrue(Plugin1.register_called)
        self.assertTrue(Plugin2.register_called)
        self.assertFalse(NotPlugin.register_called)

    def test_homedir_doesnt_exist_and_cwd_addressimo_end(self):

        self.mockOs.path.exists.side_effect = [False, False]
        self.mockOs.getcwd.return_value = '/my/test/addressimo'

        PluginManager.register_plugins()

        self.assertEqual(2, self.mockOs.path.exists.call_count)
        self.assertEqual('/my/test/addressimo/addressimo', self.mockOs.path.exists.call_args[0][0])

        self.assertEqual(1, self.mockOs.listdir.call_count)
        self.assertEqual('/my/test/addressimo/dir1', self.mockOs.listdir.call_args[0][0])

        self.assertEqual(2, self.mockImportModule.call_count)
        self.assertEqual('addressimo.dir1.one', self.mockImportModule.call_args_list[0][0][0])
        self.assertEqual('addressimo.dir1.two', self.mockImportModule.call_args_list[1][0][0])

        self.assertEqual(2, self.mockInspect.getmembers.call_count)
        self.assertTrue(Plugin1.register_called)
        self.assertTrue(Plugin2.register_called)
        self.assertFalse(NotPlugin.register_called)

    def test_homedir_doesnt_exist_and_down_one_directory(self):

        self.mockOs.path.exists.side_effect = [False, True]
        self.mockOs.getcwd.return_value = '/my/test/addressimo/downone'

        PluginManager.register_plugins()

        self.assertEqual(2, self.mockOs.path.exists.call_count)
        self.assertEqual('/my/test/addressimo/downone/../addressimo', self.mockOs.path.exists.call_args[0][0])

        self.assertEqual(1, self.mockOs.listdir.call_count)
        self.assertEqual('/my/test/addressimo/downone/../addressimo/dir1', self.mockOs.listdir.call_args[0][0])

        self.assertEqual(2, self.mockImportModule.call_count)
        self.assertEqual('addressimo.dir1.one', self.mockImportModule.call_args_list[0][0][0])
        self.assertEqual('addressimo.dir1.two', self.mockImportModule.call_args_list[1][0][0])

        self.assertEqual(2, self.mockInspect.getmembers.call_count)
        self.assertTrue(Plugin1.register_called)
        self.assertTrue(Plugin2.register_called)
        self.assertFalse(NotPlugin.register_called)