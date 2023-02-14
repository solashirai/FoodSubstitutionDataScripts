### Scripts for ingredient substitution work

This repository contains various scripts used to parse data and run experiments for work involved with
ingredient substitution, from our publication [Identifying Ingredient Substitutions Using a Knowledge Graph of Food](https://www.frontiersin.org/articles/10.3389/frai.2020.621766/full).

Many pieces of code here rely on using some parts of [FoodKG](https://foodkg.github.io/foodkg.html).

You can set up a python virtualenv and install all requirements found in the requirements.txt.

The parse_fooddotcom_reviews directory contains scripts to parse through review data from food.com (which can
be obtained [here](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions)) to collect
potential ingredient substitutions from user comments. Some more details can be found in the directory's README file.

The experiment_code directory contains scripts used to compute scores for ingredient substitutability. Some more details can be found in the directory's README file.

**DEPRECATED**

The foodsubs_scraping directory contains some basic webscraping scripts used to collect data from 
[The Cook's Thesaurus](http://foodsubs.com). Some more details can be found in the directory's README file.

This webscraping code is no longer functional due to major changes in the structure of foodsubs.com, and is only left here for posterity.
We also do not have permission to share the data we originally scraped from this website, so experiments should instead rely on the food.com review data.
