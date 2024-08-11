import os
import random
from dotenv import load_dotenv
from telebot import types, TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Word, CommonWord, User

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
NAMEDB = os.getenv('NAMEDB')
TOKEN = os.getenv('TOKEN')

bot = TeleBot(TOKEN)

DSN = f'postgresql://{LOGIN}:{PASSWORD}@localhost/{NAMEDB}'
engine = create_engine(DSN)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


class Command:
    ADD_WORD = 'Добавить слово\u2795'
    DELETE_WORD = 'Удалить слово\u2B05'
    NEXT = 'Дальше\u23ED'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    add_word = State()
    delete_word = State()


def get_random_word(user_id):

    user_words = session.query(Word).filter_by(user_id=user_id).all()
    common_words = session.query(CommonWord).all()

    all_words = user_words + common_words
    if all_words:
        return random.choice(all_words)
    return None


def create_cards(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=2)

    word = get_random_word(user_id)

    if word:
        if isinstance(word, Word):
            target_word = word.target_word
            translate_word = word.translate_word
        elif isinstance(word, CommonWord):
            target_word = word.target_word
            translate_word = word.translate_word
        else:
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте позже.")
            return

        all_words = session.query(Word.translate_word).filter(Word.target_word != target_word).all()
        all_words.extend(session.query(CommonWord.translate_word).filter(CommonWord.target_word != target_word).all())
        other_words = random.sample(all_words, 3)
        buttons = [types.KeyboardButton(translate_word)] + [types.KeyboardButton(w[0]) for w in other_words]
        random.shuffle(buttons)

        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        buttons.extend([next_btn, add_word_btn, delete_word_btn])
        markup.add(*buttons)

        greeting = f'Выберите правильный перевод слова \U0001F1F7\U0001F1FA:\n {target_word}'
        bot.send_message(message.chat.id, greeting, reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_word'] = target_word
            data['translate_word'] = translate_word


@bot.message_handler(commands=['cards', 'start'])
def start_bot(message):
    user_id = message.from_user.id
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        new_user = User(id=user_id)
        session.add(new_user)
        session.commit()
    bot.send_message(message.chat.id,
                     "Здравствуйте 👋\n\n Давайте улучшим свои навыки в английском языке.\n "
                     "Ты можешь выбрать свой собственный темп обучения, чтобы максимально эффективно использовать время.\n\n"
                     "Причём у тебя есть возможность использовать тренажёр как конструктор "
                     "и собирать свою собственную базу для обучения.\n "
                     "Для этого используйте функции Добавить слово\u2795 или Удалить слово\u2B05.\n\n"
                     "Ну что, начнём \u2B07\uFE0F", reply_markup=types.ReplyKeyboardRemove())

    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word_start(message):
    cid = message.chat.id
    user_id = message.from_user.id

    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        new_user = User(id=user_id)
        session.add(new_user)
        session.commit()

    bot.send_message(cid, "Введите слово на русском \U0001F1F7\U0001F1FA:")
    bot.set_state(user_id, MyStates.add_word, cid)


@bot.message_handler(state=MyStates.add_word)
def add_word_process(message):
    cid = message.chat.id
    target_word = message.text
    bot.send_message(cid, f"Введите перевод слова \U0001f1ec\U0001f1e7 '{target_word}':")
    with bot.retrieve_data(message.from_user.id, cid) as data:
        data['target_word'] = target_word
    bot.set_state(message.from_user.id, MyStates.translate_word, cid)


@bot.message_handler(state=MyStates.translate_word)
def add_word_translate(message):
    cid = message.chat.id
    translate_word = message.text
    with bot.retrieve_data(message.from_user.id, cid) as data:
        data['translate_word'] = translate_word
        target_word = data['target_word']
        user_id = message.from_user.id

    new_word = Word(target_word=target_word, translate_word=translate_word, user_id=user_id)
    session.add(new_word)
    session.commit()

    bot.send_message(cid, "Слово успешно добавлено!")

    total_words = session.query(Word).filter_by(user_id=user_id).count()

    bot.send_message(cid, f"Вы изучаете {total_words} слова.")

    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word_start(message):
    cid = message.chat.id
    bot.send_message(cid, "Введите слово на русском, которое хотите удалить \U0001F1F7\U0001F1FA:")
    bot.set_state(message.from_user.id, MyStates.delete_word, cid)


@bot.message_handler(state=MyStates.delete_word)
def delete_word_process(message):
    cid = message.chat.id
    target_word = message.text
    user_id = message.from_user.id

    word_to_delete = session.query(Word).filter_by(target_word=target_word, user_id=user_id).first()
    if word_to_delete:
        session.delete(word_to_delete)
        session.commit()
        bot.send_message(cid, f"Слово '{target_word}' успешно удалено!")
    else:
        bot.send_message(cid, f"Слово '{target_word}' не найдено.")
    bot.delete_state(user_id, cid)
    create_cards(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    cid = message.chat.id
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)

    with bot.retrieve_data(message.from_user.id, cid) as data:
        translate_word = data['translate_word']
        target_word = data['target_word']

    if text == translate_word:
        answer = (f"Отлично!\U0001f600\n{target_word} -> \U0001f1ec\U0001f1e7 {translate_word}")
    else:
        answer = "\u274CДопущена ошибка! Попробуйте ещё раз"

    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons = [next_btn, add_word_btn, delete_word_btn]
    markup.add(*buttons)
    bot.send_message(cid, answer, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling(skip_pending=True)