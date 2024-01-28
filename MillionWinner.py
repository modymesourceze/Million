# @elhyba & @up_uo
from mody import Mody
import telebot
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, Message, CallbackQuery
from funcs import read, write
import random
import time
import os
import threading


bot_token = Mody.ELHYBA
bot = TeleBot(bot_token, parse_mode="Markdown")
db_path = "MillionUsers.json"
db_bests = "Millioners.json"
db_questions = "questions.json"


@bot.message_handler(commands=["start", "million"])
@bot.message_handler(func = lambda message: message.text == "المليون")
def start(message: Message):
    user_id = message.from_user.id
    user = message.from_user.first_name if not message.from_user.last_name else message.from_user.first_name + message.from_user.last_name
    if str(user_id) not in users:
        users[str(user_id)] = {
            "budget" : 0,
        }
        write(db_path, users)
    best_list = read(db_bests)
    best_players = "".join(best_list)
    caption = f"""
مرحبا بك عزيزي {user} في لعبة من سيربح المليون

قائمة أفضل لاعبين :\n\n
{best_players}
"""
    markup = Keyboard(
        [ # @elhyba & @up_uo
            [
                Button("- قواعد اللعبه -", callback_data=f"rules-{user_id}"),
                Button("- إبدأ اللعب -", callback_data=f"play-{user_id}")
            ],
            [
                Button("- المطور -", "elhyba.t.me")
            ]
        ]
    )
    bot.reply_to(
        message,
        caption,
        reply_markup=markup
    )


@bot.callback_query_handler(func= lambda callback: "rules" in callback.data)
def rules(callback: CallbackQuery):
    data = callback.data.split("-")
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id 
    if user_id != int(data[1]):
        bot.answer_callback_query(callback.id, "بطل لعب ف حاجه مش بتاعتك 👀", show_alert=True)
        return
    caption = """
• هناك 15 سؤالأ يمكنك الإجابه عنهم.

• كل سؤال له وقت محدد للإجابه ( 60 ثانيه ).

• مع كل سؤال صحيح تزداد ميزانيتك.

• اذا قمت بإجابه خاطئه يتم تصفية ميزانيتك بالكامل.

• عند الوصول للمليون سيتم اضافتك لقائمة الشرف.
"""
    markup = Keyboard(
        [
            [
                Button("- العوده -", callback_data=f"million_start-{user_id}")
            ]
        ]# @elhyba & @up_uo
    )
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=callback.message.id,
        text=caption,
        reply_markup=markup
    )
    

@bot.callback_query_handler(func= lambda callback: "million_start" in callback.data)
def restart(callback: CallbackQuery):
    data = callback.data.split("-")
    user_id = callback.from_user.id
    user = callback.from_user.first_name if not callback.from_user.last_name else callback.from_user.first_name + callback.from_user.last_name
    if user_id != int(data[1]):
        bot.answer_callback_query(callback.id, "بطل لعب ف حاجه مش بتاعتك 👀", show_alert=True)
        return
    best_list = read(db_bests)
    best_players = "".join(best_list)
    caption = f"""
مرحبا بك عزيزي {user} في لعبة من سيربح المليون

قائمة أفضل لاعبين :\n\n
{best_players}
"""
    markup = Keyboard(
        [ 
            [
                Button("- قواعد اللعبه -", callback_data=f"rules-{user_id}"),
                Button("- إبدأ اللعب -", callback_data=f"play-{user_id}")
            ],
            [
                Button("- المطور -", "elhyba.t.me")
            ]
        ]
    )
    bot.edit_message_text(
        message_id=callback.message.id, 
        chat_id=callback.message.chat.id,
        text=caption,
        reply_markup=markup
    )# @elhyba & @up_uo


@bot.callback_query_handler(func= lambda callback: "play" in callback.data)
def play(callback: CallbackQuery):
    data = callback.data.split("-")
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    user = callback.from_user.first_name if not callback.from_user.last_name else callback.from_user.first_name + callback.from_user.last_name
    if user_id != int(data[1]):
        bot.answer_callback_query(callback.id, "بطل لعب ف حاجه مش بتاعتك 👀", show_alert=True)
        return
    random.shuffle(questions)
    card = random.choice(questions)
    question = card["question"]
    options = card["options"]
    answer = card["correct_option"]
    random.shuffle(options)
    markup = []
    for index in range(0, len(options), 2):
        markup.append([
            Button(options[index], callback_data=f"answer_{'True-' + answer if options[index] == answer else False}-{user_id}"),
            Button(options[index+1], callback_data=f"answer_{'True-' + answer if options[index+1] == answer else False}-{user_id}")
        ])# @elhyba & @up_uo
    caption = f"""
- اللاعب {user}
- ميزانيتك : {users[str(user_id)]["budget"]}

- السؤال :
{question}
"""
    thread_id = str(random.randint(2872, 38636299))
    markup.append([Button("60 sec", callback_data=thread_id)])
    sent_message = bot.edit_message_text(
        message_id=callback.message.id, 
        chat_id=chat_id,
        text=caption, 
        reply_markup=Keyboard(markup),
    )
    threads[str(thread_id)] = True
    thread = threading.Thread(
        target=loop, 
        args=(sent_message, thread_id,),
    )
    thread.start()
