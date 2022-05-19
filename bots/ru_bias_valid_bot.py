# ======= used packages ==========

import json
import numpy as np
import pandas as pd
import os
from collections import defaultdict

import telebot
from telebot import types

class TaskChecker():
    def __init__(self, bot):
        # row_num is global for sync between users
        global row_num
        self.bot = bot
        
        while data.at[row_num, 'is_clear'] != -1:
            row_num += 1
            
        self.row_num = row_num
            
        if self.row_num >= len(data):
            self.row_num = None
            return
            
        self.row = data.iloc[self.row_num]
        row_num += 1
        
        self.pro = self.row['pro-trope']
        self.anti = self.row['anti-trope']
        self.domain = self.row['domain']
        
        with open(validator_config, "r") as read_file:
            self.validator = json.load(read_file)[self.domain]
        
    def check_clarity(self, message):
        if self.row_num == None:
            bot.send_message(message.chat.id, "Больше заданий пока нет!", reply_markup=start_markup)
            return
        
        bot.send_message(message.chat.id, "Дана пара предложений:\n\n_" +
                         self.pro + "_\n\n_" + self.anti + "_", reply_markup=inter_markup, parse_mode="Markdown")
        bot.send_message(message.chat.id, self.validator[0], reply_markup=inter_markup, parse_mode="Markdown")

        self.bot.register_next_step_handler(message, self.check_closeness)
        
    def check_closeness(self, message):
        query = message.text.strip()
        if query == 'Да' or query == 'Да.' or query == 'Да!':
            data.at[self.row_num, 'is_clear'] = 1
        elif query == 'Нет' or query == 'Нет.' or query == 'Нет!':
            data.at[self.row_num, 'is_clear'] = 0
        else:
            bot.send_message(message.chat.id, MISTAKE_MSG, reply_markup=inter_markup)
            self.bot.register_next_step_handler(message, self.check_closeness)
            return
        
        bot.send_message(message.chat.id, self.validator[1], reply_markup=inter_markup, parse_mode="Markdown")
        self.bot.register_next_step_handler(message, self.finalize)
        
    def finalize(self, message):
        query = message.text.strip() 
        if query == 'Да' or query == 'Да.' or query == 'Да!':
            data.at[self.row_num, 'is_similar'] = 1
        elif query == 'Нет' or query == 'Нет.' or query == 'Нет!':
            data.at[self.row_num, 'is_similar'] = 0
            
        else:
            bot.send_message(message.chat.id, MISTAKE_MSG, reply_markup=inter_markup)
            self.bot.register_next_step_handler(message, self.finalize)
            return
        
        bot.send_message(message.chat.id, "Спасибо!", reply_markup=start_markup)


# ======= setting starting state ==========

with open("config.json", "r") as read_file:
    config = json.load(read_file)

bot = telebot.TeleBot(config['validator_id'])
validator_config = config["validator_config"]

# texts for tasks and file locations
HELLO_MSG = open(config['greeting'], 'r').read()
BREAK_MSG = open(config['break'], 'r').read()
FINISH_MSG = open(config['finish'], 'r').read()
MISTAKE_MSG = open(config['mistake'], 'r').read()

# loading database
data_raw = pd.read_csv("response_table_raw.tsv", sep='\t')
data = pd.read_csv("response_table.tsv", sep='\t')
data = pd.concat([data, data_raw])

row_num = 0

# ======= markups for bot states ==========

# markup for starting state
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
TEXT_NEW = "Новое задание!"
new_task = types.KeyboardButton(TEXT_NEW)
start_markup.add(new_task)

# markup for between tasks
inter_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
TEXT_YES = "Да"
TEXT_NO = "Нет"
inter_yes = types.KeyboardButton(TEXT_YES)
inter_no = types.KeyboardButton(TEXT_NO)
inter_markup.add(inter_yes)
inter_markup.add(inter_no)

# ======= message read-reply cycle ==========

# startup message
@bot.message_handler(commands=["start"])
def start(message, res=False):
    ind = message.chat.id
    bot.send_message(ind, HELLO_MSG, reply_markup=start_markup)

# reply clause
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global last_task, open_task
    query = message.text.strip()
    ind = message.chat.id
        
    if query == TEXT_NEW:
        task = TaskChecker(bot)
        task.check_clarity(message)
        data.to_csv("response_table.tsv", sep="\t", index=False)

    else:
        bot.send_message(message.chat.id, MISTAKE_MSG, reply_markup=start_markup)
        
bot.infinity_polling(timeout=10, long_polling_timeout = 5)
