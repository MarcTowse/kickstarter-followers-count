import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import boto3

aws_access_key_id = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
aws_region = st.secrets["aws"]["AWS_REGION"]


dynamodb = boto3.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

def load_data():
    table = dynamodb.Table('kickstarter-followers-catatak')
    records = []
    response = table.scan()
    while True:
        for item in response['Items']:
            try:
                followers = int(item['followers-count'])
                time = datetime.strptime(item['time'], "%Y-%m-%d_%H:%M")
                records.append({"time": time, "followers-count": followers})
            except (ValueError, KeyError) as e:
                print(f"Error processing item: {item} - {e}")
        if 'LastEvaluatedKey' not in response:
            break
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    df = pd.DataFrame.from_records(records).sort_values("time", ascending=True).reset_index(drop=True)
    return df


st.title("Follower Count Dashboard")
df = load_data()

if not df.empty:
    st.sidebar.header("Filter Options")
    time_filter = st.sidebar.selectbox("Select Time Range", ["Last 24 Hours", "Last Week", "Last Month", "All Data"])

    now = datetime.now()
    if time_filter == "Last 24 Hours":
        start_time = now - timedelta(days=1)
    elif time_filter == "Last Week":
        start_time = now - timedelta(weeks=1)
    elif time_filter == "Last Month":
        start_time = now - timedelta(days=30)
    else:
        start_time = df['time'].min()

    filtered_df = df[df['time'] >= start_time]

    st.write(f"Data from {time_filter}:")
    st.dataframe(filtered_df)
    st.write("Followers Over Time")
    fig, ax = plt.subplots()
    ax.plot(filtered_df['time'], filtered_df['followers-count'], marker='o')
    ax.set_xlabel("Time")
    ax.set_ylabel("Followers Count")
    ax.set_title("Followers Count Over Time")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("No data available.")
