# Smart-Traffic-Management

Smart Traffic Lite is a Python and Streamlit-based traffic management
simulation featuring adaptive signal timing, emergency vehicle priority,
traffic analytics, lane-wise AQI monitoring, and downloadable CSV reports.
It identifies lanes with the highest entered AQI and visualizes traffic data.
Vehicle counts and AQI readings are entered manually; this prototype does not
control real traffic signals or read physical sensors.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with
   GitHub.
2. Choose **Create app** and select this repository.
3. Select the `main` branch and set the app file path to `app.py`.
4. Choose **Deploy**.

The app dependencies are listed in `requirements.txt`.
