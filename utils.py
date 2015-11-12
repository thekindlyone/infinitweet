import os
from itertools import chain
import tweepy
import json
from PIL import Image, ImageFont, ImageOps, ImageDraw
from kitchen.text.converters import to_unicode, to_bytes
import textwrap
from KEYS import *
from ttp import ttp

def auth_step1():
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth_url = auth.get_authorization_url()
    # twitter=Twython(APP_KEY,APP_SECRET)
    # auth=twitter.get_authentication_tokens()
    # OAUTH_TOKEN = auth.request_token
    # OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
    # auth_url=auth['auth_url']
    return auth,auth_url

def auth_step2(auth,pincode):
    auth.get_access_token(pincode)
    final_token=auth.access_token
    final_secret=auth.access_token_secret
    auth.set_access_token(final_token, final_secret)
    twitter=tweepy.API(auth)
    # twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    # final_step = twitter.get_authorized_tokens(pincode)
    # final_token = final_step['oauth_token']
    # final_secret = final_step['oauth_token_secret']
    # twitter = Twython(APP_KEY, APP_SECRET, final_token, final_secret)
    with open('creds.json','w') as f:
        json.dump({'oauth_token':final_token,'oauth_token_secret':final_secret},f)
    return(twitter)


def check_stored_tokens():
    if os.path.exists('creds.json'):
        with open('creds.json') as f:
            try:
                final_step=json.load(f)
                final_token = final_step['oauth_token']
                final_secret = final_step['oauth_token_secret']
                auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
                auth.set_access_token(final_token, final_secret)
                twitter=tweepy.API(auth)
                return twitter
            except Exception as e:
                print e
                return None
    else:
        return None



def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)
    
def imagify(text,fn='temp.png'):
    FOREGROUND = (0, 0, 0)
    font_path = 'Times_New_Roman.ttf'
    font = ImageFont.truetype(font_path, 18, encoding='unic')
    # font=ImageFont.load_default()
    text = to_bytes(text)
    # (width, height) = font.getsize(text[0])
    orilines=text.split('\n')
    # print orilines
    lines = list(flatten([textwrap.wrap(oriline, width=80) if oriline else '    ' for oriline in orilines]))
    widths,heights=zip(*[font.getsize(line) if line else font.getsize('A') for line in lines ])
    # print widths,heights
    # print lines
    h=sum(heights)+6*len(lines)
    w=max(widths) +30
    # print h,w
    bg=Image.new('RGBA',(w,h), "#FFFFFF")
    draw = ImageDraw.Draw(bg)
    y_text = 10
    for line in lines:
        if line:
            width, height = font.getsize(line)
        else:
            width, height = font.getsize('A')
            print width,height
        draw.text(((w - width) / 2, y_text), line, font=font, fill=FOREGROUND)
        y_text += height+5        

    with open(fn,'w') as f:
        bg.save(f)
    return fn

parser=ttp.Parser()
def get_tweet_components(text):
    result=parser.parse(text)
    urls=' '.join(result.urls)
    tags=' '.join(['#'+tag for tag in result.tags])
    users=' '.join(['@'+user for user in result.users])
    return '{} {} {}'.format(users,urls,tags)




