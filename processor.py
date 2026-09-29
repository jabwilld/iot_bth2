"""
processor.py - Read raw data from InfluxDB, preprocess and save to processed bucket
"""
import os
import warnings
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)
load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "ptit_iot")
INFLUX_BUCKET_RAW = os.getenv("INFLUXDB_BUCKET_RAW", "sensor_raw")
INFLUX_BUCKET_PROCESSED = os.getenv("INFLUXDB_BUCKET_PROCESSED", "sensor_processed")

def remove_outliers_iqr(df, col):
    if col not in df.columns or df[col].dropna().empty:
        return df
    
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
    num_outliers = int(outlier_mask.sum())
    if num_outliers > 0:
        print(f"[PROCESSOR] Detected {num_outliers} outliers in column '{col}'. Setting NaN.", flush=True)
        df.loc[outlier_mask, col] = np.nan
    return df

def run_preprocessing():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] === START PREPROCESSING ===", flush=True)
    
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    query = f'''
    from(bucket: "{INFLUX_BUCKET_RAW}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "environment_raw")
      |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    
    try:
        raw_res = query_api.query_data_frame(query)
        if raw_res is None or (isinstance(raw_res, list) and len(raw_res) == 0):
            print("[PROCESSOR] No raw data found in InfluxDB.", flush=True)
            return

        if isinstance(raw_res, list):
            df_list = [t for t in raw_res if isinstance(t, pd.DataFrame) and not t.empty]
            if len(df_list) == 0:
                print("[PROCESSOR] No non-empty tables returned.", flush=True)
                return
            df = pd.concat(df_list, ignore_index=True)
        else:
            df = raw_res

        if df.empty:
            print("[PROCESSOR] Raw DataFrame is empty.", flush=True)
            return

        print(f"[PROCESSOR] Read {len(df)} raw records from bucket '{INFLUX_BUCKET_RAW}'.", flush=True)

        df['_time'] = pd.to_datetime(df['_time'])
        df = df.set_index('_time').sort_index()

        cols = ['temperature', 'humidity', 'light']
        for col in cols:
            if col not in df.columns:
                df[col] = np.nan

        # 1. Outliers (IQR)
        for col in cols:
            df = remove_outliers_iqr(df, col)

        # 2. Missing Values (Interpolation)
        df[cols] = df[cols].interpolate(method='time').bfill().ffill()

        # 3. Resampling 10s
        df_resampled = df[cols].resample('10s').mean().interpolate(method='linear')

        # 4. Feature Engineering (Rolling Mean & Delta)
        for col in cols:
            df_resampled[f'{col}_rolling_mean'] = df_resampled[col].rolling(window=3, min_periods=1).mean()
            df_resampled[f'{col}_delta'] = df_resampled[col].diff().fillna(0.0)

        # 5. MinMaxScaler [0, 1]
        scaler = MinMaxScaler()
        scaled_cols = [f'{col}_scaled' for col in cols]
        df_resampled[scaled_cols] = scaler.fit_transform(df_resampled[cols])

        # 6. Write to sensor_processed bucket
        points = []
        for timestamp, row in df_resampled.iterrows():
            p = Point("environment_processed").time(timestamp, WritePrecision.NS)
            p = p.tag("device_id", "esp32_sensor_01")
            for c in df_resampled.columns:
                if not pd.isna(row[c]):
                    p = p.field(c, float(row[c]))
            points.append(p)

        write_api.write(bucket=INFLUX_BUCKET_PROCESSED, record=points)
        print(f"[PROCESSOR] Success! Written {len(points)} processed records to bucket '{INFLUX_BUCKET_PROCESSED}'.", flush=True)

    except Exception as e:
        print(f"[PROCESSOR ERROR] {e}", flush=True)
    finally:
        client.close()

if __name__ == "__main__":
    run_preprocessing()
