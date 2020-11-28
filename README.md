### Scripts for ingredient substitution work

This repository contains various scripts used to parse data and run experiments for work involved with
ingredient substitution (TODO - details to be added if/when the work is published)

Many pieces of code here rely on using some parts of [FoodKG](https://foodkg.github.io/foodkg.html).

You can set up a python virtualenv and install all requirements found in the requirements.txt.

The foodsubs_scraping directory contains some basic webscraping scripts used to collect data from 
[The Cook's Thesaurus](http://foodsubs.com). Some more details can be found in the directory's README file.

The parse_fooddotcom_reviews directory contains scripts to parse through review data from food.com (which can
be obtained [here](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions)) to collect
potential ingredient substitutions from user comments. Some more details can be found in the directory's README file.

The experiment_code directory contains scripts used to compute scores for ingredient substitutability. Some more details can be found in the directory's README file.
