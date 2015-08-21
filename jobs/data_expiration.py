__author__ = 'frank'

from addressimo.config import config
from addressimo.plugin import PluginManager
from addressimo.util import LogUtil

log = LogUtil.setup_logging()

PluginManager.register_plugins()
resolver = PluginManager.get_plugin('RESOLVER', config.resolver_type)


log.info('Starting Stale Payment Request Meta Data Cleanup')
resolver.cleanup_stale_payment_request_meta_data()
log.info('Completed Stale Payment Request Meta Data Cleanup')


log.info('Starting Stale Payment Meta Data Cleanup')
resolver.cleanup_stale_payment_meta_data()
log.info('Completed Stale Payment Meta Data Cleanup')


log.info('Starting Stale PRR Data Cleanup')
resolver.cleanup_stale_prr_data()
log.info('Completed Stale PRR Data Cleanup')


log.info('Starting Stale RPR Data Cleanup')
resolver.cleanup_stale_return_pr_data()
log.info('Completed Stale RPR Data Cleanup')