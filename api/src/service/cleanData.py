import pandas as pd

def clean_data():
	data = pd.read_csv("bdd/segment_alerts_all_airports_train.csv", na_values=['Empty', '', 'NaN', 'nan'])

	data.loc[data['is_last_lightning_cloud_ground'] != True, ['is_last_lightning_cloud_ground']] = False

	data['lightning_id'] = pd.to_numeric(data['lightning_id'], errors='coerce')

	new_value = None
	new_value_range = 0
	for i in range(len(data)):
		if i % 1000 == 0 :
			print(i, new_value, new_value_range)
		if pd.isna(data.at[i, 'airport_alert_id']):
			if new_value_range < i or new_value is None:
				values = data[(data['lightning_id'] > data.at[i, 'lightning_id']) & data['airport_alert_id'].notnull()]
				if not values.empty:
					new_value = values['airport_alert_id'].iloc[0]
					new_value_range = values['lightning_id'].iloc[0]
				else:
					print(i, values)
			data.at[i, 'airport_alert_id'] = new_value

	data.to_csv("bdd/segment_alerts_all_airports_train_clean.csv", index=False)

clean_data()