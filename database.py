import logging
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Dict, List

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import yagmail


def send_email(to, subject=None, contents=None):
    yag = yagmail.SMTP(user='gamasm.com@gmail.com', password='1qaz@WSX!')
    yag.send(to=to, subject=subject, contents=contents)


DB_PATH = 'sqlite:///' + str(Path(__file__).parent / 'data.db')
engine = create_engine(DB_PATH, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


def create_all_tables():
    Base().metadata.create_all(engine, checkfirst=True)


class Admins(Base):
    __tablename__ = 'Admins'
    id = Column(Integer, primary_key=True)
    admin_email = Column(String)
    admin_password = Column(String)
    permissions = Column(Integer)  # 3=height, 2=less, 1=small


class Groups(Base):
    __tablename__ = 'Groups'
    id = Column(Integer, primary_key=True)
    group_name = Column(String)


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey(Groups.id))
    user_email = Column(String, unique=True)
    user_password = Column(String)
    user_first_name = Column(String)
    user_last_name = Column(String)
    user_phone = Column(String, nullable=True)


class Tmp(Base):
    __tablename__ = 'Tmp'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True)
    group_id = Column(Integer, ForeignKey(Groups.id))
    user_email = Column(String)
    user_first_name = Column(String)
    user_last_name = Column(String)
    user_phone = Column(String, nullable=True)


class Tracks(Base):
    __tablename__ = 'Tracks'
    id = Column(Integer, primary_key=True)
    company = Column(String)
    price = Column(Float)
    track_name = Column(String)
    description = Column(String)
    kosher = Column(Boolean)


class Clients(Base):
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    client_first_name = Column(String)
    client_last_name = Column(String)
    client_address = Column(String)
    city = Column(String)
    client_phone = Column(String)
    client_email = Column(String, nullable=True)


class Transactions(Base):
    __tablename__ = 'Transactions'
    id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey(Users.user_email))
    track_id = Column(Integer, ForeignKey(Tracks.id))
    client_id = Column(String, ForeignKey(Clients.client_id))
    payment = Column(String)  # TODO check is json
    date_time = Column(DateTime)
    sim_num = Column(String)
    phone_num = Column(String)
    status = Column(Integer)  # 0=new, 1=success, 2=fail
    comment = Column(String, nullable=True)
    reminds = Column(Date, nullable=True)


class DB:
    def __init__(self, __class):
        self._class = __class


class AdminDB(DB):
    def __init__(self):
        super().__init__(Admins)

    def set(self, admin_email, admin_password, permissions):
        try:
            session.add(self._class(admin_email=admin_email,
                                    admin_password=generate_password_hash(admin_password),
                                    permissions=permissions))
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def update(self, _id, values):
        try:
            session.query(self._class).filter(self._class.id == _id).update(values)
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def delete(self, _id):
        try:
            session.query(self._class).filter(self._class.id == _id).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def all(self):
        return session.query(*self._class.__table__.columns).all()

    def get(self, _id=None, admin_email=None):
        q = session.query(*self._class.__table__.columns)
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if admin_email is not None:
            q = q.filter(self._class.admin_email == admin_email)
        if q.count() > 1:
            return q.all()
        return q.first()


class GroupsDB(DB):
    def __init__(self):
        super().__init__(Groups)

    def set(self, group_name):
        try:
            session.add(self._class(group_name=group_name))
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def update(self, group_id, values):
        try:
            session.query(self._class).filter(self._class.id == group_id).update(values)
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def delete(self, _id):
        try:
            session.query(self._class).filter(self._class.id == _id).delete()
            for u in session.query(Users.id).filter(Users.group_id == _id).all():
                session.query(Users).filter(Users.id == u.id).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def all(self):
        return session.query(*self._class.__table__.columns).all()

    def get(self, id_or_name=None):
        q = session.query(*self._class.__table__.columns)
        print(id_or_name)
        if id_or_name is not None:
            if id_or_name.isdigit():
                q = q.filter(self._class.id == id_or_name)
            else:
                q = q.filter(self._class.group_name == id_or_name)
        if q.count() > 1 or id_or_name is None:
            return q.all()
        return q.first()


