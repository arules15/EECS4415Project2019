#!/usr/bin/python

import numpy as np
import csv
from datetime import datetime
from pprint import pprint
import re
#import matplotlib.pyplot as plt
# plt.rcdefaults()
#import matplotlib.pyplot as plt


def wordOccurences(col, list, amount):
    occur = dict()
    # is is for the break counter, row is the value of the list which comes in a list of lists
    for i, row in enumerate(list):
        splitter = []
        # games usually have more than one genre seprated by commas
        splitter = row[col].split(',')
        for word in splitter:
            # sometimes a game has a '' value
            if word not in '':
                occur[word] = occur.get(word, 0) + 1
        if i >= amount:
            break
    # sorts by the highest amount of occurences
    occur = sorted(occur.items(), key=lambda x: x[1], reverse=True)
    return occur

# Used for sorting total list of games by popularity of reviews


def sortSecond(val):
    return val[1]


def sortDate(list):
    # print(list)
    list.sort(key=lambda x: datetime.strptime(x[10], '%b %d, %Y'))
    return list


def getDeveloperGames(name, list, checkDate):
    devList = []
    for row in list:
        if name == row[4]:
            if checkDate:
                if row[10] == 'NaN':
                    continue
                elif re.sub(r"(\w+ \d{4})", '', row[10]) == '':
                    row[10] = re.sub(r"(\s)", ' 1, ', row[10])
                    devList.append(row)
                else:
                    devList.append(row)
            else:
                devList.append(row)
    return devList


def gameDateDevCorr(name, list):
    simpleList = []
    devList = getDeveloperGames(name, list, True)
    sortedDevList = sortDate(devList)
    # sortedDevList = devList.sort(key=lambda date: datetime.strptime(date, "%b %d, %y"))
    for i in sortedDevList:
        # simpleList.append([[i[0], [[i[1], i[2]], i[3]]], [[i[4], i[5]], i[10]]])
        simpleList.append([i[0], i[1], i[2], i[10]])
    # return sortedDevList
    return simpleList

# def getGames(list):
#     gameList = []
#     for row in list:
#         gameList.append(row[0])
#     return gameList

# Choose which rows to filter from the whole list
# 0 = game name, 1 = Review Count, 2 = Percentage of Review Count, 3 = Recent Review List, 4 = Developers
# 5 = Publisher, 6 = Game Tags, 7 = Game Details, 8 = Genre, 9 = Price, 10 = Release Date
# Example getRows(list, 0, 1, 9) will give you the game name, review count and price


def getRows(list, *row):
    newList = []
    rowVal = []
    for i in list:
        for x in row:
            rowVal.append(i[int(x)])
        newList.append(rowVal)
        rowVal = []
    return newList


def main(var):
    gamesReviews = []
    with open('steam_games.csv') as csv_file:
        # with open ('steam_games.csv',encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for i, row in enumerate(csv_reader):
            # if i > 10:
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
                percentageReview = extra1.split(' ')
                percentage = percentageReview[0]
                all_review_list = [reviewCount, percentage]

            if row['recent_reviews']:
                splitterReview1_recent = row['recent_reviews'].split(',(')
                splitterReview2_recent = splitterReview1_recent[1].split(')')
                reviewCount_recent = int(
                    splitterReview2_recent[0].replace(',', ''))
                re_reviews, extra1_recent = row['recent_reviews'].split('- ')
                percentageReview_recent = extra1_recent.split(' ')
                percentage_recent = percentageReview_recent[0]
                recent_review_list = [reviewCount_recent, percentage_recent]

            if row['original_price']:
                row['original_price'].lower()
                if "$" in row['original_price']:
                    Price = row['original_price'].replace('$', '')
                    amount = float(Price)
                    row['original_price'] = amount
                else:
                    row['original_price'] = row['original_price'].replace(
                        row['original_price'], 'Free')

            if 'Downloadable Content' in row['game_details']:
                continue

            if var == 1:
                if str(row['original_price']) in 'Free':
                    continue
            if var == 2:
                if str(row['original_price']) not in 'Free':
                    continue

            gamesReviews.append([row['name'], reviewCount, percentage, recent_review_list,
                                 row['developer'], row['publisher'], row['popular_tags'],
                                 row['game_details'], row['genre'], row['original_price'],
                                 row['release_date']])

    gamesReviews.sort(key=sortSecond, reverse=True)

    if var == 1:  # paid games
        return gamesReviews
    elif var == 2:  # free games
        return gamesReviews
    else:
        return gamesReviews


# gamesReviews = sorted(gamesReviews.items(), key=lambda x: x[1], reverse=True)
# popList = []
popList = main(0)
popListPaid = main(1)
popListFree = main(2)


# print("List of Valve Games ordered from Release Date")
# pprint (gameDateDevCorr('Valve', popList))
# print("List of Bluehole, Inc. Games ordered from Release Date")
# pprint (gameDateDevCorr('Bluehole, Inc.', popList))

genreTotal = wordOccurences(8, popList, 100)
# print("TOP 100 games genre paid and free")
# print(genreTotal)
# print('\n')

# y_pos = np.arange(len(genreTotal))
objects = list(genreTotal)
objects, performance = zip(*objects)
# plt.bar(range(len(genreTotal)), list(genreTotal.value()), align='center', alpha=0.8)
# plt.xticks(range(len(genreTotal)), list(genreTotal.key()))
y_pos = np.arange(len(objects))
#plt.bar(y_pos, performance, align='center', alpha=0.5)
#plt.xticks(y_pos, objects)
#plt.ylabel('positive review in percentage')
#plt.title('DevloperGames rating')
# plt.show()


# genreTotalPaid = wordOccurences(8, popListPaid, 100)
# print("TOP 100 games genre paid")
# print(genreTotalPaid)
# print('\n')

# genreTotalFree = wordOccurences(8, popListFree, 100)
# print("TOP 100 games genre free")
# print(genreTotalFree)
# print('\n')

# detailsTotal = wordOccurences(7, popList, 100)
# print("TOP 100 games details paid and free")
# print(detailsTotal)
# print('\n')

# detailsTotalPaid = wordOccurences(7, popListPaid, 100)
# print("TOP 100 games details paid")
# print(detailsTotalPaid)
# print('\n')

# detailsTotalFree = wordOccurences(7, popListFree, 100)
# print("TOP 100 games details free")
# print(detailsTotalFree)
# print('\n')

# tagsTotal = wordOccurences(6, popList, 100)
# print("TOP 100 games tags paid and free")
# print(tagsTotal)
# print('\n')

# tagsTotalPaid = wordOccurences(6, popListPaid, 100)
# print("TOP 100 games tags paid")
# print(tagsTotalPaid)
# print('\n')

# tagsTotalFree = wordOccurences(6, popListFree, 100)
# print("TOP 100 games tags free")
# print(tagsTotalFree)
# print('\n')
# print('\n')
# print(getRows(popList, 0, 1))

# print("Top games Paid/Free")
# for i,x in enumerate(getGames(popList)):
#     print(x)
#     if i >= 9:
#         print('\n')
#         break
# print('\n')
# print("Testing rows")
# for i,x in enumerate(getRows(popList, 0, 1, 9)):
#     print(x)
#     if i >= 9:
#         print('\n')
#         break
