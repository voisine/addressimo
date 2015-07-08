__author__ = 'mdavid'

import json
import logging
import logging.handlers
import os
import sys
import urllib

from flask import request, current_app, Response
from urlparse import urlparse

from addressimo.config import config

def create_json_response(success=True, message='', status=200, data={}):

    allowed_origins = [config.site_url, 'localhost', '127.0.0.1']

    # Generate Allowed Origins
    origin_value = None
    for origin in allowed_origins:
        if request.referrer and origin in request.referrer:
            try:
                _uri = urlparse(request.referrer)
                origin_value = '%s://%s' % (_uri.scheme, _uri.netloc)
                break
            except:
                pass

    # Generate Allowed Methods
    _app = current_app._get_current_object()
    allow_methods = set()
    for rule in _app.url_map._rules:
        if rule.rule == request.url_rule.rule:
            allow_methods.update(rule.methods)

    default_headers = {
        'Access-Control-Allow-Methods': ', '.join(allow_methods),
        'Access-Control-Allow-Headers': 'X-Requested-With, accept, content-type'
    }

    if origin_value:
        default_headers['Access-Control-Allow-Origin'] = origin_value

    rdict = {}
    rdict['success'] = success
    rdict['message'] = message
    for key in data.keys():
        if key not in ['success', 'message']:
            rdict[key] = data[key]

    # Certain response codes don't contain data
    if status in [204]:
        return Response(None, status=status, mimetype='application/json', headers=default_headers)

    return Response(json.dumps(rdict), status=status, mimetype='application/json', headers=default_headers)

def create_bip72_response(wallet_address, amount, payment_request_url=None):

    allowed_origins = [config.site_url, 'localhost', '127.0.0.1']

    # Generate Allowed Origins
    origin_value = None
    for origin in allowed_origins:
        if request.referrer and origin in request.referrer:
            try:
                _uri = urlparse(request.referrer)
                origin_value = '%s://%s' % (_uri.scheme, _uri.netloc)
                break
            except:
                pass

    # Generate Allowed Methods
    _app = current_app._get_current_object()
    allow_methods = set()
    for rule in _app.url_map._rules:
        if rule.rule == request.url_rule.rule:
            allow_methods.update(rule.methods)

    default_headers = {
        'Access-Control-Allow-Methods': ', '.join(allow_methods),
        'Access-Control-Allow-Headers': 'X-Requested-With, accept, content-type'
    }

    if origin_value:
        default_headers['Access-Control-Allow-Origin'] = origin_value

    response_text = 'bitcoin:'
    if wallet_address:
        response_text += wallet_address

    args = []
    if amount:
        args.append('amount=%s' % amount)
    if payment_request_url:
        args.append('r=%s' % urllib.quote_plus(payment_request_url))
    if args:
        response_text += '?%s' % '&'.join(args)

    return Response(str(response_text), status=200, mimetype='text/plain', headers=default_headers)

class ContextFilter(logging.Filter):

    def filter(self, record):
        record.ip = request.access_route[0] if request else None
        return True

class LogUtil():

    loggers = {}

    @classmethod
    def setup_logging(cls, app_name='app', log_to_file=False):

        if LogUtil.loggers.get(app_name):
            return cls.loggers.get(app_name)

        logdir = os.path.abspath('/var/log/addressimo')
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        log = logging.getLogger(app_name)
        f = ContextFilter()
        log.addFilter(f)
        log.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter("%(asctime)s [%(process)d] [%(levelname)s] %(funcName)s :: [IP: %(ip)s] :: %(message)s")

        if log_to_file:
            fh = logging.handlers.TimedRotatingFileHandler('/var/log/addressimo/%s.log' % app_name, when="d", interval=1, backupCount=10)
            fh.setFormatter(log_formatter)
            log.addHandler(fh)

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(log_formatter)
        log.addHandler(ch)
        log.info("Logger Initialized [%s]" % app_name)
        cls.loggers[app_name] = log
        return log
