#!/usr/bin/python

import csv

def wordOccurences (col, csvx):
    occur = dict()
    for row in csvx:
        splitter = []
        splitter = row[col].split(',')
    for word in splitter:
            occur[word] = occur.get(word, 0) + 1
    occur = sorted(occur.items(), key=lambda x: x[1], reverse=True)
    return occur

def sortSecond(val):
    return val[1]

genreOccur = dict()
gamesReviews = []

with open ('steam_games.csv',encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for i,row in enumerate(csv_reader):
        # if i > 50:
        #     break

        # row names: url, types, name, desc_snippet, recent_reviews, all_reviews,
        # release_date, developer, publisher, popular_tags, game_details,
        # languages, achievements, genre, game_description, mature_content,
        # minimum_requirements, recommended_requirements, original_price,
        # discount_price(wrong?)

        # Reviews come in the form of
        # 'Mostly Positive,(7,030),- 71% of the 7,030 user reviews for...'
        # To get the total we have use two splitters as the total might
        # contain a comma

        if row['types'] != 'app':
            continue

        if 'Need more user reviews to generate a score' in row['all_reviews']:
            continue
        if row['all_reviews']:
            splitterReview1 = row['all_reviews'].split(',(')
            splitterReview2 = splitterReview1[1].split(')')
            reviewCount = int(splitterReview2[0].replace(',', ''))
            allReviews, extra1 = row['all_reviews'].split('- ')
            percentageReview= extra1.split(' ')
            percentage = percentageReview[0]
            all_review_list = [reviewCount, percentage]

        if row['recent_reviews']:
            splitterReview1_recent = row['recent_reviews'].split(',(')
            splitterReview2_recent = splitterReview1_recent[1].split(')')
            reviewCount_recent = int(splitterReview2_recent[0].replace(',', ''))
            re_reviews, extra1_recent = row['recent_reviews'].split('- ')
            percentageReview_recent= extra1_recent.split(' ')
            percentage_recent = percentageReview_recent[0]
            recent_review_list = [reviewCount_recent, percentage_recent]

        if row['original_price']:
            row['original_price'].lower()
            if "$" in row['original_price']:
                Price = row['original_price'].replace('$','')
                amount = float(Price)
                row['original_price'] = amount
            else:
                row['original_price'] = row['original_price'].replace(row['original_price'],'Free')
            

        gamesReviews.append([row['name'], reviewCount, percentage, recent_review_list,
                                row['developer'], row['publisher'], row['popular_tags'],
                                row['game_details'], row['genre'], row['original_price']])

        
genreOccur = sorted(genreOccur.items(), key=lambda x: x[1], reverse=True)
gamesReviews.sort(key = sortSecond, reverse = True)
# gamesReviews = sorted(gamesReviews.items(), key=lambda x: x[1], reverse=True)

for i,x in enumerate(gamesReviews):
    print(x)
    if i > 10:
        break