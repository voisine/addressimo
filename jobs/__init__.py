__author__ = 'mdavid'

# System Imports

# Third Party Imports

# Netki Imports
from gid.common.config import ConfigManager
from gid.util.LogUtil import LogUtil

# Get Config
config = ConfigManager().get_config()

# Setup Logging
log = LogUtil.setup_logging('__init__.py')
