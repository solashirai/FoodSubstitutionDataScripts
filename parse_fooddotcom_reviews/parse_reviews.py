import json
import re
import pickle

save_file = 'recipe_level_comment_content_with_keywords.pkl'

recipe_level = False

if recipe_level:
    import csv

    comment_data = []
    recipe_data = []
    with open('RAW_interactions.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        skipfirst = True
        for line in reader:
            if skipfirst:
                skipfirst = False
                continue
            comment_data.append(line[4])
            recipe_data.append(line[1])
    with open('foodcom_id_to_recipe1m_id.pkl', 'rb') as f:
        foodcom_id_to_r1m_id = pickle.load(f)
else:
    with open('only_review_data.json', 'r') as f:
        comment_data = json.load(f)

# replace a with b
# substitute b for a
# substitute a with b
# a instead of b
# a in place of b
# plural/singular forms
# past tense
# 'subbed'
bad_templates = [
    r'not\ssubstitute[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'not\sreplace[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'not\ssub[bed]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'not\ssubstitute[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'not\sreplace[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'not\ssub[bed]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'n\'t\ssubstitute[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'n\'t\sreplace[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'n\'t\ssub[bed]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'n\'t\ssubstitute[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'n\'t\sreplace[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'n\'t\ssub[bed]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
                 ]
sub_templates = [
    r'substitute[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'replace[d]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'sub[bed]*(?P<sub>[\s[a-z]*]*?)\sfor(?P<source>[\s[a-z]*]*?)',
    r'substitute[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'replace[d]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
    r'sub[bed]*(?P<source>[\s[a-z]*]*?)\swith(?P<sub>[\s[a-z]*]*?)',
                 ]
sub_iterators = [re.compile(regex) for regex in sub_templates]
bad_iterators = [re.compile(regex) for regex in bad_templates]

has_keywords = []
full_comments_containing_keywords = set()
finished = 0
for comment_ind, raw_comment in enumerate(comment_data):
    finished += 1
    if finished % 100000 == 0:
        print(finished)
    comment = raw_comment.lower()
    candidates = []
    candidate_str = []
    bad_candidate_str = []
    for iterator in sub_iterators:
        for match in iterator.finditer(comment):
            candidate_str.append(match.group())
            candidates.append(match.groupdict())
    if not candidates:
        continue
    else:
        for iterator in bad_iterators:
            for match in iterator.finditer(comment):
                bad_candidate_str.append(match.group())
    for ind, comment_str in enumerate(candidate_str):
        if not any(comment_str in bad_str for bad_str in bad_candidate_str):
            if recipe_level:
                r1m_id = foodcom_id_to_r1m_id.get(recipe_data[comment_ind], 0)
                if r1m_id:
                    has_keywords.append((r1m_id, candidates[ind]))
            else:
                has_keywords.append(candidates[ind])
            full_comments_containing_keywords.add(comment)

print("done")
print('number with keyword match: ', len(has_keywords))

with open(save_file, 'wb') as f:
    pickle.dump(has_keywords, f)

# print(has_keywords)