import re,math,sys
import newspaper
import pickle
import random
import pyrebase
from goose3 import Goose
from collections import Counter
import os, datetime
import pandas as pd
import hashlib
from . import indian_scraper_plug
from langdetect import detect

INDIAN_LANGUAGES = ['hi','guj','ma']

max_article_addition = 15
ideal = 20.0
n_bullets = 4
stopwords = set()

max_sentences = 3
max_articles = 5
max_local_summaries = 10

SUMMARIES = dict()

email="alissaevilis25@gmail.com"
password="lolipop2003@"

config={
        "apiKey": "AIzaSyB-fNpeK90ucBwvHt_mVRjM-X3uboowFjY",
        "authDomain": "briefly-c7ef1.firebaseapp.com",
        "databaseURL": "https://briefly-c7ef1.firebaseio.com",
        "storageBucket": "briefly-c7ef1.appspot.com"
}

firebase = pyrebase.initialize_app(config)
auth=firebase.auth()
user=auth.sign_in_with_email_and_password(email,password)

def refresh(user):
    user=auth.refresh(user['refreshToken'])

db=firebase.database()

def summary(url):
    article=newspaper.Article(url)
    article.download()
    article.parse()
    title = article.title
    date = ""
    try:
	    image=article.top_image
    except:
        image = "http://www.sahalnews.com/wp-content/uploads/2014/12/news-update-.jpg"
    article.nlp()

    iso_lang = detect(title)
    if iso_lang in INDIAN_LANGUAGES:
	    summary = indian_scraper_plug.summary(article.text,article.title,iso_lang)
    else:
        summary = article.summary
    return (title,"",image,summary)

def pinChannel(username,url):
    print(url)
    try:
        value=hashlib.sha224(url.encode('utf-8')).hexdigest()
        sender_id = ''
        users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
        if(len(users.each())):
       	    lis=users.val()
            sender_id=str(lis[username])
        data={'sub':[value]}
        users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
        if(len(users.each())):
            data=users.val()[sender_id]
            if "pin" in data.keys():
                lis=data["pin"]
            else:
                lis=[]
            lis.append(value)
            data['pin']=lis
            print(data)
            db.child("users").child(sender_id).update(data,user['idToken'])
        else:
            print(data)
            db.child("users").child(sender_id).set(data,user['idToken'])
    except:
        refresh(user)
        subChannel(sender_id,value)


def unpinChannel(username,url):
    try:
        sender_id=''
        value=hashlib.sha224(url.encode('utf-8')).hexdigest()
        users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
        if(len(users.each())):
       	    lis=users.val()
            sender_id=str(lis[username])
        data={}
        print(sender_id)
        users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
        if(len(users.each())):
       	    data=users.val()[sender_id]
            if "pin" in data.keys():

                lis=data["pin"]


                if value in lis:
                    lis.remove(value)
                    data["pin"]=lis
                    db.child("users").child(sender_id).update(data,user['idToken'])
    except:
        refresh(user)
        unsubChannel(sender_id,value)


def subChannel(username,value):
    try:
        sender_id = ''
        users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
        if(len(users.each())):
       	    lis=users.val()
            sender_id=str(lis[username])
        data={'sub':[value]}
        users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
        if(len(users.each())):
            data=users.val()[sender_id]
            if "sub" in data.keys():
                lis=users.val()[sender_id]['sub']
            else:
                lis=[]
            lis.append(value)
            data['sub']=lis
            db.child("users").child(sender_id).update(data,user['idToken'])
        else:
            db.child("users").child(sender_id).set(data,user['idToken'])
    except:
        refresh(user)
        subChannel(sender_id,value)
#inactive
def unsubChannel(username,value):
    try:
        sender_id=''
        users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
        if(len(users.each())):
       	    lis=users.val()
            sender_id=str(lis[username])
        data={}
        users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
        if(len(users.each())):
       	    data=users.val()[sender_id]
            if "sub" in data.keys():
                lis=data["sub"]
                if value in lis:
                    lis.remove(value)
                    data['sub']=lis
                    db.child("users").child(sender_id).update(data,user['idToken'])
    except:
        refresh()
        unsubChannel(sender_id,value)



