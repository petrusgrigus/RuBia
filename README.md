# RuBia
A bias detection challenge dataset for the Russian language

# Repository contents 

## Bias scoring
**RuBia_scoring.ipynb** - a notebook, which
1.  Pre-processes the data
2.  Defines metrics used
3.  Tests several MLM models on the dataset
4.  Converts results into a readable format

Our results are given in _results/_ folder

## Bots
**bots/ru_bias_set_bot.py** - a bot for collecting responces to tasks
**bots/collect_data.py** - a script for putting all of the collected responces into a table
**bots/ru_bias_valid_bot.py** - a bot for validating responces stored in the table
**bots/config.json** - a config file, containing paths to tasks, bot ids, etc.

## MLM scoring
**mlm-scoring/fixed_scoring.py** - a fix for mlm-scoring library

Also contains LICENCE and NOTICE of the mlm-scoring library
