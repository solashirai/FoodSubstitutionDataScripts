from bs4 import BeautifulSoup
import bs4
from os import listdir
from os.path import isfile, join
import json

files = ['scraped_pages/'+f for f in listdir('scraped_pages/') if isfile(join('scraped_pages/', f))]

# notes tips substitutes pronunciation
# separated by =
# varieties? sometimes

subs_chunks = []
good_chunks_file = 'subs_webcontent_chunks.json'
bad_chunks_file = 'bad_subs_webcontent_chunks.json'

good_tups = []
bad_tups = []
for file in files:
    with open(file,  encoding='cp932', errors='ignore') as f:
        soup = BeautifulSoup(f,  'lxml')

    def contains_subs(elem):
        return (
                getattr(elem, 'name', None)  # is an element, not text
                # and any NavigableText child elements contain the word Cosmos
                and any('Substitutes' in child for child in elem.children
                        if not getattr(child, 'name', None))
        )
    def contains_subs2(elem):
        return (
                getattr(elem, 'name', None)  # is an element, not text
                # and any NavigableText child elements contain the word Cosmos
                and any('Substitutions' in child for child in elem.children
                        if not getattr(child, 'name', None))
        )

    subs_elements = soup.findAll(contains_subs)
    se2 = soup.findAll(contains_subs2)
    subs_elements = [s for s in subs_elements]
    subs_elements.extend([s for s in se2])
    subs_top = []
    for i in range(len(subs_elements)):
        subs_top.append(subs_elements[i].find_parent('td'))
    # subs_top = {sub_elem: sub_elem.find_parent('td') for sub_elem in subs_elements}
    subs_from = []
    subs_to = []
    for k in range(len(subs_elements)):
        subs_to.append(subs_elements[k].parent.next_sibling)
        if subs_top[k] is None:
            subs_top[k] = subs_elements[k].find_parent('p')
            if subs_elements[k].find_parent('p') is None:
                subs_top[k] = subs_elements[k].find_parent('td')
                if subs_top[k] is None:
                    subs_top[k] = subs_elements[k].find_parent('blockquote')

    for i in range(len(subs_top)):
        first_bold = subs_top[i].find_all('b')
        if len(first_bold) > 0:
            subs_from.append(first_bold[0].getText().replace("\n", " "))
        else:
            subs_from.append(" ")

    subs_chunks.extend(subs_top)
    final_tups = []
    error_tups = []
    for s in range(len(subs_elements)):
        s_to = subs_to[s]

        s_from = subs_from[s].replace("\n", " ")
        s_from = s_from.replace(":", "")
        if s_from.find('Substitutes') > 0:
            s_from = s_from[:s_from.find('Substitutes')]
        if s_from.find('Notes') > 0:
            s_from = s_from[:s_from.find('Notes')]
        if s_from.find('Equivalents') > 0:
            s_from = s_from[:s_from.find('Equivalents')]
        if s_from.find('Pronunciation') > 0:
            s_from = s_from[:s_from.find('Pronunciation')]
        if s_from.find('Varieties') > 0:
            s_from = s_from[:s_from.find('Varieties')]
        if s_from.find('To make your own') > 0:
            s_from = s_from[:s_from.find('To make your own')]
        if s_from.find('Shopping hints') > 0:
            s_from = s_from[:s_from.find('Shopping hints')]


        if isinstance(s_to, bs4.element.NavigableString):
            s_to = s_to.replace("\n", " ")
        else:
            s_to = ""

        s_from = s_from.strip()
        s_to = s_to.strip()
        print(s_from)
        if s_from.replace(" ", "") == "" or s_to.replace(" ", "") == "" or\
                s_from == "Substitutes" or s_to == "Substitutes" or s_from == "Tips" or s_to == "Tips":
            error_tups.append((str(s),
                               str(s_from),
                               str(s_to),
                               file))
        else:
            final_tups.append((str(s),
                               str(s_from),
                               str(s_to),
                               file))
    good_tups.extend(final_tups)
    bad_tups.extend(error_tups)


print('good substitute tuples: ', len(good_tups))
print('bad substitutes: ', len(bad_tups))

with open(good_chunks_file, 'w') as f:
    json.dump(good_tups, f)

with open(bad_chunks_file, 'w') as f:
    json.dump(bad_tups, f)
