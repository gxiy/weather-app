import PySimpleGUI as sg
import requests
import pygal
import os
import json
import datetime

"""
all weather data obtained from Open Weather Map API
https://openweathermap.org/current#current_JSON
"""

def get_citycode(alpha2codes, citylist, values):
	country_name = values[0]
	city_name = values[1].title()
	
	#Find alpha 2 code for chosen country
	country_dict = list(filter(lambda y: y['name'] == country_name, \
	alpha2codes))[0]
	alpha2 = country_dict['alpha-2']

	#Find city code 
	city_dict = list(filter(lambda y: y['name'].title() == city_name and \
	y['country'] == alpha2, citylist))[0] #hopefully only one entry :?
	city_code = city_dict['id']
	return city_name, city_code

def get_weather_data(api_key, city_code):
	#Get current weather data from api
	weather_url = 'https://api.openweathermap.org/data/2.5/weather?id=%s&appid=%s'\
	%(str(city_code), api_key)
	weather = requests.get(weather_url)
	weather_dat = weather.json()

	#kelvin to celsius (in case it's useful)
	k2c = lambda k: k-273

	#kelvin to fahrenheit 
	k2f = lambda k: (9/5)*(k-273)+32
	
	#Get current temperature and weather description
	temp = round(k2f(weather_dat['main']['temp'])) #in fahrenheit
	status = weather_dat['weather'][0]['description'] #ex. Scattered Clouds
	return temp, status

def weather_graph(api_key, city_name, city_code):
	#Create hourly weather graph
	hourly_url = 'https://api.openweathermap.org/data/2.5/forecast/hourly?id=%s&appid=%s'\
	%(str(city_code), api_key)
	hourly = requests.get(hourly_url)
	hourly_data = hourly.json()
	hourly_time, hourly_weather = [], []

	start_date = hourly_data['list'][0]['dt_txt']
	start_date = start_date[:10]

	#Api starts at hour 0, need to find current time
	now = datetime.datetime.now()
	current_hour = str(now)[11:13] #ex. 09, 15, etc.
	start_hour = int(current_hour)
	time = start_hour #?? so it is in current time or no?
	
	#kelvin to fahrenheit 
	k2f = lambda k: (9/5)*(k-273)+32
	
	#Make graph for time period of 12 hours
	for hour in hourly_data['list'][:13]:
		time +=1
		#or +int(hour['dt_txt'][11:13]) #ex. 09
		if time >= 24:
			time -= 24
		hourly_time.append('%s:00' %(time))
		condition_dict = {'value': k2f(hour['main']['temp']), 
		'label': hour['weather'][0]['description']} #change temp to str as needed
		hourly_weather.append(condition_dict)
	
	#Get current weather for graph title
	tempf, description = get_weather_data(api_key, city_code)
	
	#Creates graph of hourly temperatures using PYGAL!
	my_config = pygal.Config()
	my_config.fill = False
	my_config.show_legend = False
	my_config.stroke_style = {'width': 5}
	my_config.dots_size = 5
	temp_graph = pygal.Line(my_config)
	temp_graph.title = '%s Hourly Forecast \n \
	Currently %s F with %s' %(city_name, tempf, description)
	temp_graph.x_labels = hourly_time
	temp_graph.y_title = 'Temperature (F)'
	temp_graph.x_title = 'Hour'
	temp_graph.add('', hourly_weather)
	temp_graph.render_to_file('hourly_temp.svg') 

	#open file automatically 
	os.startfile(r'hourly_temp.svg', 'open')

def main():
	#Prepare country/city identification data from json files
	with open('alpha2_codes.json') as f:
		alpha2_codes = json.load(f)
	with open('city_list.json', errors = 'ignore') as f:
		city_list = json.load(f)

	#List out all possible countries and allow user to choose
	country_list = []
	for country in alpha2_codes:
		country_list.append(country['name'])
		
	#Make US default choice
	country_list.remove('United States of America')
	country_list.insert(0, 'United States of America')

	#--- Begin GUI ----
	
	#Define window
	sg.ChangeLookAndFeel('TealMono')

	layout1 = [
			[sg.Text('How\'s the weather looking today?')],
			[sg.Text('Country:'), sg.InputCombo(country_list)],
			[sg.Text('City:      '), sg.InputText()],
			[sg.Submit()]
			]
	window = sg.Window('WeatherBot').Layout(layout1)
	
	while True:
		event, values = window.Read()
		if event is None or event == 'Exit':
			break
		
		if event == 'Submit':
			try:
				city_name, city_code = get_citycode(alpha2_codes, city_list, values)
				apikey = 'd980e5931a57f7cc0b7f894467ce72a2'
				weather_graph(apikey, city_name, city_code)
			except IndexError:
				sg.Popup('Sorry, that\'s not a valid city name!',
				auto_close = True)

if __name__ == '__main__':
	main()