class UsersDB(DB):
    def __init__(self):
        super().__init__(Users)

    def set(self, group_id, user_email, user_password, user_first_name, user_last_name, user_phone=None):
        try:
            session.add(self._class(group_id=group_id,
                                    user_email=str(user_email).lower(),
                                    user_password=generate_password_hash(user_password),
                                    user_first_name=str(user_first_name).lower(),
                                    user_last_name=str(user_last_name).lower(),
                                    user_phone=user_phone))
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def update(self, user_id, values):
        try:
            session.query(self._class).filter(self._class.id == user_id).update(values)
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def delete(self, _id):
        try:
            session.query(self._class).filter(self._class.id == _id).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def all(self, group_id=None):
        q = session.query(*self._class.__table__.columns)
        if group_id is not None:
            q = q.filter(self._class.group_id == group_id)
        return q.all()

    def get(self, user_email=None, _id=None):
        q = session.query(Users.id, Users.group_id, Users.user_email,
                          Users.user_password, Users.user_first_name,
                          Users.user_last_name, Users.user_phone)
        if user_email is not None:
            q = q.filter(self._class.user_email == user_email)
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or (user_email is None and _id is None):
            return q.all()
        return q.first()


class TmpDB(DB):
    def __init__(self):
        super().__init__(Tmp)

    def set(self, group_id, user_email, user_first_name, user_last_name, user_phone):
        try:
            unique_id = generate_password_hash(str(random.randrange(10000000000000000000)))
            session.add(self._class(unique_id=unique_id,
                                    group_id=group_id, user_email=user_email, user_first_name=user_first_name,
                                    user_last_name=user_last_name, user_phone=user_phone))
            session.commit()
            ht = 'לסיום תהליך ההרשמה נא אמת חשבון בלינק'
            send_email(user_email, 'Welcome to GAMA.S.M.', f'{ht}: 127.0.0.1:8080/singUp?unique_id={unique_id}')
            return True
        except Exception as e:
            logging.error(e)
            print(e)
            session.rollback()
            return False

    def delete(self, user_email):
        try:
            session.query(self._class).filter(self._class.user_email == user_email).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def get(self, unique_id):
        return session.query(*self._class.__table__.columns).filter(self._class.unique_id == unique_id).first()

    def all(self):
        return session.query(*self._class.__table__.columns).all()


class TracksDB(DB):
    def __init__(self):
        super().__init__(Tracks)

    def set(self, company, price, track_name, description, kosher):
        try:
            session.add(self._class(company=company,
                                    price=price,
                                    track_name=track_name,
                                    description=description,
                                    kosher=kosher))
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def update(self, track_id, values):
        try:
            session.query(self._class).filter(self._class.id == track_id).update(values)
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def delete(self, track_id):
        try:
            session.query(self._class).filter(self._class.id == track_id).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def all(self, company=None, kosher=None):
        q = session.query(*self._class.__table__.columns)
        if company is not None:
            q = q.filter(self._class.company == company)
        if kosher is not None:
            q = q.filter(self._class.kosher == kosher)
        return q.all()

    def get(self, _id=None):
        q = session.query(*self._class.__table__.columns)
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or _id is None:
            return q.all()
        return q.first()

    def get_by_company(self, company):
        return session.query(*self._class.__table__.columns).filter(Tracks.company == company).all()


