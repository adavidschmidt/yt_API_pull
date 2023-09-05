import pandas as pd
import requests
import json
import time


df = pd.DataFrame(columns=["Video_id","Video_title","Upload_date",
"View_count","Like_count","Comment_count"])  # setting up our dataframe for future additions

df_name = input('Name your dataset: ')
API_KEY = input('Enter your API key:')
CHANNEL_ID = input('Enter the channel ID:')

def get_video_data(video_id):
    # sets the url to be based on the video id we will get from the next function
    url = "https://www.googleapis.com/youtube/v3/videos?id="+video_id+"&part=statistics&key="+API_KEY  

    response = requests.get(url).json()

    # assign the items we want to pull out of the json to add to a dataframe
    return response['items'][0]['statistics']['viewCount'],\
           response['items'][0]['statistics']['likeCount'],\
           response['items'][0]['statistics']['commentCount']


# Define function to pull videos from the channel_id and use the get_video_data function to pull specific data to a df

def get_video(df):
    pageToken = ''
    
    while 1:

        # set url to be the channel information as well as include a max result count to maintain our quota limit
        url = "https://www.googleapis.com/youtube/v3/search?key="+API_KEY+"&channelId="+CHANNEL_ID+"&part=snippet,id&order=date&maxResults=10000&q=-short&"+pageToken

        response = requests.get(url).json()
        
        # set timer to allow the response request to be fulfilled before moving into the for loop
        time.sleep(2)

        # create a for loop to go through the items generated in the json for the video id to gather the information we are looking for
        for video in response['items']:
            if video['id']['kind'] == 'youtube#video':
                video_id = video['id']['videoId']
                video_title = video['snippet']['title']
                video_title = str(video_title).replace('&amp;','')
                video_title = str(video_title).replace('&#39;',"'")
                upload_date = video['snippet']['publishTime']
                upload_date = str(upload_date).split('T')[0]
                print(upload_date)

                # create data points using information from the prior function
                view_count, like_count, comment_count = get_video_data(video_id)

                # add items gathered to our dataframe
                df = df.append({'Video_id':video_id,
                                'Video_title':video_title,
                                'Upload_date':upload_date,
                                'View_count':view_count,
                                'Like_count':like_count,
                                'Comment_count':comment_count},
                                ignore_index = True)
        # create a try statement to allow the program to continue across multiple pages of video until no new page is available then break the function
        try:
            if response['nextPageToken'] != None:
                pageToken = 'pageToken=' + response['nextPageToken']
        except:
            break

    # edit the data types of the columns to be as expected
    df['Upload_date'] = pd.to_datetime(df['Upload_date'])
    df['View_count'] = df['View_count'].astype(int)
    df['Like_count'] = df['Like_count'].astype(int)
    df['Comment_count'] = df['Comment_count'].astype(int)

    # return the df with the new information added
    return df

df = get_video(df)



df.to_csv(f'{df_name}.csv', index=False)