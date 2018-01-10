import logging
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    email_user = Column(String, ForeignKey(Users.user_email))


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


class CreditCard(Base):
    __tablename__ = 'CreditCard'
    id = Column(Integer, primary_key=True)
    client_id = Column(String, ForeignKey(Clients.client_id))
    card_number = Column(String)
    month = Column(String)
    year = Column(String)
    cvv = Column(String)


class BankAccount(Base):
    __tablename__ = 'BankAccount'
    id = Column(Integer, primary_key=True)
    client_id = Column(String, ForeignKey(Clients.client_id))
    account_num = Column(String)
    brunch = Column(String)
    bank_num = Column(String)


class Transactions(Base):
    __tablename__ = 'Transactions'
    id = Column(Integer, primary_key=True)
    email_user = Column(String, ForeignKey(Users.user_email))
    track_id = Column(Integer, ForeignKey(Tracks.id))
    client_id = Column(String, ForeignKey(Clients.client_id))
    credit_card_id = Column(Integer, ForeignKey(CreditCard.id), nullable=True)
    bank_account_id = Column(Integer, ForeignKey(BankAccount.id), nullable=True)
    date_time = Column(DateTime)
    sim_num = Column(String)
    phone_num = Column(String)
    status = Column(Integer)  # 0=new, 1=success, 2=fail
    transaction_client = Column(String, nullable=True)
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
                                    admin_password=admin_password,
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

    def get(self, _id=None):
        q = session.query(*self._class.__table__.columns)
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or _id is None:
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
                                    user_password=user_password,
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

    def get(self, _id=None):
        q = session.query(*self._class.__table__.columns)
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or _id is None:
            return q.all()
        return q.first()


class TmpDB(DB):
    def __init__(self):
        super().__init__(Tmp)

    def set(self, unique_id, email_user):
        try:
            session.add(self._class(unique_id=unique_id, email_user=email_user))
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def delete(self, email_user):
        try:
            session.query(self._class).filter(self._class.email_user == email_user).delete()
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def get(self, email_user):
        return session.query(*self._class.__table__.columns).filter(self._class.email_user == email_user).first()


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

    def get(self, _id):
        q = session.query(*self._class.__table__.columns)
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or _id is None:
            return q.all()
        return q.first()


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
        if _id is not None:
            q = q.filter(self._class.id == _id)
        if q.count() > 1 or _id is None:
            return q.all()
        return q.first()


class CreditCardDB(DB):
    def __init__(self):
        super().__init__(CreditCard)

    def set(self, client_id, card_number, month, year, cvv):
        try:
            session.add(self._class(client_id=client_id,
                                    card_number=card_number,
                                    month=month,
                                    year=year,
                                    cvv=cvv))
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def update(self, credit_card_id, values):
        try:
            session.query(self._class).filter(self._class.id == credit_card_id).update(values)
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def delete(self, credit_card_id):
        try:
            session.query(self._class).filter(self._class.id == credit_card_id).delete()
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def all(self, client_id=None):
        q = session.query(*self._class.__table__.columns)
        if client_id is not None:
            q = q.filter(self._class.client_id == client_id)
        return q.all()

    def get(self, credit_card_id):
        return session.query(*self._class.__table__.columns).filter(self._class.id == credit_card_id).first()


class BankAccountDB(DB):
    def __init__(self):
        super().__init__(BankAccount)

    def set(self, client_id, account_num, brunch, bank_num):
        try:
            session.add(self._class(client_id=client_id,
                                    account_num=account_num,
                                    brunch=brunch,
                                    bank_num=bank_num))
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def update(self, bank_account_id, values):
        try:
            session.query(self._class).filter(self._class.id == bank_account_id).update(values)
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def delete(self, bank_account_id):
        try:
            session.query(self._class).filter(self._class.id == bank_account_id).delete()
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def all(self, client_id=None):
        q = session.query(*self._class.__table__.columns)
        if client_id is not None:
            q = q.filter(self._class.client_id == client_id)
        return q.all()

    def get(self, bank_account_id):
        return session.query(*self._class.__table__.columns).filter(self._class.id == bank_account_id).first()


class TransactionsDB(DB):
    def __init__(self):
        super().__init__(Transactions)

    def set(self, user_email, track_id, client_id, date_time, sim_num, phone_num,
            status=0, transaction_client=None, comment=None, reminds=None, credit_card_id=None, bank_account_id=None):
        try:
            session.add(self._class(email_user=user_email,
                                    track_id=track_id,
                                    client_id=client_id,
                                    credit_card_id=credit_card_id,
                                    bank_account_id=bank_account_id,
                                    date_time=date_time,
                                    sim_num=sim_num,
                                    phone_num=phone_num,
                                    status=status,
                                    transaction_client=transaction_client,
                                    comment=comment,
                                    reminds=reminds,
                                    ))
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()
            raise e

    def update(self, transactions_id, values):
        try:
            session.query(self._class).filter(self._class.id == transactions_id).update(values)
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def delete(self, transactions_id):
        try:
            session.query(self._class).filter(self._class.id == transactions_id).delete()
            session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

    def all(self, client_id=None):
        q = session.query(*self._class.__table__.columns)
        if client_id is not None:
            q = q.filter(self._class.client_id == client_id)
        return q.all()

    def get(self, transactions_id):
        return session.query(*self._class.__table__.columns).filter(self._class.id == transactions_id).first()

    def my_sale(self, email):
        q = session.query(
            Transactions.id,
            Clients.client_first_name,
            Clients.client_last_name,
            Clients.client_phone,
            Tracks.track_name,
            Transactions.status,
            Transactions.date_time,
            Transactions.phone_num,
            Transactions.sim_num,
            Transactions.comment)
        q = q.join(Tracks, (Clients, Clients.client_id == Transactions.client_id))
        q = q.filter(Transactions.email_user == email)
        return q.all()

    def status_sale(self):
        q = session.query(Transactions.id,
                          Transactions.date_time,
                          Transactions.sim_num,
                          Transactions.phone_num,
                          Transactions.comment,
                          Transactions.status,
                          Transactions.credit_card_id,
                          Transactions.bank_account_id,
                          Users.user_first_name,
                          Users.user_last_name,
                          Clients.client_first_name,
                          Clients.client_last_name,
                          Clients.client_address,
                          Clients.city,
                          Clients.client_id,
                          Tracks.company,
                          Tracks.track_name)
        q = q.join((Users, Users.user_email == Transactions.email_user),
                   (Clients, Clients.client_id == Transactions.client_id),
                   (Tracks, Tracks.id == Transactions.track_id))
        q = q.filter(Transactions.status == 0)
        return q.all()


if __name__ == '__main__':
    pass
    # _create_db()
    # DB(Clients).create_all_tables()
    # print(GroupsDB().all())
    # GroupsDB().set('ישיפון')
    # UsersDB().set(1, 'yakir@ravtech.co.il', '1q2w3e4r', 'יקיר', 'צוברי', '0527168254')
    # TracksDB().set('cellcom', 29, 'ללא הגבלה', 'כשר ללא הגבלה', True)
    # ClientsDB().set('302637350', 'שלום', 'חלפון', 'הנורית 5', 'השרון', '0506615048')
    # t = TransactionsDB().set('yakir@ravtech.co.il', 1, '302637350', datetime.now(), '987654321', '0502222222')
    # print(base_to_dict(TransactionsDB().status_sale()))
    # CreditCardDB().set('223366683', '741258963', '03', '21', '123')
    # TransactionsDB().update(1, dict(credit_card_id=1))
    # TransactionsDB().update(1, dict(status=0))
    # print(AdminDB().all())
