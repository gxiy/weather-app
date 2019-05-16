import requests
import pygal
import os
import json
import datetime

"""
all weather data obtained from Open Weather Map API

use this: https://openweathermap.org/current#current_JSON
"""

#Find alpha 2 code for country
country_name = input('Country Name: ').title() #title() makes sure capitalization is the same
with open('alpha2_codes.json') as f:
	alpha2_codes = json.load(f)
country_dict = list(filter(lambda y: y['name'].title() == country_name, \
alpha2_codes))[0]
alpha2 = country_dict['alpha-2']

#Find city code 
city_name = input('City Name: ').title()
with open('city_list.json', errors = 'ignore') as f:
	city_list = json.load(f)
city_dict = list(filter(lambda y: y['name'].title() == city_name and \
y['country'] == alpha2, city_list))[0] #hopefully only one entry :?
city_code = city_dict['id']

#Find current weather conditions
apikey = 'd980e5931a57f7cc0b7f894467ce72a2'
weather_url = 'https://api.openweathermap.org/data/2.5/weather?id=%s&appid=%s'\
%(str(city_code), apikey)
weather = requests.get(weather_url)
weather_dat = weather.json()

#kelvin to celsius (in case it's useful)
k2c = lambda k: k-273

#kelvin to fahrenheit 
k2f = lambda k: (9/5)*(k-273)+32

temp = round(k2f(weather_dat['main']['temp'])) #in fahrenheit
status = weather_dat['weather'][0]['description'] #ex. Scattered Clouds
print('Current weather: %s F with %s' %(temp, status))

#Create hourly weather graph
hourly_url = 'https://api.openweathermap.org/data/2.5/forecast/hourly?id=%s&appid=%s'\
%(str(city_code), apikey)
hourly = requests.get(hourly_url)
hourly_data = hourly.json()
hourly_time, hourly_weather = [], []

start_date = hourly_data['list'][0]['dt_txt']
start_date = start_date[:10]

#Api starts at hour 0, need to find current time
now = datetime.datetime.now()
current_hour = str(now)[11:13] #ex. 09, 15, etc.
start_hour = int(current_hour)

#Make graph for time period of 12 hours
for hour in hourly_data['list'][:13]:
	time = start_hour + int(hour['dt_txt'][11:13]) #ex. 09
	if time >= 24:
		time -= 24
	hourly_time.append('%s:00' %(time))
	condition_dict = {'value': k2f(hour['main']['temp']), 
	'label': hour['weather'][0]['description']} #change temp to str as needed
	hourly_weather.append(condition_dict)

#Creates graph of hourly temperatures using PYGAL!
my_config = pygal.Config()
my_config.fill = False
my_config.show_legend = False
my_config.stroke_style = {'width': 5}
my_config.dots_size = 5
temp_graph = pygal.Line(my_config)
temp_graph.title = '%s Hourly Forecast' %(city_name)
temp_graph.x_labels = hourly_time
temp_graph.y_title = 'Temperature (F)'
temp_graph.x_title = 'Hour'
temp_graph.add('', hourly_weather)
temp_graph.render_to_file('hourly_temp.svg')

#open file automatically 
os.startfile(r'hourly_temp.svg', 'open')
