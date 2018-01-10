import json

import jwt
from flask import Flask, request, render_template, jsonify, abort
from flask_restful import Resource, Api

from database import UsersDB, GroupsDB, TransactionsDB, CreditCardDB, BankAccountDB, AdminDB
from config import base_to_dict, datetime_handler, verify_request

SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'

app = Flask(__name__)
app.secret_key = SECRET

ADMINS_PARAMS = ['admin_email', 'admin_password', 'permissions']
GROUPS_PARAMS = ['group_name']


@app.route('/api/admins', methods=['GET', 'POST'])
@app.route('/api/admins/<_id>', methods=['GET', 'PUT', 'DELETE'])
def admins(_id=None):
    db = AdminDB()
    if request.method == 'GET':
        q = db.get(_id) or []
        return jsonify(base_to_dict(q))
    if request.method == 'POST':
        if verify_request(request, ADMINS_PARAMS):
            params = request.json
            status = db.set(params.get('admin_email'), params.get('admin_password'), params.get('permissions'))
            if status:
                return jsonify(status='success')
    if request.method == 'PUT':
        if verify_request(request, ADMINS_PARAMS):
            params = request.json
            status = db.update(_id, params)
            if status:
                return jsonify(status='success')
    if request.method == 'DELETE':
        status = db.delete(_id)
        if status:
            return jsonify(status='success')
    return abort(400)


@app.route('/api/admins', methods=['GET', 'POST'])
@app.route('/api/admins/<id_or_name>', methods=['GET', 'DELETE'])
def groups(id_or_name=None):
    db = GroupsDB()
    if request.method == 'GET':
        q = db.get(id_or_name) or []
        return jsonify(base_to_dict(q))
    if request.method == 'POST':
        if verify_request(request, GROUPS_PARAMS):
            params = request.json
            status = db.set(params.get('group_name'))
            if status:
                return jsonify(status='success')
    # if request.method == 'DELETE': TODO
    #     status = db.delete(_id)
    #     if status:
    #         return jsonify(status='success')
    return abort(400)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
