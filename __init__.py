from flask import request
from flask_api import FlaskAPI
import jwt

from .tools.database import UsersDB, GroupsDB, TransactionsDB
from .tools.static import base_to_dict

SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'

app = FlaskAPI(__name__)
app.secret_key = SECRET


@app.route('/api/auth', methods=['POST'])
def auth():
    if request.method == 'POST':
        user_db = UsersDB()

        email = request.form.get('email')
        password = request.form.get('pw')

        user = user_db.get(email)
        if user:
            if user.password == password:
                data = base_to_dict(user)
                data.update(group_id=GroupsDB().get(user.group_id).name)
                del data['password']
                access_token = jwt.encode({'id': user.id, 'email': user.email}, SECRET)

                return {'auth': True,
                        'data': data,
                        'access_token': access_token.decode()}
    return {'auth': False}


@app.route('/api/my_sale')
def my_sale():
    _auth = request.headers.get('Authentication')
    try:
        token = jwt.decode(_auth.encode(), SECRET)
        email = token.get('email')
        tdb = TransactionsDB()
        return {'data': base_to_dict(tdb.my_sale(email))}
    except jwt.exceptions.DecodeError:
        return '', 403


if __name__ == '__main__':
    app.run()
