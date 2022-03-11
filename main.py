import requests
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

AV_API_KEY = "ALPHAVANTAGE_API_KEY"
AV_API_END_POINT = "https://www.alphavantage.co/query"

NEWS_API_KEY = "NEWSAPI_API_KEY"
NEWS_END_POINT = "https://newsapi.org/v2/everything"

TWILIO_ACC_SID = "TWILIO_ACCOUNT_ID"
TWILIO_AUTH_TOKEN = "TWILIO_AUTH TOKEN"

today_datetime = dt.datetime.now()

av_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": AV_API_KEY,
}

news_parameters = {
    "q": COMPANY_NAME,
    "from": today_datetime.date(),
    "sortBy": "publishedAt",
    "apiKey": NEWS_API_KEY,
    "language": "en",
    "excludeDomains": "elespanol.com",
}


def get_percentage_diff():
    av_data = requests.get(AV_API_END_POINT, params=av_parameters)
    av_data.raise_for_status()
    av_data_json = av_data.json()

    yesterday_datetime = today_datetime - dt.timedelta(days=1)
    before_yesterday_datetime = today_datetime - dt.timedelta(days=2)
    yesterday_date_str = str(yesterday_datetime.date())
    before_yesterday_date_str = str(before_yesterday_datetime.date())

    yesterday_close = av_data_json['Time Series (Daily)'][yesterday_date_str]['4. close']
    before_yesterday_close = av_data_json['Time Series (Daily)'][before_yesterday_date_str]['4. close']

    percentage = (float(yesterday_close) - float(before_yesterday_close)) / float(before_yesterday_close) * 100

    return round(percentage, 2)


def get_news():
    """Returns dictionary of first 3 articles"""
    news_data = requests.get(NEWS_END_POINT, params=news_parameters)
    news_data.raise_for_status()
    news_data_json = news_data.json()
    first_3 = news_data_json["articles"][:3]

    return first_3


def send_news_sms(news, percentage):
    arrow = ""
    if percentage > 0:
        arrow = "🔺"
    elif percentage == 0:
        arrow = ""
    else:
        arrow = "🔻"

    for article in news:
        client = Client(TWILIO_ACC_SID, TWILIO_AUTH_TOKEN)
        message = client.messages \
            .create(
                body=f"{STOCK} {arrow}{percentage}%\n{article['title']}\n\n{article['description']}",
                from_="FROM_PHONE_NUMBER",
                to="TO_PHONE_NUMBER"
            )
        print(message.status)


percentage_diff = get_percentage_diff()
print(percentage_diff)
if percentage_diff >= 5 or percentage_diff <= -5:
    send_news_sms(get_news(), percentage_diff)













# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

# STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
