import joblib
import streamlit as st
import math as math
import requests
from PIL import Image
from io import BytesIO

def hms_to_degrees(h, m, s):
    return (h + m / 60 + s / 3600) * 15

def dms_to_degrees(d, m, s):
    sign = -1 if d < 0 else 1
    return sign * (abs(d) + m / 60 + s / 3600)
    
st.title("Stellar Classification App 🌟")
st.write("Enter the stellar parameters to get the classification:")

# Load the trained model
model=joblib.load('stellarClassifiactionModel.pkl')
# Input fields
bv = st.number_input("Enter B-V Value:")
luminosity = st.number_input("Enter Luminosity:")
magnitude_option = st.selectbox(
    "Do you have the Absolute Magnitude?",
    ("Yes", "No")
)

# If the user has absolute magnitude, ask for it
if magnitude_option == "Yes":
    magnitude = st.number_input("Enter Absolute Magnitude:", value=0.0)

# If the user doesn't have absolute magnitude, ask for Parallax and Apparent Magnitude
else:
    parallax = st.number_input("Enter Parallax:", value=0.0)
    app_mag = st.number_input("Enter Apparent Magnitude:", value=0.0)

    # Calculate Absolute Magnitude only if parallax is greater than 0
    if parallax > 0:
        magnitude = app_mag + 5 * math.log10(parallax / 100.0)

temperature = 4600*((1/((0.92*bv)+1.7))+(1/((0.92*bv)+0.62)))
radius = ((((luminosity*3.828*(10**26))/(4*math.pi*5.67*(10**-8)*(temperature**4)))**(1/2))/(6.95*(10**8)))
if luminosity!=0:
  age = 10*(luminosity**-0.7)

# Predict button
if st.button("Classify Star"):
    try:
        # Prediction
        features = [[bv,temperature,luminosity,radius,magnitude,age]]
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities) * 100
        st.write(f"### Predicted Stellar Type: {prediction}")
        st.write(f"### Confidence Score: {confidence:.2f}%")

    except Exception as e:
        st.write("Error occurred:", e)
        
# RA and Dec input fields
ra_h = st.number_input("Enter Right Ascension Hours:", value=0, min_value=0, max_value=23)
ra_m = st.number_input("Enter Right Ascension Minutes:", value=0, min_value=0, max_value=59)
ra_s = st.number_input("Enter Right Ascension Seconds:", value=0.0, min_value=0.0, max_value=59.9999)
dec_d = st.number_input("Enter Declination Degrees:", value=0, min_value=-90, max_value=90)
dec_m = st.number_input("Enter Declination Minutes:", value=0, min_value=0, max_value=59)
dec_s = st.number_input("Enter Declination Seconds:", value=0.0, min_value=0.0, max_value=59.9999)

# Convert RA and Dec to decimal degrees
ra = hms_to_degrees(ra_h, ra_m, ra_s)
dec = dms_to_degrees(dec_d, dec_m, dec_s)

if st.button("Show Star Image"):
    if ra and dec:
        # Fetch image from NASA SkyView
        image_url = f"https://skyview.gsfc.nasa.gov/cgi-bin/pskcall?RA={ra}&DEC={dec}&Survey=DSS"
        response = requests.get(image_url)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption="Star Image from NASA SkyView")
        else:
            st.error("Could not retrieve star image. Please check RA/Dec values.")
    else:
        st.warning("Please enter valid RA and Dec values.")
