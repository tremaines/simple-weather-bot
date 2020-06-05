#!/usr/bin/env python3

import tweepy, pyowm, time, schedule
from datetime import datetime
 
# Twitter API keys
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''
# Open weather API key
weather_key = ''

# Set up API access for tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
# Set up API access for pyowm
owm = pyowm.OWM(weather_key)


city = 'Brisbane,AU'
# Sunrise/set variables will be updated dyanmically by get_sun_time() function
sunrise = '06:25'
sunset = '17:05'

degrees = u'\N{DEGREE SIGN}'
# Emojis for sunrise/set
sunrise_emoji = u'\N{SUNRISE OVER MOUNTAINS}'
sunset_emoji = u'\N{SUNSET OVER BUILDINGS}'
# Emojis for weather
few_clouds = u'\N{WHITE SUN WITH SMALL CLOUD}'
scattered_clouds = u'\N{WHITE SUN BEHIND CLOUD}'
overcast_clouds = u'\N{CLOUD}'
rain = u'\N{CLOUD WITH RAIN}'
thunderstorm = u'\N{THUNDER CLOUD AND RAIN}'
# Emojis for temp
hot_face = u'\N{OVERHEATED FACE}'
cold_face = u'\N{FREEZING FACE}'
cool_face = u'\N{SMILING FACE WITH SUNGLASSES}'

# Retrieve weather info and tweet
def tweet_weather():
    observation = owm.weather_at_place(city)
    weather = observation.get_weather()
    weather_emoji = ''
    temp_emoji = ''
    # Get weather components
    temperature = weather.get_temperature(unit = 'celsius')
    current_temp = temperature['temp']
    if current_temp > 30.0:
        temp_emoji = hot_face
    elif current_temp < 15.0:
        temp_emoji = cold_face
    else:
        temp_emoji = cool_face
    humidity = str(weather.get_humidity())
    short_status = weather.get_status()
    weather_status = weather.get_detailed_status()
    if weather_status == 'few clouds':
        weather_emoji = few_clouds
    elif weather_status == 'scattered clouds':
        weather_emoji = scattered_clouds
    elif short_status == 'Clouds':
        weather_emoji = overcast_clouds
    elif short_status == 'Rain':
        weather_emoji = rain
    elif short_status == 'Thunderstorm':
        weather_emoji = thunderstorm
    # Need to ensure tweet is uniqe otherwise it won't post
    # Append date and time of tweet to do this
    tweet_time = datetime.now().strftime('%d/%m/%y %H:%M')
    # Formulate tweet
    tweet = 'Weather: ' + ' ' + weather_emoji + ' ' + weather_status + ' ' + weather_emoji + \
            '. Temperature: ' + str(current_temp) + \
            degrees +'C' + ' ' + temp_emoji + '. Humidity: ' + humidity + '%. (' + tweet_time + ')'
    # Print tweet to bash just because    
    print(tweet)
    # Send out tweet
    api.update_status(status=tweet)

# Clear old sunrise/set times
def clear_sun_times():
    schedule.clear('sunrise')
    schedule.clear('sunset')
    print('Yesterday\'s sunrise and sunset times cleared')

# Retrieve new sunrise/set times and update variables
def get_sun_time():
    global sunrise
    global sunset
    observation = owm.weather_at_place(city)
    weather = observation.get_weather()
    
    sunrise_time = weather.get_sunrise_time()
    bne_sunrise = datetime.fromtimestamp(sunrise_time).strftime('%H:%M')
    sunrise = bne_sunrise
    print('New sunrise time retrieved')

    sunset_time = weather.get_sunset_time()
    bne_sunset = datetime.fromtimestamp(sunset_time).strftime('%H:%M')
    sunset = bne_sunset
    print('New sunset time retrieved')

# Formulate tweet for sunrise/set and post
def tweet_sunriseset(time):
    tweet_time = datetime.now().strftime('%d/%m/%y %H:%M')
    if time == 'rise':
        tweet = sunrise_emoji + ' Good morning! The sun has just risen! ' + sunrise_emoji + '(' + tweet_time + ')'
    elif time == 'set':
        tweet = sunset_emoji + ' Good evening! The sun has just set! ' + sunset_emoji + '(' + tweet_time + ')'
    # Print tweet to bash just because    
    print(tweet)
    # Send out tweet
    api.update_status(status=tweet)

# Update sunrise/set scheduler
def update_sun_times():
    schedule.every().day.at(sunrise).do(tweet_sunriseset, 'rise').tag('sunrise')
    schedule.every().day.at(sunset).do(tweet_sunriseset, 'set').tag('sunset')

# Schedule when to tweet weather
schedule.every(2).hours.at(":00").do(tweet_weather)
# Clear old sunrise/sunset times
schedule.every().day.at("00:05").do(clear_sun_times)
# Get new sunrise/set times
schedule.every().day.at("00:10").do(get_sun_time)
# Update and schedule times
schedule.every().day.at("00:15").do(update_sun_times)

while True:
        schedule.run_pending()
        time.sleep(1)