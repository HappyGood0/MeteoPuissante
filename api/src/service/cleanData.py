import pandas as pd
import numpy as np

def clean_data(data):
	data.loc[data['is_last_lightning_cloud_ground'] != True, ['is_last_lightning_cloud_ground']] = False

	data['lightning_id'] = pd.to_numeric(data['lightning_id'])#, errors='coerce')
	data['date'] = pd.to_datetime(data['date']).dt.tz_localize(None)

	alerte = False
	alerte_value = None
	for i in range(len(data)):
		if not pd.isna(data.at[i, 'airport_alert_id']) and not data.at[i, 'is_last_lightning_cloud_ground'] and alerte_value != data.at[i, 'airport_alert_id']:
			alerte = True
			alerte_value = data.at[i, 'airport_alert_id']
		if alerte and data.at[i, 'is_last_lightning_cloud_ground']:
			alerte = False
		if alerte:
			data.at[i, 'airport_alert_id'] = alerte_value

def modify_data(data):	
	data.insert(2, 'year', data['date'].dt.year)

	#Le jour actuel dans l'année
	data.insert(3, 'day_of_year', data['date'].dt.dayofyear)

	#La seconde actuelle dans la journée
	data.insert(4, 'second', data['date'].dt.hour * 3600 + data['date'].dt.minute * 60 + data['date'].dt.second)

	#Compte le nombre d'éclair precedent enregistré sur le même orage
	data.insert(0, "nst_of_storm", data.groupby('airport', group_keys=False)[['date', 'lightning_id']]\
							.rolling("1h", on="date", closed = "right", min_periods=1)\
							.count()\
							.reset_index(level=0, drop=True)['lightning_id'])

	#fait la moyenne et variance des amplitudes des eclairs qui appartiennent au même orage (séparé deux à deux de moins d'une heure)
	ampli_rolling = data.groupby('airport', group_keys=False)[['date', 'amplitude']]\
							.rolling("1h", on="date", closed = "right", min_periods=1)
	data.insert(10, "mean_amplitude", ampli_rolling.mean().reset_index(level=0, drop=True)['amplitude'])
	data.insert(11, "var_amplitude", ampli_rolling.var().reset_index(level=0, drop=True)['amplitude'])
	
	data.insert(14, "prop_icloud_of_storm", data.groupby('airport', group_keys=False)[['date', 'icloud']]\
							.rolling("1h", on="date", closed = "right", min_periods=1)\
							.mean()\
							.reset_index(level=0, drop=True)['icloud'])

	second_lighning = data[data["nst_of_storm"] == 2]
	second_lighning["original_index"] = second_lighning.index -1
	#data.insert(16, "dist_derivative", (second_lighning["dist"] - data.loc[second_lighning["original_index"], "dist"]))# / ((data["date"] - data["date"].shift(1)) / pd.Timedelta(seconds=1)))
	
	#Compte le nombre d'éclair precedent enregistré sur la même alerte
	data.insert(18, "nst_of_alert", data.groupby((data['airport_alert_id'] != data['airport_alert_id'].shift())\
										.cumsum())['airport_alert_id']\
      									.cumcount())

	data.drop(['lightning_id', 'lightning_airport_id', 'date'], axis=1, inplace=True)
	

def process_data():
	data = pd.read_csv("bdd/segment_alerts_all_airports_train.csv", na_values=['Empty', '', 'NaN', 'nan'])

	print("Start of the clean process...")
	clean_data(data)
	print("End of the clean process\n")
	print("Start of the modifying process...")
	modify_data(data)
	print("End of the modifying process\n")

	print("Saving change...")
	data.to_csv("bdd/segment_alerts_all_airports_train_clean.csv", index=False)
	print("Clean data are now in 'bdd/segment_alerts_all_airports_train_clean.csv'")

process_data()