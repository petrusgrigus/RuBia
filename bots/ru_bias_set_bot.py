# ======= used packages ==========

import json
import numpy as np
import os
from collections import defaultdict

import telebot
from telebot import types


# ======= processing messages within one task ==========

class TaskGenerator():
    def __init__(self, bot, task_path, task_dom):
        self.bot = bot

        task_file = open(task_path, "r")
        task_text = task_file.read()
        steps = task_text.split('===\n')
        self.task_path = os.path.join(ans_folder,
                            task_domains[task_dom],
                            task_path.split('/')[-1][:-4])
        self.steps = steps
        self.answers = []

    def give(self, step, msg):
        answer = msg.text.strip()

        if answer == TEXT_BREAK:
            bot.send_message(msg.chat.id, BREAK_MSG, reply_markup=inter_markup)
            return

        if step != 0:
            self.answers.append(answer)

        if step == len(self.steps):
            bot.send_message(msg.chat.id, FINISH_MSG, reply_markup=inter_markup)
            
            ind = msg.chat.id
            filename = os.path.join(self.task_path,
                            (str(ind) + '_' + 
                            str(user_complete[ind]) + '.txt'))

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            user_complete[ind] += 1
            with open(filename, "w") as f:
                f.write("===".join(self.answers))
            return

        else:
            bot.send_message(msg.chat.id, self.steps[step], reply_markup=task_markup)
            self.bot.register_next_step_handler(msg, lambda msg: 
                                            self.give(step + 1, msg))
            


# ======= setting starting state ==========

with open("config.json", "r") as read_file:
    config = json.load(read_file)

bot = telebot.TeleBot(config['id'])

# texts for tasks and file locations
HELLO_MSG = open(config['greeting'], 'r').read()
BREAK_MSG = open(config['break'], 'r').read()
FINISH_MSG = open(config['finish'], 'r').read()
MISTAKE_MSG = open(config['mistake'], 'r').read()

ans_folder = config['ans_folder']
domains = config['domains']
task_list, task_probs, task_domains = [], [], []

N_DOM = len(domains)
for domain in domains:
    task_folder = domain['task_folder']
    task_list.append([task_folder + x for x in domain['tasks']])
    task_probs.append(np.array(domain['probs']))
    task_domains.append(domain['name'])

# user data
user_complete = defaultdict(int)
user_domain = defaultdict(int)
user_task = defaultdict(int)


# ======= markups for bot states ==========

# markup for starting state
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
TEXT_NEW = "Новое задание!"
new_task = types.KeyboardButton(TEXT_NEW)
start_markup.add(new_task)

# markup for between tasks
inter_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
TEXT_SAME = "Задание на ту же тему!"
TEXT_DIFF = "Задание на новую тему!"
inter_same_task = types.KeyboardButton(TEXT_SAME)
inter_diff_task = types.KeyboardButton(TEXT_DIFF)
inter_markup.add(inter_same_task)
inter_markup.add(inter_diff_task)

# markup for in-task state
task_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
TEXT_BREAK = "Прервать задание!"
break_task=types.KeyboardButton(TEXT_BREAK)
task_markup.add(break_task)

# ======= message read-reply cycle ==========

# startup message
@bot.message_handler(commands=["start"])
def start(message, res=False):
    ind = message.chat.id
    bot.send_message(ind, HELLO_MSG, reply_markup=start_markup)
    user_domain[ind] = np.random.randint(N_DOM)

# reply clause
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global last_task, open_task
    query = message.text.strip()
    ind = message.chat.id
        
    if query == TEXT_NEW or query == TEXT_SAME or query == TEXT_DIFF:
        if query == TEXT_DIFF:
            user_domain[ind] = (user_domain[ind] + 1) % N_DOM
            
        task_dom = user_domain[ind]
        task_path = np.random.choice(task_list[task_dom],
                                     p=task_probs[task_dom] / 
                                     sum(task_probs[task_dom]))
        
        task = TaskGenerator(bot, task_path, task_dom)
        user_complete[ind] += 1
        task.give(0, message)

    else:
        if user_complete[ind] == 0:
            bot.send_message(message.chat.id, MISTAKE_MSG, reply_markup=start_markup)
        else:
            bot.send_message(message.chat.id, MISTAKE_MSG, reply_markup=inter_markup)
        

# ======= running loop ==========
        
bot.infinity_polling(timeout=10, long_polling_timeout = 5)
