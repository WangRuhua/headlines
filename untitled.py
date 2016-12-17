import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib2
import urllib

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640',
             'mitbbs': 'http://www.mitbbs.com/board_rss/EB23.xml',
             'slickdeals': 'http://slickdeals.net/newsearch.php?mode=popdeals&searcharea=deals&searchin=first&rss=1'}


DEFAULTS = {'publication':'bbc',
            'city': 'London,UK',
            'currency_from':'USD',
            'currency_to':'CNY'}


@app.route("/", methods=['GET','POST'])
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication.lower())
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

# get customized currency based on user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']

    currency_to = request.args.get("currency_to")
    print currency_to
    if not currency_to:
        currency_to = DEFAULTS['currency_to']

    rate = get_rate(currency_from, currency_to)
    return render_template("home.html", articles=articles,weather=weather,
                           currency_from=currency_from, currency_to=currency_to, rate=rate)

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']
WEATHER_URL= "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=bf6d8af5429c9fb993b181feaef2647f"
CURRENCY_URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20(%22{}%22)&format=json&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='
def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        #weather = {'description':parsed['weather'][0]['description'],'temperature':parsed['main']['temp'],'city':parsed['name']}
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']
                   }
    return weather


def get_rate(frm, to):
    url=CURRENCY_URL.format(frm+to)

    all_currency = urllib2.urlopen(url).read()

    Rate = json.loads(all_currency).get('query').get('results').get('rate').get('Rate')

    #frm_rate = parsed.get(frm.upper())
    #to_rate = parsed.get(to.upper())
    return Rate



if __name__ == "__main__" :
    app.run(port=5000, debug=True)