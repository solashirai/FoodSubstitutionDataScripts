### Data

obtain RAW_interactions.csv from https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions

construct the [FoodKG](https://foodkg.github.io/foodkg.html). This should yield you 1 or more files used to link
FoodKG ingredients to FoodOn classes (e.g. named 'foodon-links.trig'). modify the food_link_files variable in the
foodcom_review_raw_names_to_uris script to point to that file containing foodon links.

### Running the scripts

- Run the simplify script

- Run the parse_reviews script

- Run the foodcom_review_raw_names_to_uris script. by default this should output substitution data to data/out/fooddotcom_review_sub_data.json.