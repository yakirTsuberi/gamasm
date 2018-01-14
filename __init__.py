import json
from datetime import timedelta

from flask import Flask, request, jsonify, abort, Response
from flask_jwt import JWT, jwt_required, current_identity, CONFIG_DEFAULTS
from werkzeug.security import safe_str_cmp, check_password_hash

from database import session, create_all_tables, UsersDB, GroupsDB, TransactionsDB, AdminDB, ClientsDB, \
    TracksDB
from config import base_to_dict, datetime_handler, verify_request

SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'

create_all_tables()

app = Flask(__name__)
app.secret_key = SECRET


def authenticate(username, password):
    user = UsersDB().get(username)
    if user and check_password_hash(user.user_password, password):
        return user


def identity(payload):
    print(payload)
    _id = payload['identity']
    return UsersDB().get(_id=_id)


CONFIG_DEFAULTS['JWT_EXPIRATION_DELTA'] = timedelta(days=30)
jwt = JWT(app, authenticate, identity)

ADMINS_PARAMS = ['admin_email', 'admin_password', 'permissions']
GROUPS_PARAMS = ['group_name']
USERS_PARAMS = ['group_id', 'user_email', 'user_password', 'user_first_name', 'user_last_name', 'user_phone']
CLIENTS_PARAMS = ['client_id', 'client_first_name', 'client_last_name', 'client_address', 'city', 'client_phone',
                  'client_email']
TRACKS_PARAMS = ['company', 'price', 'track_name', 'description', 'kosher']
TRANSACTIONS_PARAMS = ['user_email', 'tracks', 'payment', 'client_id', 'client_first_name', 'client_last_name',
                       'client_address', 'city', 'client_phone', 'client_email', 'comment', 'reminds', 'status']


def get(db, _id=None):
    q = base_to_dict(db.get(_id) or [])
    return Response(json.dumps(q, default=datetime_handler), mimetype='application/json')


def post(db, data_params):
    if verify_request(request, data_params):
        return _response(db.set(**request.json))
    abort(400)


def put(db, data_params, _id):
    if verify_request(request, data_params):
        return _response(db.update(_id, request.json))
    abort(400)


def delete(db, _id):
    return _response(db.delete(_id))


def _response(result):
    if result is True:
        return jsonify(status='success')
    abort(400)


def simple_api(db, data_params, _id=None):
    if request.method == 'GET':
        return get(db, _id)
    if request.method == 'POST':
        return post(db, data_params)
    if request.method == 'PUT':
        return put(db, data_params, _id)
    if request.method == 'DELETE':
        return delete(db, _id)
    return abort(400)


@app.route('/api/admins', methods=['GET', 'POST'])
@app.route('/api/admins/<_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def admins(_id=None):
    db = AdminDB()
    return simple_api(db, ADMINS_PARAMS, _id)


@app.route('/api/groups', methods=['GET', 'POST'])
@app.route('/api/groups/<id_or_name>', methods=['GET', 'DELETE'])
@jwt_required()
def groups(id_or_name=None):
    db = GroupsDB()
    return simple_api(db, GROUPS_PARAMS, id_or_name)


@app.route('/api/users', methods=['GET', 'POST'])
@app.route('/api/users/<_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def users(_id=None):
    db = UsersDB()
    return simple_api(db, USERS_PARAMS, _id)


@app.route('/api/clients', methods=['GET', 'POST'])
@app.route('/api/clients/<_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def clients(_id=None):
    db = ClientsDB()
    return simple_api(db, CLIENTS_PARAMS, _id)


@app.route('/api/tracks', methods=['GET', 'POST'])
@app.route('/api/tracks/<_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def tracks(_id=None):
    db = TracksDB()
    return simple_api(db, TRACKS_PARAMS, _id)


@app.route('/api/transactions', methods=['GET', 'POST'])
@app.route('/api/transactions/<_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def transactions(_id=None):
    db = TransactionsDB()
    if request.method == 'GET':
        return Response(json.dumps(db.get(_id) or [], default=datetime_handler), mimetype='application/json')
    return simple_api(db, TRANSACTIONS_PARAMS, _id)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()


if __name__ == '__main__':
    app.run(debug=True, port=8080)
