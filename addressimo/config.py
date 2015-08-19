__author__ = 'mdavid'

from attrdict import AttrDict

# Addressimo Configuration
config = AttrDict()

# General Setup
config.site_url = 'addressimo.netki.com'
config.cache_loader_process_pool_size = 4
config.cache_loader_blocktx_pool_size = 15
config.bip32_enabled = True
config.bip70_enabled = True
config.bip70_default_amount = 0
config.bip70_default_expiration = 900
config.bip72_compatability = True
config.bip70_audit_log = True

# Presigned Payment Request
config.presigned_pr_limit = 100

# Path Configuration
config.home_dir = '/Users/frank/PycharmProjects/addressimo/addressimo'
config.plugin_directories = [
    'logger',
    'resolvers',
    'signer'
]

# Redis Setup
config.redis_id_obj_uri = 'redis://localhost:6379/1'
config.redis_prr_queue = 'redis://localhost:6379/2'
config.redis_pr_store = 'redis://localhost:6379/3'
config.redis_payment_store = 'redis://localhost:6379/4'
config.redis_logdb_uri = 'redis://localhost:6379/5'
config.redis_address_branch_uri = 'redis://localhost:6379/13'
config.redis_addr_cache_uri = 'redis://localhost:6379/14'
config.redis_ratelimit_uri = 'redis://localhost:6379/15'

# Object Configuration
config.resolver_type = 'REDIS'
config.signer_type = 'LOCAL'

# Logging Plugin Setup
config.logger_type = 'LOCAL'
config.logger_api_endpoint = 'https://auditor.mydomain.com/log'

# Bitcoin Setup
config.bitcoin_user = 'bitcoinrpc'
config.bitcoin_pass = '03fd3f1cba637e40e984611b50bed238'
config.cache_blockheight_threshold = 2
config.payment_submit_tx_retries = 5

# Admin public key for authenticating signatures for signed requests to get_branches endpoint (hex encoded).
# That endpoint is used for HD wallets to retrieve which branches Addressimo has served addresses for
config.admin_public_key = 'ac79cd6b0ac5f2a6234996595cb2d91fceaa0b9d9a6495f12f1161c074587bd19ae86928bddea635c930c09ea9c7de1a6a9c468f9afd18fbaeed45d09564ded6'

#config.signer_api_endpoint = 'https://signer.mydomain.com/sign'