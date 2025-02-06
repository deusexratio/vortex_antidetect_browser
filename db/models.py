from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TypeDecorator, String

from db.config import DB_DIR
from db.db import DB


class StringList(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return ','.join(value)
        return ''

    def process_result_value(self, value, dialect):
        if value:
            return value.split(',')
        return []


class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    proxy: Mapped[str | None]
    page_urls = mapped_column(StringList)
    fingerprint: Mapped[str | None]
    user_data_dir: Mapped[str] = mapped_column(unique=True) # default=os.path.join(USER_DATA_DIR, str(name))
    creation_date: Mapped[datetime] = mapped_column(default=datetime.now())
    note: Mapped[str | None]

    def __repr__(self):
        return f'{self.id}: Name: {self.name}, Proxy: {self.proxy}, Fingerprint: {self.fingerprint}'


class Wallets(Base):
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True, index=True)

    evm_seed_phrase: Mapped[str | None]
    evm_private_key: Mapped[str | None]
    solana_seed_phrase: Mapped[str | None]
    solana_private_key: Mapped[str | None]
    aptos_seed_phrase: Mapped[str | None]
    aptos_private_key: Mapped[str | None]
    sui_seed_phrase: Mapped[str | None]
    sui_private_key: Mapped[str | None]

    def __repr__(self):
        return f'{self.id}: Name: {self.name}'


class Extension(Base):
    __tablename__ = 'extensions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    extension_id: Mapped[str]


db = DB(f'sqlite:///{DB_DIR}', echo=False, pool_recycle=3600, connect_args={'check_same_thread': False})
db.create_tables(Base)