def subscribe_model(source):

    file_name = "sum.pickle"
    load_stopwords('en')

    articles_per_source = dict()

    if os.path.isfile(file_name):
        article_file = open(file_name,"rb")
        articles_per_source = pickle.load(article_file)
        article_file.close()

    article_file = open(file_name,"wb")


    MEMO_flag = False
    if source in articles_per_source.keys():
        MEMO_flag = True

    article_links = []

    now = datetime.datetime.now()
    current_time = now.hour*60 + now.minute



    links = newspaper.build(source,memoize_articles=MEMO_flag)

    for article in links.articles[:min(max_article_addition,len(links.articles))]:
        article_links.append([summary(article.url)])

    if source not in articles_per_source.keys():
        articles_per_source[source] = []
    articles_per_source[source] += article_links
    n_articles = len(articles_per_source[source])
    articles_per_source[source] = articles_per_source[source][:min(n_articles,50)]

    pickle.dump(articles_per_source,article_file)
    article_file.close()

    random.shuffle(articles_per_source[source])

    return articles_per_source[source][-1*min(n_articles-1,3):]

def generate_summaries(url,sentences):
    if "http" not in url:
        url="http://"+url
    links_to_articles = subscribe_model(url)
    available = len(links_to_articles)
    results = []
    for article_url in links_to_articles[:min(available,max_articles)]:
        summar=summary(article_url)
        headline = summar[0]
        publish_date = summar[1]
        top_image_url  = summar[2]
        summaries = summar[3]
        concate_news = ""
        for bullets in summaries:
            concate_news +=  bullets
            concate_news += "\n"
        sum_keys = sorted(SUMMARIES.keys())
        if len(sum_keys) > max_local_summaries :
            del SUMMARIES[0]
        if not len(sum_keys):
            hash_index = 0
        else:
            hash_index = sum_keys[-1]
        results.append([headline,top_image_url,publish_date,concate_news])
        SUMMARIES[hash_index+1] = concate_news
    return results

def generate_feed(username):
        data={}
        users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
        if(len(users.each())):
       	    lis=users.val()
            sender_id=str(lis[username])
            users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
            if(len(users.each())):
                lis=users.val()[sender_id]
                if 'sub' in lis.keys():
                    lis=lis['sub']
                else:
                    return {}
                subl={}
                try:
                    articles_per_source = db.child("sources").get(user['idToken']).val()
                    Uarticle = db.child("article").get(user['idToken']).val()
                except:
                    refresh(user)
                    generate_feed(username)
                result={}
                for i in lis:
                    li=[]
                    if i!=None:
                        if i in articles_per_source.keys():
                            lent=len(articles_per_source[i])
                            hashes=articles_per_source[i][-min(lent,4):]
                        for hashe in hashes:
                            try:
                                li.append(Uarticle[hashe])
                            except:
                                print(hashe)
                                pass
                    result[i]=li
                return result
            else:
                return {}
        else:
            return {}

def browser(source):
    try:
        articles_per_source = db.child("sources").get(user['idToken']).val()
        Uarticle = db.child("article").get(user['idToken']).val()
    except:
        refresh(user)
        generate_feed(username)
    li=[]
    if source!=None:
        if source in articles_per_source.keys():
            lent=len(articles_per_source[source])
            hashes=articles_per_source[source][-min(lent,9):]
            for hashe in hashes:
                try:
                    li.append(Uarticle[hashe])
                except:
                    print(hashe)
    return li


def show_saved(username):
        data={}
        users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
        if(len(users.each())):#check if entry exists
       	    lis=users.val()
            sender_id=str(lis[username])
            users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
            if(len(users.each())):
                lis=users.val()[sender_id]
                if 'pin' in lis:
                    lis=lis['pin']
                    print(lis)
                else:
                    return []
                try:
                    articles_per_source = db.child("sources").get(user['idToken']).val()
                    Uarticle = db.child("article").get(user['idToken']).val()
                except:
                    refresh(user)
                    generate_feed(username)
                li=[]
                print("++"*20)
                print(lis)
                for hashe in lis:
                    print("====",hashe)
                    if hashe!=None:
                            li.append(Uarticle[hashe])
                    result=li
                    print(li)
                return result
            else:
                return []
        else:
            return []

def extra(username):
    #print("hello")
    users=db.child("id").order_by_key().equal_to(username).get(user['idToken'])
    if(len(users.each())):#check if entry exists
        lis=users.val()
        sender_id=str(lis[username])
    users=db.child("users").order_by_key().equal_to(sender_id).get(user['idToken'])
    if(len(users.each())):#check if entry exists
        lis=users.val()[sender_id]['sub']
        #print(lis)
        return lis

def addUser(sender_id,value):
    try:
        data = {sender_id:value}
        db.child("id").child(value).set(sender_id,user['idToken'])
    except:
        refresh(user)
        addUser(sender_id,value)

if __name__ == "__main__":
    print(subscribe_model(input()))
