from datetime import datetime
from flask import render_template
from flask import Flask
from SmartHack import app
import json
import requests
import pyrebase
import collections
import string
import vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas
import numpy
import sklearn
import yfinance as yf
import time
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# acronims
tick = {"Intertek":"ITRK.L",
        "Unilever":"ULVR.L",
        "Scottish-Mortgage-Investment-Trust":"SMT.L",
        "AstraZeneca":"AZN.L",
        "British-American-Tobacco":"BATS.L",
        "Polymetal-International":"POLY.L",
        "LSEG":"LSE.L",
        "RBS":"RBS.L",
        "Morrisons":"MRW.L",
        "Rentokil":"RTO.L"}

# predictions
def train(X, Y):
    regr = LinearRegression()
    regr.fit_transform(X, Y)
    return regr;

def find_closest(elem, list):
    i = 0
    for l in list:
        if elem <= l:
            break
        i = i + 1
    return min(i, len(list) - 1)

prediction = []
yesterday = []
companies = []
company_list = []

# sentiment analyser
sid = SentimentIntensityAnalyzer()

# date secured care nu ar trebui sa apara aici
email = "adela.vais99@gmail.com"
password = "linette"
current_company = "blabla"

# firebase configuration
config = {
  "apiKey": "AIzaSyBLAiP4GJe8ofbx7GcrL-bmwPXH39d5qy8",
  "authDomain": "smarthack-18d58.firebaseapp.com",
  "databaseURL": "https://smarthack-18d58.firebaseio.com",
  "projectId": "smarthack-18d58",
  "storageBucket": "smarthack-18d58.appspot.com",
  "messagingSenderId": "1033245751558",
  "appId": "1:1033245751558:web:8d44bd98138b97e5e28687",
  "measurementId": "G-9V8BVRHZDR"
}

# firebase access
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email, password)
db = firebase.database()
all_articles_in_database = db.child("articles").get()

# number of queries
number_of_selected_companies = 10
number_of_news_for_the_same_company = 10

# url for google news api 
URL = 'https://newsapi.org/v2/everything?q={company}&language=en&from={start_date}&to={end_date}&sortBy=publishedAt&apiKey={apikey}'

# test if an article is already 
def already_in (article_info):
	for article in all_articles_in_database.each():
		current_article_in_database = article.val()
		for key, value in current_article_in_database.items():
			if (value['url'] == article_info['url']):
				return False
	return True

# extracts the news for the given company 
# calls the sentiment check
def add_articles(**params):
	# get news
	response = requests.get(URL.format(**params))
	#print(response.content)
	all_articles_news = json.loads(response.content)['articles']
	for i in range (min(number_of_news_for_the_same_company, len(all_articles_news))):
		articles_info = all_articles_news[i]
		# verify if url is already in database
		# add article
		if (already_in(articles_info)):
			current_company_db = current_company[0:(len(current_company)-1)]
			sentence = articles_info['title'] #+ articles_info['content']
			analysed_sentence = sid.polarity_scores(sentence)
			eps = 0.01
			if (abs(analysed_sentence["pos"] - analysed_sentence["neg"]) <= eps):
				category = "neutral"
			elif (analysed_sentence["pos"] > analysed_sentence["neg"]):
				category = "positive"
			else:
				category = "negative"
			data = {"title": articles_info['title'], 
					"content": articles_info['content'], 
					"url": articles_info['url'], 
					"date": articles_info['publishedAt'], 
					"category": category,
					"sentiments": analysed_sentence}
			results = db.child("articles").child(current_company_db).push(data)

# template for adding users
def update_users():
	data = { "company": "AstraZeneca"}
	user = "tibi"
	results = db.child("accounts").child(user).push(data)
	data = { "company": "LSEG"}
	user = "tibi"
	results = db.child("accounts").child(user).push(data)
	data = { "company": "LSEG"}
	user = "linette"
	results = db.child("accounts").child(user).push(data)
	data = { "company": "Unilever"}
	user = "linette"
	results = db.child("accounts").child(user).push(data)
	data = { "company": "British-American-Tobacco"}
	user = "raluca"
	results = db.child("accounts").child(user).push(data)
	data = { "company": "RBS"}
	user = "raluca"
	results = db.child("accounts").child(user).push(data)

# web app
@app.route('/')
def home1():
    """Renders the home page."""
    return render_template(
        'Home.html',
        title='Home Page'
    )

@app.route('/home', methods = ['GET', 'POST'])
def home():
    """Renders the home page."""
    return render_template(
        'Home.html',
        title='Home Page'
    )

