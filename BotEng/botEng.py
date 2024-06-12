import os
import random
from dotenv import load_dotenv
from telebot import types, TeleBot, custom_filters
from telebot.handler_backends import State, StatesGroup
from sqlalchemy.sql.expression import func
from models import create_table, Word, Translate, Other, User
from sqlalchemy.orm import sessionmaker
import sqlalchemy

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
NAMEDB = os.getenv('NAMEDB')

TOKEN = os.getenv('TOKEN')
bot = TeleBot(TOKEN)


DSN = f'postgresql://{LOGIN}:{PASSWORD}@localhost/{NAMEDB}'
engine = sqlalchemy.create_engine(DSN)
create_table(engine)


Session = sessionmaker(bind=engine)
session = Session()


class Command:
    ADD_WORD = 'Добавить слов\u2795'
    DELETE_WORD = 'Удалить слово\u2B05'
    NEXT = 'Дальше\u23ED'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()
    example_word = State()
    add_word = State()
    delete_word = State()


def create_cards(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=2)

    word = (session.query(Word).filter((Word.user_id == user_id) | (Word.user_id == 1), Word.mastered == False)
            .order_by(func.random()).first())

    if word:
        target_word = word.target_word
        translate_object = session.query(Translate).filter_by(id_word=word.id).first()
        translate_word = translate_object.translate_word
        example = translate_object.example
        other_words = [other.other_word for other in session.query(Other).filter_by(id_translate=word.id).all()]

        target_word_btn = types.KeyboardButton(translate_word)
        other_word_btn = [types.KeyboardButton(word) for word in other_words]

        buttons = [target_word_btn] + other_word_btn
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
            data['other_words'] = other_words
            data['example'] = example


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
    bot.send_message(cid, "Введите три неправильных варианта перевода, разделяя их запятыми \U0001f1ec\U0001f1e7:")
    bot.set_state(message.from_user.id, MyStates.other_words, cid)


@bot.message_handler(state=MyStates.other_words)
def add_word_other(message):
    cid = message.chat.id
    other_words = message.text.split(",")
    with bot.retrieve_data(message.from_user.id, cid) as data:
        data['other_words'] = other_words
        target_word = data['target_word']
        translate_word = data['translate_word']
        user_id = message.from_user.id

        new_word = Word(target_word=target_word, user_id=user_id)
        session.add(new_word)
        session.flush()

        new_translate = Translate(translate_word=translate_word, word=new_word)
        session.add(new_translate)

        for other_word in other_words:
            new_other = Other(other_word=other_word.strip(), translate=new_translate)
            session.add(new_other)

        session.commit()

        bot.send_message(cid, f"Теперь введите пример использования слова '{translate_word}' "
                              f"на английском \U0001f1ec\U0001f1e7:")
        bot.set_state(message.from_user.id, MyStates.example_word,cid)


@bot.message_handler(state=MyStates.example_word)
def add_example(message):
    cid = message.chat.id
    example = message.text
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, cid) as data:
        target_word = data['target_word']

    word = session.query(Word).filter_by(target_word=target_word).first()

    if word:
        translate = session.query(Translate).filter_by(id_word=word.id).first()
        translate.example = example
        session.commit()

        bot.send_message(cid, "Слово с примером успешно добавлено!")

        total_words = session.query(Word).filter_by(user_id=user_id).count()

        bot.send_message(cid, f"Вы изучаете {total_words} слова.")

    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word_start(message):
    cid = message.chat.id
    bot.send_message(cid, "Введите слово, которое хотите удалить \U0001F1F7\U0001F1FA:")
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

    if text == translate_word:
        user_id = message.from_user.id
        word = session.query(Word).filter_by(target_word=data['target_word'], user_id=user_id).first()

        if word:
            word.attempts += 1
            if word.attempts >= 5:
                word.mastered = True
                answer = (f"Отлично!\U0001f600\n{data['target_word']} -> \U0001f1ec\U0001f1e7 {data['translate_word']} "
                          f"-> {data['example']}\n\U0001f389 Слово '{data['translate_word']}' изучено! \U0001f389")
            else:
                answer = (f"Отлично!\U0001f600\n{data['target_word']} -> \U0001f1ec\U0001f1e7 {data['translate_word']} "
                          f"-> {data['example']}\nОсталось {5 - word.attempts} "
                          f"правильных ответа до изучения слова '{data['translate_word']}'.")
            session.commit()
        else:
            answer = (f"Отлично!\U0001f600\n{data['target_word']} -> \U0001f1ec\U0001f1e7 "
                      f"{data['translate_word']} -> {data['example']}")

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



