import pickle
import streamlit as st
import math as math

st.title("Stellar Classification App 🌟")
st.write("Enter the stellar parameters to get the classification:")

# Load the trained model
with open('stellarClassifiactionModel.pkl', 'rb') as file:
    model = pickle.load(file)
print(type(model))
# Input fields
bv = st.number_input("Enter B-V Value:")
luminosity = st.number_input("Enter Luminosity:")
parallax = st.number_input("Enter Parallax:", value=0.0)
app_mag = st.number_input("Enter Apparent Magnitude:", value=0.0)

# Determine magnitude to use
if parallax>0:
    magnitude=app_mag + 5 * math.log10(parallax/100.)

temperature = 4600*((1/((0.92*bv)+1.7))+(1/((0.92*bv)+0.62)))
radius = ((((luminosity*3.828*(10**26))/(4*math.pi*5.67*(10**-8)*(temperature**4)))**(1/2))/(6.95*(10**8)))
if luminosity!=0:
  age = 10*(luminosity**-0.7)

# Predict button
if st.button("Classify Star"):
    try:
        # Prediction
        features = [[bv, luminosity, magnitude,temperature,radius,age]]
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities) * 100
        st.write(f"### Predicted Stellar Type: {prediction}")
        st.write(f"### Confidence Score: {confidence:.2f}%")

    except Exception as e:
        st.write("Error occurred:", e)