@app.route('/entertainment')
def entertainment():
    """Renders the home page."""
    return render_template(
        'Entertainment.html',
        title='Entertainment'
    )


@app.route('/account')
def account():
    """Renders the contact page."""
    return render_template(
        'Cont.html',
        title='Account'
    )

@app.route('/joc1')
def joc1():
    """Renders the contact page."""
    return render_template(
        'Joc1.html',
        title='Account'
    )

@app.route('/joc2')
def joc2():
    """Renders the contact page."""
    return render_template(
        'Joc2.html',
        title='Account'
    )

@app.route('/joc3')
def joc3():
    """Renders the contact page."""
    return render_template(
        'Joc3.html',
        title='Account'
    )

@app.route('/joc4')
def joc4():
    """Renders the contact page."""
    return render_template(
        'Joc4.html',
        title='Account'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'About.html',
        title='About'
    )

@app.route('/news')
def news():
	title = []
	url = []
	category = []
	for article in all_articles_in_database.each():
		current_article_in_database = article.val()
		for key, value in current_article_in_database.items():
			title.append(value['title'])
			url.append(value['url'])
			category.append(value['category'])
			companies.append(article.key())
			print(article.key())
			break
	category  = [c.upper() for c in category]
	return render_template(
        'News.html',
        title='News',
		url0 = url[0],
		title0 = title[0],
		category0 = category[0],
		prediction0 = prediction[0],
		url1 = url[1],
		title1 = title[1],
		category1 = category[1],
		prediction1 = prediction[1],
		url2 = url[2],
		title2 = title[2],
		category2 = category[2],
		prediction2 = prediction[2],
		url3 = url[3],
		title3 = title[3],
		category3 = category[3],
		prediction3 = prediction[3],
		url4 = url[4],
		title4 = title[4],
		category4 = category[4],
		prediction4 = prediction[4],
		url5 = url[5],
		title5 = title[5],
		category5 = category[5],
		prediction5 = prediction[5],
		url6 = url[6],
		title6 = title[6],
		category6 = category[6],
		prediction6 = prediction[6],
		url7 = url[7],
		title7 = title[7],
		category7 = category[7],
		prediction7 = prediction[7],
		url8 = url[8],
		title8 = title[8],
		category8 = category[8],
		prediction8 = prediction[8],
		url9 = url[9],
		title9 = title[9],
		category9 = category[9],
		prediction9 = prediction[9],
		yesterday0 = yesterday[0],
		yesterday1 = yesterday[1],
		yesterday2 = yesterday[2],
		yesterday3 = yesterday[3],
		yesterday4 = yesterday[4],
		yesterday5 = yesterday[5],
		yesterday6 = yesterday[6],
		yesterday7 = yesterday[7],
		yesterday8 = yesterday[8],
		yesterday9 = yesterday[9],
		company0 = companies[0],
		company1 = companies[1],
		company2 = companies[2],
		company3 = companies[3],
		company4 = companies[4],
		company5 = companies[5],
		company6 = companies[6],
		company7 = companies[7],
		company8 = companies[8],
		company9 = companies[9]
    )

# analyse database for predictions
i = 0
for company in all_articles_in_database.each():
	print(company.key())
	company_list.append(company.key())
	dataY = yf.download(tick[company.key()],'2019-10-01','2019-11-01')
	days = [pandas.to_datetime(d).date() for d in dataY.index]
	i = i + 1
	indices = []
	X_aux = []
	for article in company.val().items():
		day_str = article[1]['date'][0:10]
		day = (datetime.strptime(day_str, '%Y-%m-%d')).date()
		indices.append(find_closest(day, days))
		pos = article[1]['sentiments']['pos']
		neu = article[1]['sentiments']['neu']
		neg = article[1]['sentiments']['neg']
		t = time.mktime(day.timetuple())
		X_aux.append([pos, neu, neg, t])
	Y = numpy.array([dataY.Close[idx] for idx in indices][2:])
	X = numpy.array(X_aux[2:])
	poly = PolynomialFeatures(degree=2)
	X_ = poly.fit_transform(X)
	X_test_ = poly.fit_transform(numpy.array(X_aux[0]).reshape(1, -1))
	lin = LinearRegression()
	lin.fit(X_, Y)
	result = lin.predict(X_test_)
	print(result)
	prediction.append('%.3f'%(result[0]))
	yesterday.append('%.3f'%(dataY.Close[0]))
# selects companies from the locally saved company list
# processes the news requests 
	#add_articles(company=current_company, start_date="2019-10-02", end_date="2019-11-02", apikey="f2b21171f2f0418c92d8209babcbddad")
#update_users()
app.run(debug = True)
