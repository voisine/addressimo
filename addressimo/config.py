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
config.redis_address_branch_uri = 'redis://localhost:6379/13'
config.redis_addr_cache_uri = 'redis://localhost:6379/14'
config.redis_ratelimit_uri = 'redis://localhost:6379/15'
config.redis_logdb_uri = 'redis://localhost:6379/5'

# Object Configuration
# config.object_lookup_class = 'LocalResolver'
# config.object_lookup_class = 'MongoResolver'
config.resolver_type = 'REDIS'
config.signer_type = 'LOCAL'

# Logging Plugin Setup
config.logger_type = 'LOCAL'
config.logger_api_endpoint = 'https://auditor.mydomain.com/log'

# Bitcoin Setup
config.bitcoin_user = 'bitcoinrpc'
config.bitcoin_pass = '03fd3f1cba637e40e984611b50bed238'
config.cache_blockheight_threshold = 2

# Admin public key for authenticating signatures for signed requests to get_branches endpoint (hex encoded).
# That endpoint is used for HD wallets to retrieve which branches Addressimo has served addresses for
config.admin_public_key = 'ac79cd6b0ac5f2a6234996595cb2d91fceaa0b9d9a6495f12f1161c074587bd19ae86928bddea635c930c09ea9c7de1a6a9c468f9afd18fbaeed45d09564ded6'

#config.signer_api_endpoint = 'https://signer.mydomain.com/sign'

# config.bip32.static_table = {
#     '1234567890abcdef': 'xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8'
# }
#
# config.bip70.static_table = {
#     '1234567890abcdef': '''
# -----BEGIN PRIVATE KEY-----
# MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAL5j+dJFa9/OSeLJ
# ghO9DXgoT5Da7clwBtulQOTXy0/K7lryPr6WVzE1CpTv69AaGG7iUsTFqoJ2p0jM
# 8/xzmOSDRbEw6VgAy+UCZ1Tny4k5fujO9FUiMwRXlIcpo+hZIxoZg+Fch7oeBEN4
# o/YhvaCzZLSw2l82oeggxxVRKvh7AgMBAAECgYBLehzm1Cig0AoQgywzIQZ+9RQd
# 6/zKl8PQPaINVtM97cgye8iOC9HDKzDnvHlyxXWcN9LyOR6Qm/NTdBThpv4cIMwc
# DUaGz8eAKvMz7RyPRipwwG0Aq+xvscuJIhEESWBug5M3vbRkNGsGo0nIlkzIAqhn
# +zq10R2jMlUXY4M5AQJBAPq3EnTAJD8jx8euNwAC+BELpgLru15lkV0o0z/I1hhk
# 91F8QhTmSFl17a0H//mMBm+w3QFyyExwtxhLHQFasvsCQQDCZ2Apk6WoggMD2Jv+
# 5QeRh3sXLX2azTnszRWN5xvOiQcBM5q8+RI4wRviU7A8nbrxlySsS0VAfkLq0qSP
# 6diBAkEAvdXW1K4UA/b8s1ZXcNvOp2Fxjy6dDenL+oUKB3bznT7+ASYcByUizRI9
# J9Ix4OtEiFeb0BfwT+jcyjk9uiPJ9wJBALB2p9p1tJzGDziRieCRQxJ92WTLnUVE
# Xv0tmBAsJZiP17Tmg+JfcIPl/oquDr6nKoeb++UNmjoVomaHeGtOCIECQBEtmwwj
# Eb0xwt9hlPF3ax7mQTH9et/2bMfoCz0PwrnZQCIyIj+xcExkdkoOd8q4kkVyDvI/
# 9zfKcsYvAmDU4OQ=
# -----END PRIVATE KEY-----
# -----BEGIN CERTIFICATE-----
# MIIC9DCCAl2gAwIBAgIJALbvOdiQX4QgMA0GCSqGSIb3DQEBCwUAMIGSMQswCQYD
# VQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEUMBIGA1UEBwwLTG9zIEFuZ2Vs
# ZXMxFDASBgNVBAoMC05ldGtpLCBJbmMuMQwwCgYDVQQLDANkZXYxDzANBgNVBAMM
# Bm1kYXZpZDEjMCEGCSqGSIb3DQEJARYUb3BlbnNvdXJjZUBuZXRraS5jb20wHhcN
# MTUwNDIzMDEzMDI2WhcNMTYwNDIyMDEzMDI2WjCBkjELMAkGA1UEBhMCVVMxEzAR
# BgNVBAgMCkNhbGlmb3JuaWExFDASBgNVBAcMC0xvcyBBbmdlbGVzMRQwEgYDVQQK
# DAtOZXRraSwgSW5jLjEMMAoGA1UECwwDZGV2MQ8wDQYDVQQDDAZtZGF2aWQxIzAh
# BgkqhkiG9w0BCQEWFG9wZW5zb3VyY2VAbmV0a2kuY29tMIGfMA0GCSqGSIb3DQEB
# AQUAA4GNADCBiQKBgQC+Y/nSRWvfzkniyYITvQ14KE+Q2u3JcAbbpUDk18tPyu5a
# 8j6+llcxNQqU7+vQGhhu4lLExaqCdqdIzPP8c5jkg0WxMOlYAMvlAmdU58uJOX7o
# zvRVIjMEV5SHKaPoWSMaGYPhXIe6HgRDeKP2Ib2gs2S0sNpfNqHoIMcVUSr4ewID
# AQABo1AwTjAdBgNVHQ4EFgQUSXzp9Q6toC9mi3qLLr0/YJfhpEEwHwYDVR0jBBgw
# FoAUSXzp9Q6toC9mi3qLLr0/YJfhpEEwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0B
# AQsFAAOBgQAU6E55fjxi2+C9FXnEHRVDEt1l1Rl/C6UxuzHtCitG7uSNa0NqJsP3
# F4J5pF1jFlRnTix8s/5TMJ9+fQwsYu7mlhTN4xB/9DDA13C40pWkNifeoquhE/+0
# rFhAxdbeHjwhElfusbIPLl8jNikPKYIjynm3P+4oTU8jzSqF6FiOTA==
# -----END CERTIFICATE-----
# '''
# }
#
# # Mongo Configuration
# config.mongo.connection_uri = 'mongodb://localhost:27017/addressimo'
#
# # Redis Configuration
# config.redis.connection_uri = 'redis://localhost:6379'