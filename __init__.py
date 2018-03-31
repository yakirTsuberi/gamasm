import json
from datetime import timedelta

from flask import Flask, request, jsonify, abort, Response, redirect, url_for, render_template
from flask_jwt import JWT, CONFIG_DEFAULTS, jwt_required, current_identity
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from database import session, create_all_tables, UsersDB, GroupsDB, TransactionsDB, AdminDB, ClientsDB, \
    TracksDB, TmpDB
from config import base_to_dict, datetime_handler, verify_request

SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'

app = Flask(__name__)
app.secret_key = SECRET


def authenticate(username, password):
    user = UsersDB().get(username)
    if user and check_password_hash(user.user_password, password):
        return user


def identity(payload):
    _id = payload['identity']
    return UsersDB().get(_id=_id)


CONFIG_DEFAULTS['JWT_EXPIRATION_DELTA'] = timedelta(days=30)
jwt = JWT(app, authenticate, identity)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(admin_email):
    if AdminDB().get(admin_email=admin_email):
        user = User()
        user.id = admin_email
        return user


ADMINS_PARAMS = ['admin_email', 'admin_password', 'permissions']
GROUPS_PARAMS = ['group_name']
USERS_PARAMS = ['group_id', 'user_email', 'user_password', 'user_first_name', 'user_last_name', 'user_phone']
TMP_PARAMS = ['group_id', 'user_email', 'user_first_name', 'user_last_name', 'user_phone']
CLIENTS_PARAMS = ['client_id', 'client_first_name', 'client_last_name', 'client_address', 'city', 'client_phone',
                  'client_email']
TRACKS_PARAMS = ['company', 'price', 'track_name', 'description', 'kosher']
TRANSACTIONS_PARAMS = ['user_email', 'tracks', 'payment', 'client_id', 'client_first_name', 'client_last_name',
                       'client_address', 'city', 'client_phone', 'client_email', 'comment', 'reminds', 'status']


def get(db, _id=None):
    q = base_to_dict(db.get(_id) or [])
    return Response(json.dumps(q, default=datetime_handler), mimetype='application/json')


def post(db, data_params):
    print(request.json)
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


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    admin_email = request.form.get('admin_email')
    db = AdminDB().get(admin_email=admin_email)
    if db:
        if check_password_hash(db.admin_password, request.form.get('admin_password')):
            user = User()
            user.id = admin_email
            login_user(user, remember=request.form.get('remember-me') == 'on')
            return redirect(url_for('index'))

    return redirect(url_for('login'))


@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin/index')
def index():
    if current_user.is_authenticated:
        return render_template('admin.html')
    return redirect(url_for('login'))


@app.route('/api/admin/groups', methods=['GET', 'POST'])
@app.route('/api/admin/groups/<id_or_name>', methods=['GET', 'DELETE'])
@login_required
def groups(id_or_name=None):
    db = GroupsDB()
    return simple_api(db, GROUPS_PARAMS, id_or_name)


@app.route('/api/admin/users', methods=['GET', 'POST'])
@app.route('/api/admin/users/<_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def users(_id=None):
    db = UsersDB()
    return simple_api(db, USERS_PARAMS, _id)


@app.route('/api/admin/tmp', methods=['GET', 'POST'])
@app.route('/api/admin/tmp/<_id>', methods=['DELETE'])
@login_required
def tmp(_id=None):
    db = TmpDB()
    return simple_api(db, TMP_PARAMS, _id)


@app.route('/api/admin/clients', methods=['GET', 'POST'])
@app.route('/api/admin/clients/<_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def clients(_id=None):
    db = ClientsDB()
    return simple_api(db, CLIENTS_PARAMS, _id)


@app.route('/api/admin/tracks', methods=['GET', 'POST'])
@app.route('/api/admin/tracks/<_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def tracks(_id=None):
    db = TracksDB()
    return simple_api(db, TRACKS_PARAMS, _id)


@app.route('/api/admin/transactions', methods=['GET', 'POST'])
@app.route('/api/admin/transactions/<_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def transactions(_id=None):
    db = TransactionsDB()
    if request.method == 'GET':
        return Response(json.dumps(db.get(_id) or [], default=datetime_handler), mimetype='application/json')
    return simple_api(db, TRANSACTIONS_PARAMS, _id)


@app.route('/singUp', methods=['GET', 'POST'])
def sing_up():
    if request.method == 'GET':
        u = TmpDB().get(request.args.get('unique_id'))
        if u:
            return render_template('sing_up.html', u=json.dumps(base_to_dict(u)))
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('password_again'):
            u = request.form.get('u')
            if u:
                u = json.loads(u)
                u['user_password'] = request.form.get('password')
                del u['id']
                del u['unique_id']
                if UsersDB().set(**u):
                    TmpDB().delete(u.get('user_email'))
                return 'כל הכבוד!'
    return ''


@app.route('/api/transactions_by_user')
@jwt_required()
def transactions_by_user():
    db = TransactionsDB()
    return jsonify(db.get_by_user(current_identity.user_email))


@app.route('/api/tracks/<company>')
@jwt_required()
def tracks_by_company(company):
    db = TracksDB()
    return jsonify(companies=base_to_dict(db.get_by_company(company)))


@app.teardown_appcontext
def shutdown_session(exception=None):
    print(exception)
    session.close()


if __name__ == '__main__':
    create_all_tables()
    app.run(host='0.0.0.0')
