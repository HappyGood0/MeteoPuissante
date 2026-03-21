import pandas as pd
from tqdm import trange

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

def modify_data(data):
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




	#Compte le nombre d'éclair precedent enregistré sur la même alerte
	data.insert(21, "nst_of_alert", data.groupby((data['airport_alert_id'] != data['airport_alert_id'].shift())\
										.cumsum())['airport_alert_id']\
	  									.cumcount())

	rep = {}
	for airport in data["airport"].unique():
		rep[str(airport)] = data[data["airport"] == airport].drop(['airport', 'lightning_id', 'lightning_airport_id', 'date', 'lat', 'lon', 'total_second', 'date_barycentre', 'dist_barycentre_diff', 'date_barycentre_diff', 'azimuth_barycentre_diff'], axis=1)

	return rep
	

def process_data():
	data = pd.read_csv("bdd/segment_alerts_all_airports_train.csv", na_values=['Empty', '', 'NaN', 'nan'])

	print("Start of the clean process...")
	clean_data(data)
	print("End of the clean process\n")
	print("Start of the modifying process...")
	dico = modify_data(data)
	print("End of the modifying process\n")

	print("Saving change...")
	for airport in dico:
		dico.get(airport).to_csv("bdd/segment_alerts_"+airport+"_train_clean.csv", index=False)
		print("Clean data are now in 'bdd/segment_alerts_"+airport+"_train_clean.csv'")

process_data()