# @elhyba & @up_uo

@bot.callback_query_handler(func= lambda callback: "answer" in callback.data)
def get_answer(callback: CallbackQuery):
    try:
        thread_id = callback.message.reply_markup.keyboard[-1][0].callback_data
        threads[thread_id] = False
    except IndexError:
        pass
    data = callback.data.split("-")
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    user = callback.from_user.first_name if not callback.from_user.last_name else callback.from_user.first_name + callback.from_user.last_name
    if user_id != int(data[-1]):
        bot.answer_callback_query(callback.id, "بطل لعب ف حاجه مش بتاعتك 👀", show_alert=True)
        return
    budget = users[str(user_id)]["budget"]
    new_markup = Keyboard(
            [
                [
                    Button("- قواعد اللعبه -", callback_data=f"rules-{user_id}"),
                    Button("- إلعب من جديد -", callback_data=f"play-{user_id}")
                ],
                [
                    Button("- المطور -", "elhyba.t.me")
                ]
            ]
        )
    if "False" in data[0]:
        users[str(user_id)]["budget"] = 0
        write(db_path, users)
        caption = f"""
- اللاعب {user}
- آجابه خاطئه
- تم تصفية ميزانيتك
"""
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=callback.message.id, 
            text=caption, 
            reply_markup=new_markup
        )
        return
    if budget in (0 ,200):
      budget += 100
    elif budget not in (64000, 300):
        budget = budget * 2
    elif budget == 300:
        budget += 200
    elif budget == 64000:
        budget += 61000
        # @elhyba & @up_uo
    if budget == 1000_000:
        users[str(user_id)]["budget"] = budget
        write(db_path, users)
        bests[f"- {user_id}"] = budget
        write(db_bests, bests)
        caption =f"""
- اللاعب {user}
- تهانينا لقد وصلت إلى نهاية اللعبه
- اصبحت ميزانيتك :  {users[str(user_id)]["budget"]}
- تمت إضافك إلى قائمة أفضل اللاعبين.
- سيظهر الأيدي الخاص بك عندما تضغط /start
"""
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=callback.message.id, 
            text=caption,
            reply_markup=new_markup
        )
        return
        # @elhyba & @up_uo
    users[str(user_id)]["budget"] = budget
    write(db_path, users)
    random.shuffle(questions)
    card = random.choice(questions)
    question = card["question"]
    options = card["options"]
    answer = card["correct_option"]
    random.shuffle(options)
    markup = []
    for index in range(0, len(options), 2):
        markup.append([
            Button(options[index], callback_data=f"answer_{'True ' + answer if options[index] == answer else False}-{user_id}"),
            Button(options[index+1], callback_data=f"answer_{'True ' + answer if options[index+1] == answer else False}-{user_id}")
        ])
    caption = f"""
- اللاعب {user}
- إجابه صحيحه.
- ميزانيتك : {users[str(user_id)]["budget"]}

- السؤال :
{question}
"""
    thread_id = str(random.randint(2872, 38636299))
    markup.append([Button("60 sec", callback_data=thread_id)])
    sent_message = bot.edit_message_text(
        message_id=callback.message.id, 
        chat_id=chat_id,
        text=caption, 
        reply_markup=Keyboard(markup),
    )
    threads[str(thread_id)] = True
    thread = threading.Thread(
        target=loop, 
        args=(sent_message, thread_id,),
    )
    thread.start()
# @elhyba & @up_uo

def loop(message: Message, thread_id):
    message_id = message.id
    chat = message.chat.id
    timer = 60
    timed = threads.get(thread_id)
    markup = message.reply_markup.keyboard
    user_id = markup[0][0].callback_data.split("-")[1]
    if timed:
        while True:
            if not threads.get(thread_id):
                break
            if timer != 0:
                time.sleep(1)
                timer -= 1
                sec = timer
                markup[-1][0].text = f" {sec} sec"
                markup[-1][0].callback_data = thread_id
                # @elhyba & @up_uo
                if not threads.get(thread_id):
                    break
                bot.edit_message_reply_markup(
                    chat_id= chat,
                    message_id = message_id,
                    reply_markup = Keyboard(markup),
                )
                continue
            threads[thread_id] = False
            user = message.from_user.first_name if not message.from_user.last_name else message.from_user.first_name + message.from_user.last_name
            caption = f"""
- اللاعب {user}
- آجابه خاطئه
- تم تصفية ميزنيتك
"""
            bot.edit_message_text(
                chat_id= chat,
                message_id = message_id,
                text=caption,
                reply_markup=Keyboard(
                    [
                        [
                            Button("- قواعد اللعبه -", callback_data=f"rules-{user_id}"),
                            Button("- إلعب من جديد -", callback_data=f"play-{user_id}")
                        ],
                        [
                            Button("- المطور -", "elhyba.t.me")
                        ]
                    ]
                ))
            return
    return


def dbs_checker(dbs):
    for db in dbs:
        if not os.path.exists(db):
            write(db, {})


dbs_checker([db_path, db_bests])
users = read(db_path)
questions = read(db_questions)
bests = read(db_bests)
threads = {}


bot.infinity_polling()