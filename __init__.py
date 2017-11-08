import json
import sys

from flask import Flask, request, render_template
import jwt

sys.path.insert(0, "/var/www/api.gama-sm.com/gamasm/tools/")
from tools.database import UsersDB, GroupsDB, TransactionsDB, CreditCardDB, BankAccountDB
from tools.static import base_to_dict, datetime_handler

SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'

app = Flask(__name__)
app.secret_key = SECRET


@app.route('/api/admin')
def admin():
    return render_template('admin.html')


@app.route('/api/admin/status_sale')
def status_sale():
    status_sale = TransactionsDB().status_sale()
    payments = {}
    for p in status_sale:
        if p.credit_card_id is not None:
            payments[p.id] = base_to_dict(CreditCardDB().get(p.credit_card_id))
        elif p.bank_account_id is not None:
            payments[p.id] = base_to_dict(BankAccountDB().get(p.credit_card_id))
    return json.dumps(dict(status_sale=base_to_dict(status_sale), payments=payments), default=datetime_handler,
                      ensure_ascii=False).encode()


@app.route('/api/admin/groups_and_users')
def groups_and_users():
    result = {}
    groups = GroupsDB().all()
    print(groups)
    for group in groups:
        users = base_to_dict(UsersDB().all(group.id))
        for user in users:
            del user['user_password']
        result[group.group_name] = users
    print(result)
    return json.dumps(result, ensure_ascii=False).encode()


@app.route('/api/admin/update_user', methods=['POST'])
def update_user():
    print(request.form)
    UsersDB().update(int(request.form.get('id')), json.loads(request.form.get('values')))
    return json.dumps({'response': 'success'})


@app.route('/api/admin/remove_user', methods=['POST'])
def remove_user():
    print(request.form)
    UsersDB().delete(int(request.form.get('id')))
    return json.dumps({'response': 'success'})


@app.route('/api/admin/create_user', methods=['POST'])
def create_user():
    print(request.form, request.form.get('user_phone'))
    group_id = GroupsDB().get(group_name=request.form.get('group_name')).id

    UsersDB().set(group_id=group_id, user_email=request.form.get('user_email'),
                  user_password='#123',
                  user_first_name=request.form.get('user_first_name'),
                  user_last_name=request.form.get('user_last_name'),
                  user_phone=request.form.get('user_phone'))

    return json.dumps({'response': 'success'})


@app.route('/api/admin/update_status', methods=['POST'])
def update_status():
    print(request.form)
    TransactionsDB().update(int(request.form.get('id')), json.loads(request.form.get('values')))
    return json.dumps({'response': 'success'})


@app.route('/api/admin/remove_sale', methods=['POST'])
def remove_sale():
    print(request.form)
    return json.dumps({'response': 'success'})


@app.route('/api/auth', methods=['POST'])
def auth():
    user_db = UsersDB()

    email = request.form.get('email_user')
    password = request.form.get('pw')

    user = user_db.get(email)
    if user:
        if user.password == password:
            data = base_to_dict(user)
            data.update(admin_id=GroupsDB().get(user.group_id).name)
            del data['user_password']
            access_token = jwt.encode({'id': user.id, 'email_user': user.email}, SECRET)

            return json.dumps({'auth': True,
                               'data': data,
                               'access_token': access_token.decode()},
                              ensure_ascii=False).encode()
    return json.dumps({'auth': False})


@app.route('/api/my_sale')
def my_sale():
    _auth = request.headers.get('Authentication')
    if _auth is not None:
        try:
            token = jwt.decode(_auth.encode(), SECRET)
            email = token.get('email_user')
            tdb = TransactionsDB()
            return json.dumps({'data': base_to_dict(tdb.my_sale(email))}, ensure_ascii=False).encode()
        except jwt.exceptions.DecodeError:
            pass
    return '', 403


if __name__ == '__main__':
    app.run(debug=True)
