### Running the web scraper

- Install scrapy

- Make a new directory, named 'scraped_pages'

- While in this directory, run the web scraper using 'scrapy crawl subs'


### Putting together substitution data

- Install bs4

- Run the soup_extract_subs_from_pages script

- Optionally perform some manual fixes in the output subs_webcontent_chunks.json

- Run the extract_subs_to_foodkg script. By default this script uses spaCy, and requires you to have valid foods from foodkg identified
using some links which are output by the FoodKG construction script (e.g., 'foodon-links-1.trig')
