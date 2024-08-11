import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_table, Word, CommonWord, User
import os
from dotenv import load_dotenv

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
NAMEDB = os.getenv('NAMEDB')

DSN = f'postgresql://{LOGIN}:{PASSWORD}@localhost/{NAMEDB}'
engine = sqlalchemy.create_engine(DSN)
create_table(engine)

Session = sessionmaker(bind=engine)
session = Session()

common_words_data = [
    {'target_word': 'Привет', 'translate_word': 'Hello'},
    {'target_word': 'Спасибо', 'translate_word': 'Thank you'},
    {'target_word': 'Пожалуйста', 'translate_word': 'Please'},
    {'target_word': 'Красный', 'translate_word': 'Red'},
    {'target_word': 'Собака', 'translate_word': 'Dog'},
    {'target_word': 'Она', 'translate_word': 'She'},
    {'target_word': 'Магазин', 'translate_word': 'Shop'},
    {'target_word': 'Кролик', 'translate_word': 'Rabbit'},
    {'target_word': 'Они', 'translate_word': 'They'},
    {'target_word': 'Лифт', 'translate_word': 'Elevator'},
    {'target_word': 'Дом', 'translate_word': 'House'},
    {'target_word': 'Трава', 'translate_word': 'Grass'},
    {'target_word': 'Дорога', 'translate_word': 'Road'}
]
for word_data in common_words_data:
    word = CommonWord(**word_data)
    session.add(word)

session.commit()
