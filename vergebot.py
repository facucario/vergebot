import requests
import re
import shutil
from bs4 import BeautifulSoup
from twython import Twython
from decouple import config

twitter_acc = Twython(config("APP_KEY"), config("APP_SECRET"),
                  config("OAUTH_TOKEN"), config("OAUTH_TOKEN_SECRET"))

def download_image(background_image_url):
    r = requests.get(background_image_url, stream = True)
    r.raw.decode_content = True
    with open("background.jpg","wb") as f:
        shutil.copyfileobj(r.raw, f)

def tweet(tweet_body, background_image_url):
    with open("last_tweet.txt", "w") as text_file:
        text_file.write(tweet_body + " " + background_image_url)

    download_image(background_image_url)
    image = open("background.jpg", "rb")
    response = twitter_acc.upload_media(media=image)
    twitter_acc.update_status(status=tweet_body, media_ids=[response["media_id"]])

def _main():
    
    # Get HTML from website
    req = requests.get("https://www.theverge.com")
    soup = BeautifulSoup(req.text, "lxml")

    # Find image URL
    background_image = soup.find("div", class_="c-masthead__main").get("style")
    background_image_url= re.search("(?P<url>https?://[^\s]+)", background_image).group("url")[:-1]

    # Find tagline text and URL
    tag = soup.find("span", class_="c-masthead__tagline")
    link = tag.a.get("href")
    tagline = tag.string
    current_tweet_body = (tagline + " " + link)

    # Check for changes
    try:
        with open("last_tweet.txt", "r") as text_file:
            last_tweet = text_file.read()
            current_tweet = current_tweet_body + " " + background_image_url
            if current_tweet != last_tweet:
                tweet(current_tweet_body, background_image_url)
    except:
        open("last_tweet.txt","w+")
        tweet(current_tweet_body, background_image_url)

if __name__ == "__main__":
    _main()
