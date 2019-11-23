import mysql.connector
from mysql.connector import Error
import tweepy
import json
from dateutil import parser
import time
import re
import os
import subprocess
from tweeter_app_credential import *
from googletrans import Translator
import requests


"""
Nota Bene sui requirements:

pip install mysql-connector (per versioni precedenti alla 8.0 di MySQL)

pip install mysql-connector-python (per versioni dalla 8.0 di MySQL)
che utilizzano Authentication plugin 'caching_sha2_password'

Per forzare l'uso di mysql_native_password invece di caching_sha2_password:
cnx = mysql.connector.connect(user='elle', password='password', host='127.0.0.1',
database='test', auth_plugin='mysql_native_password')

"""
# If I have keys and password in a file:
#
# importing file which sets env variable
# subprocess.call("./settings.sh", shell = True) #in questo file sono contenuti le chiavi ma io preferisco utilizzare uno script esterno
#
# consumer_key = os.environ['CONSUMER_KEY']
# consumer_secret = os.environ['CONSUMER_SECRET']
# access_token = os.environ['ACCESS_TOKEN']
# access_token_secret = os.environ['ACCESS_TOKEN_SECRET']
# password = os.environ['PASSWORD'] #la password del database

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')
"""
Connesione con il database MySQL
"""
def connect_tweet(tweet_created_at, tweet_id_str, tweet_text, tweet_truncated, tweet_place_country, tweet_place_full_name, tweet_retweet_count, tweet_favorite_count, tweet_favorited, tweet_lang, user_id, user_id_str, user_name):
   
    """
    translator = Translator()
    
    try:
        traduzione = translator.translate(tweet_text, dest='en')
        print(traduzione.text)
    except Exception as e:
        print(str(e))
    """
    
    """
    connect to MySQL database and insert twitter data
    """
    try:
        con = mysql.connector.connect(host = 'localhost', database='xfactor_db', user='root', password = 'root', charset = 'utf8')
        if con.is_connected():
            """
            Insert twitter data
            """
            cursor = con.cursor()

            
            tweet_text = deEmojify(tweet_text)
            user_name = deEmojify(user_name)

            #tweet_text = '{}'.format(tweet_text)
            #user_name = '{}'.format(user_name)
            query = """INSERT INTO tweet (tweet_created_at, tweet_id_str, tweet_text, tweet_truncated, tweet_place_country, tweet_place_full_name, tweet_retweet_count, tweet_favorite_count, tweet_favorited, tweet_lang,
            user_id, user_id_str, user_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, (tweet_created_at, tweet_id_str, tweet_text, tweet_truncated, tweet_place_country, tweet_place_full_name, tweet_retweet_count, tweet_favorite_count, tweet_favorited, tweet_lang,
            user_id, user_id_str, user_name))
            print("Last Id Tweeet "+ str(cursor.lastrowid))
            last_id_tweet = cursor.lastrowid
            
            con.commit()
            cursor.close()
            con.close()
            return last_id_tweet
            
    except Error as e:
        print(e)
        return None


def connect_hashtag(tweet_id,hashtag_text):
    
    
    """
    connect to MySQL database and insert twitter data
    """
    try:
        con = mysql.connector.connect(host = 'localhost', database='xfactor_db', user='root', password = 'root', charset = 'utf8')

        if con.is_connected():
            """
            Insert twitter data
            """
            cursor = con.cursor()
            
            
            query = """SELECT * FROM hashtag WHERE text LIKE %s"""
            cursor.execute(query, (hashtag_text,))
            records = cursor.fetchall()
            
            if cursor.rowcount > 0:
                for row in records:
                    hashtag_id = row[0]
                    break
            else:
                query = """INSERT INTO hashtag (text) VALUES (%s)"""
                cursor.execute(query, (hashtag_text,))
                hashtag_id = cursor.lastrowid
            

            query1 = """INSERT INTO contiene (id_tweet, id_hashtag) VALUES (%s, %s)"""
            cursor.execute(query1, (tweet_id, hashtag_id))
            con.commit()
            

    except Error as e:
        print(e)

    cursor.close()
    con.close()
    return

"""
StreamListener che fa l'ovveride dei metodi le listener di tweepy
"""
class Streamlistener(tweepy.StreamListener):

    def on_connect(self):
        print("You are connected to the Twitter API")

    def on_error(self, status_code):
        if status_code != 200:
            print("error found")
            print(status_code)
            # returning false disconnects the stream
            return False

    """
    This method reads in tweet data as Json and extracts the data we want.
    """

   

    def on_data(self,data): #data è string
        
        
        try:
            tweet = json.loads(data)
            if 'text' in tweet: # se non ci fosse la chiave text il tweet sarebbe vuoto
                tweet_created_at = parser.parse(tweet['created_at'])
                #tweet_id = tweet['id'] # int64
                tweet_id_str = tweet['id_str'] # string
                # tweet_text = tweet['text']
                try:
                    tweet_text = tweet['full_text']  #string
                    
                except AttributeError:
                    tweet_text = tweet['text']
                except KeyError:
                    tweet_text = tweet['text']
                tweet_truncated = tweet['truncated'] # boolean
                

                # Definite qui perché se il tweet non contiene il campo place devo comunque dichiararlo
                tweet_place_country = None
                tweet_place_full_name = None
                if tweet['place'] is not None:
                    if tweet['place']['country']:
                        tweet_place_country = tweet['place']['country']
                    else:
                        tweet_place_country = None

                    if tweet['place']['full_name']:
                        tweet_place_full_name = tweet['place']['full_name']
                    else:
                        tweet_place_full_name = None

                tweet_retweet_count = tweet['retweet_count'] # int
                tweet_favorite_count = tweet['favorite_count'] # Integer
                tweet_favorited = tweet['favorited'] # boolean
                tweet_lang = tweet['lang'] # String

                user_id = tweet['user']['id'] # int64
                user_id_str = tweet['user']['id_str'] # string
                user_name = tweet['user']['name'] # string

                last_id = connect_tweet(tweet_created_at, tweet_id_str, tweet_text, tweet_truncated, tweet_place_country, tweet_place_full_name, tweet_retweet_count, tweet_favorite_count, tweet_favorited, tweet_lang,
                user_id, user_id_str, user_name)
                if last_id is not None:
                    hashtags = tweet['entities']['hashtags']
                    
                    if len(hashtags)>0:
                        for i in hashtags: 
                            hashtag = i['text']
                            connect_hashtag(last_id, hashtag)
                    else:
                        print("Non ci sono hashtag")
                else:
                    print("impossibile aggiungere tweet")
                #connect_hashtag(last_id, hashtag)
                
                #Insert data just collected into MySQL database
                
                
                
                print("Tweet about X Factor 13: {} ".format(tweet_text))
                print("")
        except Error as e:
            print(e)

"""
Main
"""
if __name__== '__main__':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True)

    # Create instance of Streamlistener
    listener = Streamlistener(api = api)
    stream = tweepy.Stream(auth, listener = listener, tweet_mode='extended')

    # Choose what we want to filter by
    track = ['DavideRossi', 'EugenioCampagna', 'Seawards','NicolaCavallaro', 'GiordanaPetralia', 'SofiaTornambene', 'Booda', 'Sierra', 'SferaEbbasta', 'SamuelRomano', 'MaraMaionchi', 'MalikaAyane', 'XF13', 'XFactor13']
    stream.filter(track = track, languages = ['it'])
