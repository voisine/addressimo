__author__ = 'mdavid'

import logging

from flask import Flask, Response, request

from addressimo.config import config
from addressimo.paymentrequest.prr import PRR
from addressimo.plugin import PluginManager
from addressimo.resolvers import resolve, return_used_branches
from addressimo.storeforward import StoreForward
from addressimo.util import create_json_response

log = logging.getLogger(__name__)

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    TESTING=True,
    RATELIMIT_STORAGE_URL=config.redis_ratelimit_uri,
    RATELIMIT_HEADERS_ENABLED=False
)

# ###########################################
# Setup Pre-Request Processing
# ###########################################
@app.before_request
def before_request():

    # Handle our pre-flight OPTIONS check
    if request.method == 'OPTIONS':
        return create_json_response()


# ###########################################
# Setup Rate Limiting
# ###########################################
try:
    from flask_limiter import Limiter
    limiter = Limiter(app, global_limits=["20 per minute"])

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return create_json_response(success=False, message="ratelimit exceeded", status=429)

    @limiter.request_filter
    def ip_whitelist():
        return request.remote_addr == "127.0.0.1"

except ImportError:
    log.warn('Rate limiting not available. To add rate limiting, install the Flask-Limiter module, install Redis, and configure Redis in config.')

######################
# Register Plugins
######################
PluginManager.register_plugins()

# ###########################################
# Status Testing Route (for Load Balancing, etc)
@app.route('/index.html', methods=['GET', 'OPTIONS', 'HEAD', 'POST'])
def index():
    return Response("UP", status=200, mimetype='text/html')

@app.route('/resolve/<id>', methods=['GET'])
@limiter.limit("60 per minute")
def resolve_id(id):
    return resolve(id)

@app.route('/resolve/<id>', methods=['POST'])
@limiter.limit("60 per minute")
def submit_pr_request(id):
    return PRR.submit_prr(id)

@app.route('/branches/<id>', methods=['GET'])
@limiter.limit("10 per minute")
def get_used_branches(id):
    return return_used_branches(id)

@app.route('/sf', methods=['POST'])
@limiter.limit("10 per minute")
def register_sf_endpoint():
    return StoreForward.register()

@app.route('/sf/<id>', methods=['PUT'])
@limiter.limit("10 per minute")
def add_sf_paymentrequests(id):
    return StoreForward.add()

@app.route('/sf/<id>', methods=['DELETE'])
@limiter.limit("10 per minute")
def remove_sf_endpoint(id):
    return StoreForward.delete()

@app.route('/sf/<id>', methods=['GET'])
@limiter.limit("10 per minute")
def sf_getcount(id):
    return StoreForward.get_count()

@app.route('/prr/<id>', methods=['GET'])
@limiter.limit("10 per minute")
def get_prr(id):
    return PRR.get_queued_pr_requests(id)

@app.route('/prr/<id>', methods=['POST'])
@limiter.limit("10 per minute")
def submit_return_pr(id):
    return PRR.submit_return_pr(id)

@app.route('/pr/<id>', methods=['GET'])
@limiter.limit("10 per minute")
def get_return_pr(id):
    return PRR.get_return_pr(id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)