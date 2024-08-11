import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Word(Base):
    __tablename__ = 'word'

    id = sa.Column(sa.Integer, primary_key=True)
    target_word = sa.Column(sa.String(length=50), nullable=False)
    translate_word = sa.Column(sa.String(length=50), nullable=False)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey('user.id'), nullable=True)


class CommonWord(Base):
    __tablename__ = 'common_word'

    id = sa.Column(sa.Integer, primary_key=True)
    target_word = sa.Column(sa.String(length=50), nullable=False)
    translate_word = sa.Column(sa.String(length=50), nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.BigInteger, primary_key=True)
    words = relationship('Word', backref='user')


def create_table(engine):

    Base.metadata.create_all(engine)
