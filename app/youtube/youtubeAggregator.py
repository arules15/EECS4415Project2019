import pandas as pd
import re

csgo_df = pd.read_csv('minecraft.csv')

avg_ld = 0
avg_v = 0

video_rows = []
for t in csgo_df.itertuples():
    published = t[6]
    if '2019' in str(published):        # get all videos for 2019
        ld_ratio = (int(t[3]) / (int(t[3]) + int(t[4]))) * 100
        # if int(t[4]) == 0:            # ratio
        #     ld_ratio = int(t[3])
        # else:
        #     ld_ratio = int(t[3]) / int(t[4])
        month = re.sub('[^Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec]', '', published)
        video_rows.append([month, ld_ratio, int(t[5])])
        # print(published, ld_ratio, int(t[5]))
videos = pd.DataFrame(video_rows, columns=['month', 'ldratio', 'views'])
m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

month_avg_tuples = []
for mn in m:
    vids_for_month = videos.loc[videos['month'] == mn]
    number_of_vids = len(vids_for_month.index)
    month_avg_tuples.append([mn, vids_for_month['ldratio'].mean(), vids_for_month['views'].mean(), number_of_vids])
month_avgs = pd.DataFrame(month_avg_tuples, columns=['month', 'Average Like/Dislike', 'Average Views', 'Number of videos'])
print(month_avgs)
