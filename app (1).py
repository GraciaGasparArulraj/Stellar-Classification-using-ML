import joblib
import streamlit as st
import math as math
import requests
from astropy.io import fits
from io import BytesIO
from PIL import Image

def hms_to_degrees(h, m, s):
    return (h + m / 60 + s / 3600) * 15

def dms_to_degrees(d, m, s):
    sign = -1 if d < 0 else 1
    return sign * (abs(d) + m / 60 + s / 3600)

def get_fits_image(ra, dec):
    """Fetch FITS image dynamically from NASA SkyView"""
    url = f"https://skyview.gsfc.nasa.gov/cgi-bin/pskcall?survey=DSS2&position={ra},{dec}&Return=FITS"
    response = requests.get(url)
    
    if response.status_code == 200:
        return BytesIO(response.content)  # Return FITS data as BytesIO
    else:
        return None

def fits_to_png(fits_data):
    """Convert FITS data to an 8-bit grayscale image"""
    with fits.open(fits_data) as hdul:
        image_data = hdul[0].data  # Extract image array

    # Normalize the image to 8-bit (0-255)
    image_data = np.nan_to_num(image_data)  # Replace NaNs with 0
    image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data)) * 255
    image_data = image_data.astype(np.uint8)  # Convert to 8-bit

    return Image.fromarray(image_data)  # Convert to PIL Image
    
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
    fits_data = get_fits_image(ra, dec)
        
    if fits_data:
        image = fits_to_png(fits_data)
        st.image(image, caption="Star Image from NASA SkyView")
    else:
        st.write("Could not retrieve star image. Check RA/Dec values.")
