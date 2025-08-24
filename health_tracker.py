import streamlit as st
import datetime
import requests
import json
import os
from dotenv import load_dotenv 

load_dotenv()

# =========================================================================
# === IMPORTANT: Medical Disclaimer ===
# This application is for informational purposes only and is not a substitute
# for professional medical advice, diagnosis, or treatment. Always seek the
# advice of your physician or other qualified health provider with any
# questions you may have regarding a medical condition.
# =========================================================================
st.warning("⚠️ **Disclaimer:** This app is for informational purposes only and is not a substitute for professional medical advice. Always consult with a healthcare professional.")

# =========================================================================
# === API Key and Endpoint Configuration ===
# =========================================================================
API_KEY = os.getenv("API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# =========================================================================
# === APP UI: THEME AND STYLING ===
# Custom CSS is injected to make the app more visually appealing.
# =========================================================================
st.markdown("""
<style>
    /* Main body background and text color */
    body {
        background-color: #ffe4e1; /* A soft, pale pink */
        color: #333333;
        font-family: Arial, sans-serif;
    }

    /* Streamlit container styling for a professional look */
    .stApp {
        background-color: #ffe4e1;
        background-attachment: fixed;
    }

    .css-1d37gxe { /* Main content container */
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #ff69b4; /* Hot pink for headers */
        font-weight: bold;
    }
    
    /* Custom button styling */
    .stButton>button {
        background-color: #ff69b4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        background-color: #ff1493; /* Deeper pink on hover */
    }
    
    /* Info box styling */
    .stAlert {
        border-left: 5px solid #ff69b4;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================================
# === APP UI: INPUTS ===
# All user inputs are collected in the first section of the page.
# =========================================================================
st.title("Nourish & Flow 🌻")
st.markdown("A comprehensive tool to track your cycle, check for symptoms(PCOS/PCOD),and get a personalized diet chart.")

# --- Period Tracker Section ---
st.header("🗓️ Period Tracker")
last_period_date = st.date_input("When did your last period start?", datetime.date.today())
cycle_length = st.number_input("What is your average cycle length (in days)?", min_value=21, max_value=35, value=28)

# --- PCOD/PCOS Symptom Checker Section ---
st.header("🩺PCOD/PCOS Symptom Checker")
symptoms = [
    "Irregular or infrequent periods",
    "Excess facial or body hair (hirsutism)",
    "Acne on the face, chest, or upper back",
    "Weight gain, especially around the abdomen",
    "Thinning hair on the scalp",
    "Darkening of skin around the neck, groin, or under breasts (acanthosis nigricans)",
    "Difficulty getting pregnant"
]
selected_symptoms = st.multiselect("Select any symptoms you have experienced:", symptoms)
severity_level = st.selectbox("How would you describe your PCOD/PCOS severity?", ["Mild", "Moderate", "Severe", "Unsure"])

# --- Diet Chart Generator Section ---
st.header("🍏 Personalized Diet Chart Generator")
st.info("Please enter your details to generate a customized diet plan.")
col1, col2 = st.columns(2)
with col1:
    height = st.number_input("Enter your height in cm", min_value=50, max_value=250, value=160)
with col2:
    weight = st.number_input("Enter your current weight in kg", min_value=20, max_value=200, value=60)

food_preference = st.radio("What are your dietary preferences?", ("Vegetarian", "Non-Vegetarian"))
allergies = st.text_input("List any food allergies or aversions (e.g.,'dairy, nuts, gluten,eggs')")

# The main button to trigger all calculations and display the report
if st.button("Generate Health Report"):
    
    # =========================================================================
    # === Functions for API Calls and Calculations ===
    # These functions are called when the button is pressed.
    # =========================================================================
    
    def get_pcod_likelihood(symptoms):
        """Calculates a simple likelihood based on the number of symptoms."""
        num_symptoms = len(symptoms)
        if num_symptoms == 0:
            return "Based on your selection, the likelihood is **low**."
        elif num_symptoms <= 2:
            return "Based on your selection, the likelihood is **moderate**."
        elif num_symptoms <= 4:
            return "Based on your selection, the likelihood is **high**."
        else:
            return "Based on your selection, the likelihood is **very high**.Please consult a doctor."

    def get_diet_plan(height, weight, preference, allergies, severity):
        """Generates a personalized diet plan using the Gemini API."""
        if API_KEY == "YOUR_GEMINI_API_KEY":
            return "⚠️ **API Key Missing:** Please enter your API key in the script to generate a diet chart."
        
        # Calculate Broca's Index for ideal weight as a simple measure
        # This is a general guideline and may not be suitable for all body types
        ideal_weight = height - 100
        
        prompt = f"""
        You are a highly knowledgeable nutritionist specializing in PCOD/PCOS.
        A user needs a personalized diet chart based on their information.

        Here are the user's details:
        - Current Weight: {weight} kg
        - Ideal Weight (Broca's Index): {ideal_weight} kg
        - Dietary Preference: {preference}
        - PCOD/PCOS Severity: {severity}
        - Food Allergies/Aversions: {allergies if allergies else 'None'}

        Based on these details, please provide a comprehensive and detailed one-week diet chart.
        The chart should include meal suggestions for breakfast, lunch, dinner, and snacks.
        The diet should be tailored for a person with {severity} PCOD/PCOS.
        Mention key dietary principles like low-GI foods, adequate protein, and healthy fats.
        The plan should be easy to follow, ingredients that are easily available in indian market and should not require complex ingredients.
        Provide a friendly,encouraging opening and closing statement.
        """

        try:
            headers = {'Content-Type': 'application/json'}
            payload = {'contents': [{'parts': [{'text': prompt}]}]}
            
            response = requests.post(
                f"{GEMINI_API_URL}?key={API_KEY}",
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()

            # Add this line to explicitly set the encoding to UTF-8
            response.encoding = 'utf-8'
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0 and 'content' in result['candidates'][0]:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "Could not generate a diet plan. Please try again."
        
        except requests.exceptions.RequestException as e:
            return f"An error occurred while calling the API: {e}"

    # =========================================================================
    # === APP UI: SUMMARY PAGE ===
    # This section is only displayed after the button is clicked.
    # =========================================================================
    st.markdown("---")
    st.header("📝 Your Personalized Health Report")

    # --- Period Prediction ---
    next_period_date = last_period_date + datetime.timedelta(days=cycle_length)
    st.subheader(" Next Period Prediction")
    st.write(f"Based on your last period and cycle length, your next period is expected on: **{next_period_date.strftime('%B %d, %Y')}**")

    # --- PCOD/PCOS Likelihood ---
    st.subheader(" PCOD/PCOS Likelihood")
    likelihood = get_pcod_likelihood(selected_symptoms)
    st.markdown(likelihood)
    st.markdown("---")
    
    # --- BMI and Broca's Index ---
    st.subheader(" Body Metrics")
    
    # Calculate BMI
    bmi = weight / ((height / 100) ** 2)
    st.write(f"Your BMI is: **{bmi:.2f}**")
    st.info("BMI or Body Mass Index is a quick way to check if your weight is healthy for your height. It's a screening tool that helps doctors see if you are in a healthy, underweight, or overweight range.")
    
    # Provide BMI interpretation
    if bmi < 18.5:
        st.write("BMI Status: Underweight")
    elif bmi >= 18.5 and bmi < 24.9:
        st.write("BMI Status: Normal weight")
    elif bmi >= 25 and bmi < 29.9:
        st.write("BMI Status: Overweight")
    else:
        st.write("BMI Status: Obesity")

    # Calculate and show Broca's Index
    broca_index = height - 100
    st.write(f"Your ideal weight is approximately **{broca_index} kg**.")
    st.info("Ideal weight or in other terms the weight you should maintain to be healthy can be found through Broca's Index this is a very simple formula to estimate your ideal body weight in kilograms, based only on your height in centimeters.")
    st.markdown("---")

    # --- Diet Plan ---
    st.subheader(" Personalized Diet Plan")
    st.info("This diet plan is AI-generated and for informational purposes only. Consult with a professional before making any significant changes to your diet.")
    
    with st.spinner('Generating your personalized diet chart...'):
        diet_chart = get_diet_plan(height, weight, food_preference, allergies, severity_level)
        st.markdown(diet_chart)

    # --- Notepad Download Button ---
    if diet_chart:
        st.download_button(
            label="Download Diet Plan as Text File",
            data=diet_chart,
            file_name="PCOD_Diet_Plan.txt",
            mime="text/plain"
        )

    # --- Final Disclaimer ---
    st.markdown("---")
    st.subheader("Important Final Disclaimer")
    st.error("This report is for general guidance only. It is not a substitute for professional medical advice, diagnosis, or treatment. If you have underlying health conditions such as diabetes, thyroid issues, or other concerns, please consult a qualified healthcare professional before following any of these suggestions.")
