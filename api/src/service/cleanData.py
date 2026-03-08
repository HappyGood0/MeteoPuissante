import pandas as pd

def clean_data():
	data = pd.read_csv("bdd/segment_alerts_all_airports_train.csv", na_values=['Empty', '', 'NaN', 'nan'])

	data.loc[data['is_last_lightning_cloud_ground'] != True, ['is_last_lightning_cloud_ground']] = False

	data['lightning_id'] = pd.to_numeric(data['lightning_id'])#, errors='coerce')
	data['date'] = pd.to_datetime(data['date'])

	alerte = False
	alerte_value = None
	old_alerte_value = None
	for i in range(len(data)):
		if not pd.isna(data.at[i, 'airport_alert_id']) and not data.at[i, 'is_last_lightning_cloud_ground'] and alerte_value != data.at[i, 'airport_alert_id']:
			alerte = True
			old_alerte_value = alerte_value
			alerte_value = data.at[i, 'airport_alert_id']
		if alerte and data.at[i, 'is_last_lightning_cloud_ground']:
			alerte = False
		if alerte:
			data.at[i, 'airport_alert_id'] = alerte_value

	data.to_csv("bdd/segment_alerts_all_airports_train_clean.csv", index=False)

clean_data()