import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Word(Base):
    __tablename__ = 'word'

    id = sa.Column(sa.Integer, primary_key=True)
    target_word = sa.Column(sa.String(length=50), nullable=False, unique=True)
    translate = relationship('Translate', backref='word', cascade='all')
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey('user.id'), nullable=False)
    attempts = sa.Column(sa.Integer, default=0)
    mastered = sa.Column(sa.Boolean, default=False)


class Translate(Base):
    __tablename__ = 'translate'

    id = sa.Column(sa.Integer, primary_key=True)
    translate_word = sa.Column(sa.String(length=50), nullable=False)
    id_word = sa.Column(sa.Integer, sa.ForeignKey('word.id'), nullable=False)
    other_words = relationship('Other', backref='translate', cascade='all')
    example = sa.Column(sa.String(length=255))


class Other(Base):
    __tablename__ = 'other'

    id = sa.Column(sa.Integer, primary_key=True)
    other_word = sa.Column(sa.String(length=50), nullable=False)
    id_translate = sa.Column(sa.Integer, sa.ForeignKey('translate.id'), nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.BigInteger, primary_key=True)


def create_table(engine):
    Base.metadata.create_all(engine)
