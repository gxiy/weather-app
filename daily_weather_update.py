import requests
import pygal
import os

"""
all weather data obtained from http://www.wunderground.com/weather/api/
forecast: http://api.wunderground.com/api/e1a67220464f7891/forecast/q/GA/Watkinsville.json
hourly: http://api.wunderground.com/api/e1a67220464f7891/hourly/q/GA/Watkinsville.json
"""
state = input('US State Name (abbreviation): ')
town = input('Town/City Name: ').replace(' ', '_')

#Executes API call to return response object
forecast_url = 'http://api.wunderground.com/api/e1a67220464f7891/forecast/q/%s/%s.json' %(state, town)
hourly_url = 'http://api.wunderground.com/api/e1a67220464f7891/hourly/q/%s/%s.json' %(state, town)
forecasts = requests.get(forecast_url)
hourly = requests.get(hourly_url)

#Converts json files into python-usable dictionaries
forecast_data = forecasts.json()
hourly_data = hourly.json()

#Display weather forecast for current day and next day
forecast_txt = forecast_data['forecast']['txt_forecast']['forecastday']
day, night, next_day = forecast_txt[0], forecast_txt[1], forecast_txt[2]
print('%s forecast' %day['title'])
print('Today: %s' %(day['fcttext']))
print('Tonight: %s' %(night['fcttext']))
print('Tomorrow: %s' %(next_day['fcttext']))

#Obtains hourly temperature data for current day
hour_list, condition_dicts = [], []
hourly_forecast = hourly_data['hourly_forecast']
date_data = hourly_forecast[0]['FCTTIME']
date_string = '%s %s, %s' %(date_data['mon_abbrev'], \
 date_data['mday'], date_data['year'])

#finds index at which the day ends
stop_index = 7
for hour in hourly_forecast:
	if hour['FCTTIME']['hour'] == '0':
		stop_index = hourly_forecast.index(hour)
		break

#adds hour and temperature values into list
for hour in hourly_forecast[:stop_index+1]:
	hour_list.append(hour['FCTTIME']['civil'])
	condition_dict = {'value': int(float(hour['temp']['english'])),
					  'label': hour['condition']} 
	condition_dicts.append(condition_dict)

#Creates graph of hourly temperatures using PYGAL!
my_config = pygal.Config()
my_config.fill = False
my_config.show_legend = False
my_config.stroke_style = {'width': 5}
my_config.dots_size = 5
temp_graph = pygal.Line(my_config)
temp_graph.title = 'Hourly Forecast for %s, %s: %s' %(town, state, date_string)
temp_graph.x_labels = hour_list
temp_graph.y_title = 'Temperature (F)'
temp_graph.add('', condition_dicts)
temp_graph.render_to_file('hourly_temp.svg')

#open file automatically 
os.startfile(r'hourly_temp.svg', 'open')
