import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt


file_path = 'AAOS.csv'


df = pd.read_csv(file_path, encoding='cp949')

# data.iloc[:, 2:] = data.iloc[:, 2:].apply(lambda col: col.fillna(col.mean()))
# data = data['1.5M ��� ���(��C)']
# data['�Ͻ�'] = pd.to_datetime(data['�Ͻ�'])


# data.set_index('�Ͻ�', inplace=True)

# features = ['1.5M ��� ���(��C)']
# df = data['1.5M ��� ���(��C)']

df.iloc[:, 12:] = df.iloc[:, 12:].apply(lambda col: col.fillna(col.mean()))
df.iloc[:, 3:] = df.iloc[:, 3:].apply(lambda col: col.fillna(col.mean()))

# '�Ͻ�' ���� Datetime �������� ��ȯ
df['�Ͻ�'] = pd.to_datetime(df['�Ͻ�'])

# '�Ͻ�' ���� �ε����� ����
df.set_index('�Ͻ�', inplace=True)

# �ʿ��� Ư�� ����
features = ['1.5M ��� ���(��C)','1.5M ��� ����(%)']
df = df[features]


# ������ �����ϸ� (0�� 1 ���̷� ����ȭ)
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df)

# �ð迭 �����͸� �н� �����ͷ� ��ȯ
X, y = [], []

# ���� �Ⱓ ���� (��: ������ 30���� ���� ���� ���� ����)
lookback = 30

for i in range(len(df_scaled) - lookback):
    X.append(df_scaled[i:(i + lookback)])
    y.append(df_scaled[i + lookback])

X, y = np.array(X), np.array(y)

# �н� �����Ϳ� �׽�Ʈ �����ͷ� �и�
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# LSTM �� ����
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dense(2))  # ��� ��� ���� Ư���� ���� �����ϰ� ����
model.compile(optimizer='adam', loss='mse')

# �� �н�
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1)

# Training �� Validation Loss �׷����� �ð�ȭ
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()

# �׽�Ʈ �����͸� ����Ͽ� ����
y_pred = model.predict(X_test)


# ���� ��� �ð�ȭ
plt.plot(df.index[-len(y_test):], scaler.inverse_transform(y_test), label='True Values')
plt.plot(df.index[-len(y_test):], scaler.inverse_transform(y_pred), label='Predicted Values')
plt.xticks(rotation=45)
plt.legend()
plt.show()

# Predict test data�� ������ 7�� ������ ���
last_7_days = df_scaled[-lookback:]
last_7_days = last_7_days.reshape((1, lookback, len(features)))
next_day_prediction = model.predict(last_7_days)
next_day_prediction = scaler.inverse_transform(next_day_prediction)
predicted_temp = next_day_prediction[0, 0]
predicted_humi = next_day_prediction[0, 1]
print("Predicted Weather for the next 7 days:")
print("Predicted Temperature : ", predicted_temp)
print("Predicted Humidity : ", predicted_humi)

# # Calculate RMSE
# rmse = np.sqrt(mean_squared_error(scaler.inverse_transform(y_test), scaler.inverse_transform(y_pred)))
# print(f'Root Mean Squared Error (RMSE): {rmse}')


# # Calculate R squared
# r2 = r2_score(scaler.inverse_transform(y_test), scaler.inverse_transform(y_pred))
# print(f'R Squared (R^2): {r2}')

for i in range(len(features)):
    # Calculate RMSE for each feature
    rmse = np.sqrt(mean_squared_error(scaler.inverse_transform(y_test)[:, i], scaler.inverse_transform(y_pred)[:, i]))
    print(f'Root Mean Squared Error (RMSE) for {features[i]}: {rmse}')

    # Calculate R squared for each feature
    r2 = r2_score(scaler.inverse_transform(y_test)[:, i], scaler.inverse_transform(y_pred)[:, i])
    print(f'R Squared (R^2) for {features[i]}: {r2}')
    
    # predicted_temp = 25
# predicted_humi = 30

def detect_plant_disease(predicted_temp, predicted_humi):
    if predicted_temp >= 20:
        if predicted_temp >= 25 and predicted_temp <= 30 and predicted_humi >= 80 and predicted_humi <= 90:
            return "�ٸ������� �ؽ��մϴ�. �����ϼ���"
        elif predicted_temp >= 20 and predicted_temp < 25 and predicted_humi >= 90:
            return "�ٰ����̺��� �����ϼ���"
        elif predicted_temp >= 25 and predicted_temp <= 28 and predicted_humi <= 55:
            return "�򰡷纴�� �����ϼ���"
        else:
            return "�ǰ��� ����"
    else:
        return "�ǰ��� ����"
    
disease_detect_result = detect_plant_disease(predicted_temp, predicted_humi)
print(disease_detect_result)