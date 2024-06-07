import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_table, Word, Translate, Other, User


DSN = f'postgresql://postgres:530496@localhost/botTG'
engine = sqlalchemy.create_engine(DSN)
create_table(engine)


Session = sessionmaker(bind=engine)
session = Session()

new_user = User()
session.add(new_user)
session.commit()
user_id = new_user.id

word_1 = Word(target_word='Красный', user_id=user_id)
word_2 = Word(target_word='Собака', user_id=user_id)
word_3 = Word(target_word='Она', user_id=user_id)
word_4 = Word(target_word='Магазин', user_id=user_id)
word_5 = Word(target_word='Кролик', user_id=user_id)
word_6 = Word(target_word='Они', user_id=user_id)
word_7 = Word(target_word='Лифт', user_id=user_id)
word_8 = Word(target_word='Дом', user_id=user_id)
word_9 = Word(target_word='Трава', user_id=user_id)
word_10 = Word(target_word='Дорога', user_id=user_id)


translate_wrd_1 = Translate(translate_word='Red', word=word_1, example="The sky is red tonight.")
translate_wrd_2 = Translate(translate_word='Dog', word=word_2, example="My dog loves playing fetch.")
translate_wrd_3 = Translate(translate_word='She', word=word_3, example="She runs every morning.")
translate_wrd_4 = Translate(translate_word='Shop', word=word_4, example="After work, let's go shop for dinner ingredients.")
translate_wrd_5 = Translate(translate_word='Rabbit', word=word_5, example="Rabbits are fast runners.")
translate_wrd_6 = Translate(translate_word='They', word=word_6, example="They are going on vacation next month.")
translate_wrd_7 = Translate(translate_word='Elevator', word=word_7, example="Please take the elevator to the fourth floor.")
translate_wrd_8 = Translate(translate_word='House', word=word_8, example="This house has a beautiful garden.")
translate_wrd_9 = Translate(translate_word='Grass', word=word_9, example="The grass is greener on the other side of the fence.")
translate_wrd_10 = Translate(translate_word='Road', word=word_10, example="Take the road to the right at the traffic light.")


other_wrd_1 = Other(other_word='Green', translate=translate_wrd_1)
other_wrd_2 = Other(other_word='Yellow', translate=translate_wrd_1)
other_wrd_3 = Other(other_word='Sun', translate=translate_wrd_1)
other_wrd_4 = Other(other_word='Cat', translate=translate_wrd_2)
other_wrd_5 = Other(other_word='Cow', translate=translate_wrd_2)
other_wrd_6 = Other(other_word='Bee', translate=translate_wrd_2)
other_wrd_7 = Other(other_word='He', translate=translate_wrd_3)
other_wrd_8 = Other(other_word='It', translate=translate_wrd_3)
other_wrd_9 = Other(other_word='His', translate=translate_wrd_3)
other_wrd_10 = Other(other_word='Market', translate=translate_wrd_4)
other_wrd_11 = Other(other_word='Bridge', translate=translate_wrd_4)
other_wrd_12 = Other(other_word='Stock', translate=translate_wrd_4)
other_wrd_13 = Other(other_word='Bear', translate=translate_wrd_5)
other_wrd_14 = Other(other_word='Hamster', translate=translate_wrd_5)
other_wrd_15 = Other(other_word='Squirrel', translate=translate_wrd_5)
other_wrd_16 = Other(other_word='Who', translate=translate_wrd_6)
other_wrd_17 = Other(other_word='Why', translate=translate_wrd_6)
other_wrd_18 = Other(other_word='What', translate=translate_wrd_6)
other_wrd_19 = Other(other_word='Car', translate=translate_wrd_7)
other_wrd_20 = Other(other_word='Ladder', translate=translate_wrd_7)
other_wrd_21 = Other(other_word='Eggplant', translate=translate_wrd_7)
other_wrd_22 = Other(other_word='Tent', translate=translate_wrd_8)
other_wrd_23 = Other(other_word='Sea', translate=translate_wrd_8)
other_wrd_24 = Other(other_word='Sand', translate=translate_wrd_8)
other_wrd_25 = Other(other_word='Dew', translate=translate_wrd_9)
other_wrd_26 = Other(other_word='Stone', translate=translate_wrd_9)
other_wrd_27 = Other(other_word='Rain', translate=translate_wrd_9)
other_wrd_28 = Other(other_word='Down', translate=translate_wrd_10)
other_wrd_29 = Other(other_word='Plane', translate=translate_wrd_10)
other_wrd_30 = Other(other_word='Deep', translate=translate_wrd_10)

session.add_all([word_1, word_2, word_3, word_4, word_5, word_6, word_7, word_8, word_9, word_10, translate_wrd_1,
                 translate_wrd_2, translate_wrd_3, translate_wrd_4, translate_wrd_5, translate_wrd_6, translate_wrd_7,
                 translate_wrd_8, translate_wrd_9, translate_wrd_10, other_wrd_1, other_wrd_2, other_wrd_3, other_wrd_4,
                 other_wrd_5, other_wrd_6, other_wrd_7, other_wrd_8, other_wrd_9, other_wrd_10, other_wrd_11, other_wrd_12,
                 other_wrd_13, other_wrd_14, other_wrd_15, other_wrd_16, other_wrd_17, other_wrd_18, other_wrd_19, other_wrd_20,
                 other_wrd_21, other_wrd_22, other_wrd_23, other_wrd_24, other_wrd_25, other_wrd_26, other_wrd_27, other_wrd_28,
                 other_wrd_29, other_wrd_30
                 ])
session.commit()
