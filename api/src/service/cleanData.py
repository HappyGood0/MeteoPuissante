import pandas as pd
import numpy as np
from tqdm import trange
import requests
import time
from io import StringIO

station_meteo_fr_id = {
	"Ajaccio": 20004002,
	"Bastia": 20148001,
	"Biarritz": 64024001,
	"Nantes": 44020001,
}

token = "" # token meteo france

def barycentre(df, time_col, col, time_window, max_rows):
	results = []

	for j in trange(0, len(df), 2500, desc="Calc the barycentre of " + col):
		for i in range(j, min(j+2500, len(df))):
			current_time = df.iloc[i][time_col]

			window_start = current_time - pd.Timedelta(time_window)

			row_start = max(0, i - max_rows + 1)
			window = df.iloc[row_start:i + 1]

			window = window[window[time_col] >= window_start]

			results.append(window[col].mean())

	return pd.Series(results, index=df.index)


def clean_data(data):
	data.loc[data['is_last_lightning_cloud_ground'] != True, ['is_last_lightning_cloud_ground']] = False

	data['lightning_id'] = pd.to_numeric(data['lightning_id'])
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



def fetch_commande_id(bearer_token, station_id, start_date, end_date):
	url = f"https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/horaire?id-station={station_id}&date-deb-periode={start_date}T00:00:00Z&date-fin-periode={end_date}T00:00:00Z"
	headers = {
		"accept": "*/*",
		"Authorization": f"Bearer {bearer_token}"
	}
	print(url)
	response = requests.get(url, headers=headers)
	if response.status_code >= 200 and response.status_code < 300:
		json_response = response.json()
		commande_id = json_response["elaboreProduitAvecDemandeResponse"]["return"]
		print(f"====================== {commande_id} ==========================")
		return commande_id
	else:
		raise Exception(f"Erreur lors de la requête : {response.status_code} - {response.text}")

def fetch_meteo_file(bearer_token, commande_id):
	url = f"https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier?id-cmde={commande_id}"
	headers = {
		"Authorization": f"Bearer {bearer_token}"
	}
	print(url)
	response = requests.get(url, headers=headers)
	if response.status_code >= 200 and response.status_code < 300:
		return response.text  # ou response.json() si la réponse est en JSON
	else:
		raise Exception(f"Erreur lors de la récupération du fichier : {response.status_code} - {response.text}")

def fetch_meteo_data(bearer_token, station_id, start_date, end_date):
	commande_id = fetch_commande_id(bearer_token, station_id, start_date, end_date)

	time.sleep(20)

	csv_content = fetch_meteo_file(bearer_token, commande_id)
	df = pd.read_csv(StringIO(csv_content), sep=";")  # Utilisez le bon séparateur si nécessaire
	return df[["DATE", "PSTAT"]]



def add_meteo_fr_data(data):
	data["date_meteo_fr"] = data['date'].dt.year * 1000000 + data['date'].dt.month * 10000 + data['date'].dt.day * 100 + data['date'].dt.hour

	"""meteo_data = pd.DataFrame()
	for airport in data["airport"].unique():
		if airport in station_meteo_fr_id:
			mmin, mmax = data[data["airport"] == airport]['date'].dt.date.agg(["min", "max"])
			dates = pd.date_range(start=mmin, end=mmax, freq="1Y")
			old_date = mmin

			for date in dates.date:
				meteo_data_tmp = fetch_meteo_data(token, station_meteo_fr_id[airport], old_date, date)
				meteo_data_tmp["name_station"] = airport
				meteo_data = pd.concat([meteo_data, meteo_data_tmp], ignore_index=True)
				old_date = date

			meteo_data_tmp = fetch_meteo_data(token, station_meteo_fr_id[airport], old_date, mmax)
			meteo_data_tmp["name_station"] = airport
			meteo_data = pd.concat([meteo_data, meteo_data_tmp], ignore_index=True)


	meteo_data.to_csv("bdd/meteo_data.csv", index=False)"""
	meteo_data = pd.read_csv("bdd/meteo_data.csv", na_values=['Empty', '', 'NaN', 'nan'])
	meteo_data['PSTAT'] = pd.to_numeric(meteo_data['PSTAT'].astype(str).str.replace(",", ".").replace("nan", np.nan))

	print(meteo_data)
			
	data = data.merge(
		meteo_data,
		left_on=["date_meteo_fr", "airport"],
		right_on=["DATE", "name_station"],
		how="left"
	)
	print(data)
	return data


