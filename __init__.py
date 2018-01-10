import json

import jwt
from flask import Flask, request, render_template, jsonify, abort

from database import session, UsersDB, GroupsDB, TransactionsDB, CreditCardDB, BankAccountDB, AdminDB, ClientsDB, \
    TracksDB
from config import base_to_dict, datetime_handler, verify_request

SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'

app = Flask(__name__)
app.secret_key = SECRET

ADMINS_PARAMS = ['admin_email', 'admin_password', 'permissions']
GROUPS_PARAMS = ['group_name']
USERS_PARAMS = ['group_id', 'user_email', 'user_password', 'user_first_name', 'user_last_name', 'user_phone']
CLIENTS_PARAMS = ['client_id', 'client_first_name', 'client_last_name', 'client_address', 'city', 'client_phone',
                  'client_email']
TRACKS_PARAMS = ['company', 'price', 'track_name', 'description', 'kosher']
TRANSACTIONS_PARAMS = ['email_user', 'track_id', 'client_id', 'credit_card_id', 'bank_account_id',
                       'date_time', 'sim_num', 'phone_num', 'status', 'transaction_client', 'comment', 'reminds']


def get(db, _id=None):
    q = db.get(_id) or []
    return jsonify(base_to_dict(q))


def post(db, data_params, _id):
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
        return post(db, data_params, _id)
    if request.method == 'PUT':
        return put(db, data_params, _id)
    if request.method == 'DELETE':
        return delete(db, _id)
    return abort(400)


@app.route('/api/admins', methods=['GET', 'POST'])
@app.route('/api/admins/<_id>', methods=['GET', 'PUT', 'DELETE'])
def admins(_id=None):
    db = AdminDB()
    return simple_api(db, ADMINS_PARAMS, _id)


@app.route('/api/groups', methods=['GET', 'POST'])
@app.route('/api/groups/<id_or_name>', methods=['GET', 'DELETE'])
def groups(id_or_name=None):
    db = GroupsDB()
    return simple_api(db, GROUPS_PARAMS, id_or_name)


@app.route('/api/users', methods=['GET', 'POST'])
@app.route('/api/users/<_id>', methods=['GET', 'PUT', 'DELETE'])
def users(_id=None):
    db = UsersDB()
    return simple_api(db, USERS_PARAMS, _id)


@app.route('/api/clients', methods=['GET', 'POST'])
@app.route('/api/clients/<_id>', methods=['GET', 'PUT', 'DELETE'])
def clients(_id=None):
    db = ClientsDB()
    return simple_api(db, CLIENTS_PARAMS, _id)


@app.route('/api/tracks', methods=['GET', 'POST'])
@app.route('/api/tracks/<_id>', methods=['GET', 'PUT', 'DELETE'])
def tracks(_id=None):
    db = TracksDB()
    return simple_api(db, TRACKS_PARAMS, _id)


@app.route('/api/transactions', methods=['GET', 'POST'])
@app.route('/api/transactions/<_id>', methods=['GET', 'PUT', 'DELETE'])
def transactions(_id=None):
    db = TransactionsDB()
    # TODO
    return simple_api(db, TRANSACTIONS_PARAMS, _id)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()


if __name__ == '__main__':
    app.run(debug=True, port=8080)
