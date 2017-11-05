import logging
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = 'sqlite:///' + str(Path(__file__).parent.parent / 'data.db')
Base = declarative_base()


class Groups(Base):
    __tablename__ = 'Groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey(Groups.id))
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String, nullable=True)


class Tmp(Base):
    __tablename__ = 'Tmp'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True)
    email = Column(String)


class Tracks(Base):
    __tablename__ = 'Tracks'
    id = Column(Integer, primary_key=True)
    company = Column(String)
    price = Column(Float)
    name = Column(String)
    description = Column(String)
    kosher = Column(Boolean)


class Clients(Base):
    __tablename__ = 'Clients'
    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(String)
    city = Column(String)
    phone = Column(String)
    email = Column(String, nullable=True)


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
    user_id = Column(String, ForeignKey(Users.email))
    track_id = Column(Integer, ForeignKey(Tracks.id))
    client_id = Column(String, ForeignKey(Clients.client_id))
    credit_card_id = Column(Integer, ForeignKey(CreditCard.id), nullable=True)
    bank_account_id = Column(Integer, ForeignKey(BankAccount.id), nullable=True)
    date_time = Column(DateTime)
    sim_num = Column(String)
    phone_num = Column(String)
    status = Column(Integer)  # 0=new, 1=success, 2=fail
    comment = Column(String, nullable=True)
    reminds = Column(Date, nullable=True)


class DB:
    def __init__(self, __class):
        self.engine = create_engine(DB_PATH, connect_args={'check_same_thread': False})
        session = sessionmaker(bind=self.engine)
        self.session = session()
        self._class = __class

    def create_all_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)


class GroupsDB(DB):
    def __init__(self):
        super().__init__(Groups)

    def set(self, name):
        try:
            self.session.add(self._class(name=name))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def update(self, group_id, values):
        try:
            self.session.query(self._class).filter(self._class.id == group_id).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, group_id):
        try:
            self.session.query(self._class).filter(self._class.id == group_id).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self):
        return self.session.query(*self._class.__table__.columns).all()

    def get(self, group_id):
        return self.session.query(*self._class.__table__.columns).filter(self._class.id == group_id).first()


class UsersDB(DB):
    def __init__(self):
        super().__init__(Users)

    def set(self, group_id, email, password, first_name, last_name, phone=None):
        try:
            self.session.add(self._class(group_id=group_id,
                                         email=str(email).lower(),
                                         password=password,
                                         first_name=str(first_name).lower(),
                                         last_name=str(last_name).lower(),
                                         phone=phone))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def update(self, email, values):
        try:
            self.session.query(self._class).filter(self._class.email == email.lower()).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, email):
        try:
            self.session.query(self._class).filter(self._class.email == email.lower()).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self, group_id=None):
        q = self.session.query(*self._class.__table__.columns)
        if group_id is not None:
            q = q.filter(self._class.group_id == group_id)
        return q.all()

    def get(self, email):
        return self.session.query(*self._class.__table__.columns).filter(self._class.email == email.lower()).first()


class TmpDB(DB):
    def __init__(self):
        super().__init__(Tmp)

    def set(self, unique_id, email):
        try:
            self.session.add(self._class(unique_id=unique_id, email=email))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, email):
        try:
            self.session.query(self._class).filter(self._class.email == email).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def get(self, email):
        return self.session.query(*self._class.__table__.columns).filter(self._class.email == email).first()


class TracksDB(DB):
    def __init__(self):
        super().__init__(Tracks)

    def set(self, company, price, name, description, kosher):
        try:
            self.session.add(self._class(company=company,
                                         price=price,
                                         name=name,
                                         description=description,
                                         kosher=kosher))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def update(self, track_id, values):
        try:
            self.session.query(self._class).filter(self._class.id == track_id).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, track_id):
        try:
            self.session.query(self._class).filter(self._class.id == track_id).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self, company=None, kosher=None):
        q = self.session.query(*self._class.__table__.columns)
        if company is not None:
            q = q.filter(self._class.company == company)
        if kosher is not None:
            q = q.filter(self._class.kosher == kosher)
        return q.all()

    def get(self, track_id):
        return self.session.query(*self._class.__table__.columns).filter(self._class.id == track_id).first()


