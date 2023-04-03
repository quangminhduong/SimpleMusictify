from decimal import Decimal
import json
import boto3
import os
print(os.getcwd())

def load_music(musics, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Music')
        for music in musics['songs']:
            title = music['title']
            artist = music['artist']
            year = int(music['year'])
            web_url = music['web_url']
            img_url = music['img_url']
            print("Adding music:", title, artist, year, web_url, img_url)
            music['release_year'] = music.pop('year')
            table.put_item(Item=music)
if __name__ == '__main__':
    with open("SimpleMusictify/AWSCode/a1.json") as json_file:
        music_list = json.load(json_file, parse_float=Decimal)
    load_music(music_list)