def modify_data(data, for_training):
	#data = data[data["airport"] == "Biarritz"]

	max_delta_of_same_storm = "1h"

	data.insert(2, 'year', data['date'].dt.year)

	#Le jour actuel dans l'année
	data.insert(3, 'day_of_year', data['date'].dt.dayofyear)

	#La seconde actuelle dans la journée
	data.insert(4, 'second', data['date'].dt.hour * 3600 + data['date'].dt.minute * 60 + data['date'].dt.second)
	data['total_second'] = (data['date'] - pd.to_datetime("1/1/2000")).dt.total_seconds()

	#Compte le nombre d'éclair precedent enregistré sur le même orage
	data.insert(0, "nst_of_storm", data.groupby('airport', group_keys=False)[['date', 'lightning_id']]\
							.rolling(max_delta_of_same_storm, on="date", closed = "right", min_periods=1)\
							.count()\
							.reset_index(level=0, drop=True)['lightning_id'])

	#fait la moyenne et variance des amplitudes des eclairs qui appartiennent au même orage (séparé deux à deux de moins d'une heure)
	ampli_rolling = data.groupby('airport', group_keys=False)[['date', 'amplitude']]\
							.rolling(max_delta_of_same_storm, on="date", closed = "right", min_periods=1)
	data.insert(10, "mean_amplitude", ampli_rolling.mean().reset_index(level=0, drop=True)['amplitude'])
	data.insert(11, "var_amplitude", ampli_rolling.var().reset_index(level=0, drop=True)['amplitude'])
	
	data.insert(14, "prop_icloud_of_storm", data.groupby('airport', group_keys=False)[['date', 'icloud']]\
							.rolling(max_delta_of_same_storm, on="date", closed = "right", min_periods=1)\
							.mean()\
							.reset_index(level=0, drop=True)['icloud'])
	
	data.insert(16, 'dist_barycentre', barycentre(data, 'date', 'dist', time_window=max_delta_of_same_storm, max_rows=6))
	data['date_barycentre'] = barycentre(data, 'date', 'total_second', time_window=max_delta_of_same_storm, max_rows=6)
	data.insert(18, 'azimuth_barycentre', barycentre(data, 'date', 'azimuth', time_window=max_delta_of_same_storm, max_rows=6))
	
	m = 3
	data['dist_barycentre_diff'] = (
		data.groupby('airport', group_keys=False)['dist_barycentre']
		.diff()
		.where(data['nst_of_storm'] > m, pd.NA)
	)
	data['date_barycentre_diff'] = (
		data.groupby('airport', group_keys=False)['date_barycentre']
		.diff()
		.where(data['nst_of_storm'] > m, pd.NA)
	)
	data['azimuth_barycentre_diff'] = (
		data.groupby('airport', group_keys=False)['azimuth_barycentre']
		.diff()
		.where(data['nst_of_storm'] > m, pd.NA)
	)
	#Vitesse en coordonnée carthesienne
	data.insert(19, "barycentre_speed", (data["dist_barycentre_diff"] + data["dist_barycentre"] * data["azimuth_barycentre_diff"]) / data["date_barycentre_diff"].clip(lower=1))
	
	data = add_meteo_fr_data(data)


	#Compte le nombre d'éclair precedent enregistré sur la même alerte
	data.insert(21, "nst_of_alert", data.groupby((data['airport_alert_id'] != data['airport_alert_id'].shift())\
										.cumsum())['airport_alert_id']\
	  									.cumcount())



	drop_columns = ['airport', 'lightning_id', 'lightning_airport_id', 'date', 'lat', 'lon', 'total_second', 'date_meteo_fr', 'DATE', "name_station", 'date_barycentre', 'dist_barycentre_diff', 'date_barycentre_diff', 'azimuth_barycentre_diff']
	if for_training:
		drop_columns.pop(0)
	
	data.drop(drop_columns, axis=1)


	column_to_move = "is_last_lightning_cloud_ground"

	# Reorder columns
	data = data.reindex(columns=[col for col in data.columns if col != column_to_move] + [column_to_move])

	return data



def process_data(data, for_training=False):
	print("Start of the clean process...")
	clean_data(data)
	print("End of the clean process\n")
	print("Start of the modifying process...")
	data = modify_data(data, for_training)
	print("End of the modifying process\n")
	return data



def clean_base_data():
	data = pd.read_csv("bdd/segment_alerts_all_airports_train.csv", na_values=['Empty', '', 'NaN', 'nan'])

	data = process_data(data, True)

	for airport in data["airport"].unique():
		data[data["airport"] == airport]\
			.drop(['airport'], axis=1)\
			.to_csv("bdd/segment_alerts_"+str(airport)+"_train_clean.csv", index=False)
		print("Clean data are now in 'bdd/segment_alerts_"+airport+"_train_clean.csv'")