class ClientsDB(DB):
    def __init__(self):
        super().__init__(Clients)

    def set(self, client_id, first_name, last_name, address, city, phone, email=None):
        try:
            self.session.add(self._class(client_id=client_id,
                                         first_name=first_name,
                                         last_name=last_name,
                                         address=address,
                                         city=city,
                                         phone=phone,
                                         email=email))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def update(self, client_id, values):
        try:
            self.session.query(self._class).filter(self._class.client_id == client_id).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, client_id):
        try:
            self.session.query(self._class).filter(self._class.client_id == client_id).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self):
        return self.session.query(*self._class.__table__.columns).all()

    def get(self, client_id):
        return self.session.query(*self._class.__table__.columns).filter(self._class.client_id == client_id).first()


class CreditCardDB(DB):
    def __init__(self):
        super().__init__(CreditCard)

    def set(self, client_id, card_number, month, year, cvv):
        try:
            self.session.add(self._class(client_id=client_id,
                                         card_number=card_number,
                                         month=month,
                                         year=year,
                                         cvv=cvv))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def update(self, credit_card_id, values):
        try:
            self.session.query(self._class).filter(self._class.id == credit_card_id).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, credit_card_id):
        try:
            self.session.query(self._class).filter(self._class.id == credit_card_id).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self, client_id=None):
        q = self.session.query(*self._class.__table__.columns)
        if client_id is not None:
            q = q.filter(self._class.client_id == client_id)
        return q.all()

    def get(self, client_id):
        return self.session.query(*self._class.__table__.columns).filter(self._class.client_id == client_id).first()


class BankAccountDB(DB):
    def __init__(self):
        super().__init__(BankAccount)

    def set(self, client_id, account_num, brunch, bank_num):
        try:
            self.session.add(self._class(client_id=client_id,
                                         account_num=account_num,
                                         brunch=brunch,
                                         bank_num=bank_num))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def update(self, bank_account_id, values):
        try:
            self.session.query(self._class).filter(self._class.id == bank_account_id).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, bank_account_id):
        try:
            self.session.query(self._class).filter(self._class.id == bank_account_id).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self, client_id=None):
        q = self.session.query(*self._class.__table__.columns)
        if client_id is not None:
            q = q.filter(self._class.client_id == client_id)
        return q.all()

    def get(self, client_id):
        return self.session.query(*self._class.__table__.columns).filter(self._class.client_id == client_id).first()


class TransactionsDB(DB):
    def __init__(self):
        super().__init__(Transactions)

    def set(self, user_email, track_id, client_id, date_time, sim_num, phone_num,
            status=0, comment=None, reminds=None, credit_card_id=None, bank_account_id=None):
        try:
            self.session.add(self._class(user_id=user_email,
                                         track_id=track_id,
                                         client_id=client_id,
                                         credit_card_id=credit_card_id,
                                         bank_account_id=bank_account_id,
                                         date_time=date_time,
                                         sim_num=sim_num,
                                         phone_num=phone_num,
                                         status=status,
                                         comment=comment,
                                         reminds=reminds,
                                         ))
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()
            raise e

    def update(self, transactions_id, values):
        try:
            self.session.query(self._class).filter(self._class.id == transactions_id).update(values)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def delete(self, transactions_id):
        try:
            self.session.query(self._class).filter(self._class.id == transactions_id).delete()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

    def all(self, user_id=None):
        q = self.session.query(*self._class.__table__.columns)
        if user_id is not None:
            q = q.filter(self._class.user_id == user_id)
        return q.all()

    def get(self, group_id):
        return self.session.query(*self._class.__table__.columns).filter(self._class.id == group_id).first()

    def my_sale(self, email):
        q = self.session.query(
            Transactions.id,
            Clients.first_name,
            Clients.last_name,
            Clients.phone,
            Tracks.name,
            Transactions.status,
            Transactions.date_time,
            Transactions.phone_num,
            Transactions.sim_num,
            Transactions.comment)
        q = q.join(Tracks, (Clients, Clients.id == Transactions.client_id))
        q = q.filter(Transactions.user_id == email)
        return q.all()


if __name__ == '__main__':
    from tools.static import base_to_dict

    tdb = TransactionsDB()
    clients = ClientsDB()
    print(base_to_dict(tdb.my_sale('yakir@ravtech.co.il')))
