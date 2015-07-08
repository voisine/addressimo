__author__ = 'frank'

# System Imports

# Third Party Imports
from flask import Flask, Response, request

# Addressimo Imports
from addressimo.admin import admin
from addressimo.plugin import PluginManager
from addressimo.util import create_json_response, LogUtil

# Setup Logging
log = LogUtil.setup_logging('server.py')

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    TESTING=True
)

# ###########################################
# Setup Pre-Request Processing
# ###########################################
@app.before_request
def before_request():

    # Handle our pre-flight OPTIONS check
    if request.method == 'OPTIONS':
        return create_json_response()

######################
# Register Plugins
######################
PluginManager.register_plugins()

# ###########################################
# Status Testing Route (for Load Balancing, etc)
@app.route('/index.html', methods=['GET', 'OPTIONS', 'HEAD', 'POST'])
def index():
    return Response("UP", status=200, mimetype='text/html')

@app.route('/api', defaults={'id': None}, methods=['GET'])
@app.route('/api/<id>', methods=['GET'])
def get_id_objs(id):
    return admin.get_id_objs(id)

@app.route('/api', methods=['POST'])
def create_id_obj():
    return admin.update_id_obj(None)

@app.route('/api/<id>', methods=['PUT'])
def update_id_obj(id):
    return admin.update_id_obj(id)

@app.route('/api/<id>', methods=['DELETE'])
def delete_id_obj(id):
    return admin.delete_id_obj(id)

@app.route('/api/<id>/privkey', methods=['DELETE'])
def delete_id_obj_priv_key(id):
    return admin.delete_id_obj_priv_key(id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