class ClientsDB(DB):
    def __init__(self):
        super().__init__(Clients)

    def set(self, client_id, client_first_name, client_last_name, client_address, city, client_phone,
            client_email=None):
        try:
            session.add(self._class(client_id=client_id,
                                    client_first_name=client_first_name,
                                    client_last_name=client_last_name,
                                    client_address=client_address,
                                    city=city,
                                    client_phone=client_phone,
                                    client_email=client_email))
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def update(self, _id, values):
        try:
            session.query(self._class).filter(self._class.id == _id).update(values)
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def delete(self, _id):
        try:
            session.query(self._class).filter(self._class.id == _id).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def all(self):
        return session.query(*self._class.__table__.columns).all()

    def get(self, _id):
        q = session.query(*self._class.__table__.columns)
        print(q.all())
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or _id is None:
            return q.all()
        return q.first()


class TransactionsDB(DB):
    def __init__(self):
        super().__init__(Transactions)

    @staticmethod
    def _add_client(client_id, client_first_name, client_last_name, client_address, city, client_phone,
                    client_email):
        client = session.query(Clients.client_id).filter(Clients.client_id == client_id).first()
        if client is None:
            if ClientsDB().set(client_id, client_first_name, client_last_name, client_address, city, client_phone,
                               client_email):
                client = session.query(Clients.client_id).filter(Clients.client_id == client_id).first()
            else:
                return False
        print(client.keys())
        return client.client_id

    @staticmethod
    def _add_payment(payment):
        return payment

    def set(self, user_email, tracks: Dict[str, List[dict]], payment,
            client_id, client_first_name=None, client_last_name=None, client_address=None, city=None, client_phone=None,
            client_email=None, comment=None, reminds=None):
        try:
            client = self._add_client(client_id, client_first_name, client_last_name, client_address, city,
                                      client_phone, client_email)
            payment = self._add_payment(payment)  # TODO
            if reminds is not None:
                reminds = datetime.strptime(reminds, '%Y-%m-%d').date()

            if not any([client, payment]):
                return False
            print(client)
            for k, v in tracks.items():
                for t in v:
                    print(k, t)
                    session.add(self._class(email_user=user_email,
                                            track_id=k,
                                            client_id=client,
                                            payment=payment,
                                            date_time=datetime.utcnow(),
                                            sim_num=t.get('sim_num'),
                                            phone_num=t.get('phone_num'),
                                            status=0,
                                            transaction_client=None,
                                            comment=comment,
                                            reminds=reminds,
                                            ))
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            print(e)
            session.rollback()
            return False

    def update(self, _id, values):
        try:
            print(values)
            session.query(self._class).filter(self._class.id == _id).update(values)
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            print(e)
            session.rollback()
            return False

    def delete(self, transactions_id):
        try:
            session.query(self._class).filter(self._class.id == transactions_id).delete()
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            session.rollback()
            return False

    def get(self, _id=None):
        result = dict()
        q = session.query(*self._class.__table__.columns)
        if _id is not None:
            q = q.filter(Transactions.id == _id)
        for t in q.all():
            if result.get(t.client_id) is None:
                result[t.client_id] = {t.track_id: []}
            tmp = dict(id=t.id, date_time=str(t.date_time),
                       sim_num=t.sim_num, phone_num=t.phone_num,
                       comment=t.comment, status=t.status,
                       payment=t.payment, email_user=t.email_user)
            result[t.client_id][t.track_id].append(tmp)
        return result

    @staticmethod
    def get_by_user(user_email, date: datetime.date = None):
        # TODO: get all data of Transactions
        if date is None:
            date = datetime.utcnow().replace(day=1)

        def _filter(status):
            return session.query(Transactions).filter(
                Transactions.user_email == user_email).filter(
                and_(Transactions.date_time >= date,
                     Transactions.date_time < (date + relativedelta(months=1)))).filter(
                Transactions.status == status).count()

        return dict(fail=_filter(2), success=_filter(1), waiting=_filter(0))


if __name__ == '__main__':
    pass
    # create_all_tables()
    # AdminDB().set('yakir@ravtech.co.il', '123', 3)
    # print(TransactionsDB().get_by_user('yakir@ravtech.co.il'))
    print(TracksDB().get_by_company("cellcom"))