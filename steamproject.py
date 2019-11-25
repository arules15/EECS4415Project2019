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
with open ('steam_games.csv') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    line = 0
    for row in csv_reader:
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

        # splitterGenre = []
        # splitterGenre = row['genre'].split(',')
        # for word in splitterGenre:
        #         genreOccur[word] = genreOccur.get(word, 0) + 1

        if 'Need more user reviews to generate a score' in row['all_reviews']:
            continue
        if row['all_reviews']:
            splitterReview1 = row['all_reviews'].split(',(')
            splitterReview2 = splitterReview1[1].split(')')
            # print(row['name'], splitterReview2[0].replace(',', ''))
            reviewCount = int(splitterReview2[0].replace(',', ''))
            re_reviews, extra1 = row['all_reviews'].split('- ')
            percentageReview= extra1.split(' ')
            percentage = percentageReview[0]
            # print(row['name'], row['original_price'])
            # price = float(row['orignal_price'].replace('$', ''))
            gamesReviews.append([row['name'], reviewCount, percentage, row['recent_reviews'],
                                 row['developer'], row['publisher'], row['popular_tags'],
                                 row['game_details'], row['genre'], row['original_price']])
            # gamesReviews[row['name'], row['genre']] = int(splitterReview2[0].replace(',', ''))
            # print(re_reviews)
            # print(percentage)

        # line += 1
        # if line == 5:
        # #
        #     break
genreOccur = sorted(genreOccur.items(), key=lambda x: x[1], reverse=True)
gamesReviews.sort(key = sortSecond, reverse = True)
# gamesReviews = sorted(gamesReviews.items(), key=lambda x: x[1], reverse=True)
num = 0
for x in gamesReviews:
    # splitterGenre = []
    # splitterGenre = row['genre'].split(',')
    # for word in splitterGenre:
    #         genreOccur[word] = genreOccur.get(word, 0) + 1
    print(x)
    num += 1
    if num == 10:
        break
# print (genreOccur)
# df = pd.read_csv("steam_games.csv")

# print(df.head(10))
