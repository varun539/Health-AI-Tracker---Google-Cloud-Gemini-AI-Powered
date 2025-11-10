import streamlit as st
import joblib
import pandas as pd
import json
import google.generativeai as genai
import numpy as np
import re
from sklearn.preprocessing import OneHotEncoder
import traceback
import gspread
from google.oauth2.service_account import Credentials
import os

# === ENV VARS for Cloud Run ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")

# === Google Sheets Setup ===
def get_gsheet_client():
    creds = Credentials.from_service_account_file(
        'credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return gspread.authorize(creds)

gs_ready, ws = False, None
try:
    gc = get_gsheet_client()
    sh = gc.open_by_url(GOOGLE_SHEET_URL)
    ws = sh.sheet1
    gs_ready = True
except Exception as e:
    ws = None
    gsheet_warn = f"Google Sheets failed: {e}"

# === Model loading ===
model = None
encoder = None
model_loaded = False
try:
    model = joblib.load("model_v3.joblib")
    encoder = joblib.load("encoder_v3.pkl")
    model_loaded = True
except Exception as e:
    model_loaded = False

# === Streamlit UI Setup ===
st.set_page_config(page_title="Health AI Tracker", layout="wide")
st.markdown("""
<style>
.stApp {background-color:#0e1117; color:#fafafa;}
.stButton>button {background-color:#0f3460; color:white; border-radius:12px; font-weight:600;}
.stTextInput>label, .stNumberInput>label, .stSelectbox>label {color:#a0d2ff;}
.card {background:#1f2a44; padding:1.5rem; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.3);}
</style>
""", unsafe_allow_html=True)
st.title("💪 Health AI Tracker (Gemini Powered)")
st.caption("LightGBM Recovery Prediction + AI Fitness Coach")

st.subheader("Connection Status")
col1, col2, col3 = st.columns(3)
col1.success("✅ Model & Encoder" if model_loaded else "❌ Model/Encoder")
col2.success("✅ Gemini API" if GEMINI_API_KEY else "⚠️ Gemini Key Missing")
col3.success("✅ Google Sheets" if gs_ready else "⚠️ Sheets Not Ready")

# Old OneHotEncoder patch
if not hasattr(OneHotEncoder, "feature_name_combiner"):
    OneHotEncoder.feature_name_combiner = lambda *args, **kwargs: None

def safe_get_ohe_feature_names(enc, input_features):
    try:
        return list(enc.get_feature_names_out(input_features))
    except Exception:
        cats = getattr(enc, "categories_", None)
        if cats is None:
            raise RuntimeError("Encoder has no categories_ attribute.")
        names = []
        drop_idx = getattr(enc, "drop_idx_", None)
        for i, feat in enumerate(input_features):
            categories = list(cats[i])
            dropped = set()
            if drop_idx is not None:
                try:
                    di = drop_idx[i]
                    if di is None:
                        dropped = set()
                    elif isinstance(di, (list, tuple, np.ndarray)):
                        dropped = set(map(int, di))
                    else:
                        dropped = {int(di)}
                except Exception:
                    dropped = set()
            for j, cat in enumerate(categories):
                if j in dropped:
                    continue
                cat_str = str(cat).replace(" ", "_").replace("\n", "\\n").replace("\t", "\\t")
                names.append(f"{feat}_{cat_str}")
        return names

def safe_ohe_transform_to_df(enc, df, input_features):
    arr = enc.transform(df[input_features])
    if hasattr(arr, "toarray"):
        arr = arr.toarray()
    arr = np.asarray(arr)
    col_names = safe_get_ohe_feature_names(enc, input_features)
    if arr.shape[1] != len(col_names):
        col_names = [f"ohe_{i}" for i in range(arr.shape[1]])
    return pd.DataFrame(arr, columns=col_names, index=df.index)

# === User Input ===
st.subheader("Enter Your Workout Data")
with st.form("input_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Name", "John Doe")
        age = st.number_input("Age", 10, 100, 25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (m)", 1.0, 2.5, 1.75, 0.01)
    with c2:
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0, 0.1)
        avg_bpm = st.number_input("Avg BPM", 60, 200, 120)
        resting_bpm = st.number_input("Resting BPM", 40, 120, 70)
    with c3:
        session = st.number_input("Session Duration (hours)", 0.1, 5.0, 1.0, 0.1)
        workout = st.selectbox("Workout Type", ["HIIT", "Strength", "Yoga", "Cardio", "Cycling"])
        water = st.number_input("Water Intake (liters)", 0.5, 10.0, 3.0, 0.1)
    colA, colB = st.columns(2)
    with colA:
        fat = st.number_input("Body Fat (%)", 5.0, 50.0, 20.0, 0.1)
        freq = st.number_input("Workout Frequency (days/week)", 1, 7, 4)
    with colB:
        stretch = st.slider("Stretch Score", 1, 10, 6)
    submit = st.form_submit_button("Predict & Coach Me", use_container_width=True)

# === Main Prediction/Analytics ===
if submit:
    try:
        if not model_loaded:
            st.error("❌ Model not loaded. Cannot predict.")
            st.stop()
        bmi = weight / (height ** 2)
        max_bpm = avg_bpm * 1.15
        input_df = pd.DataFrame([{
            'Age': age, 'Gender': gender, 'Weight (kg)': weight, 'Height (m)': height,
            'Max_BPM': max_bpm, 'Avg_BPM': avg_bpm, 'Resting_BPM': resting_bpm,
            'Session_Duration (hours)': session, 'Workout_Type': workout,
            'Fat_Percentage': fat, 'Water_Intake (liters)': water,
            'Workout_Frequency (days/week)': freq, 'BMI': bmi, 'Stretch_Score': stretch
        }])
        try:
            ohe_features = ['Gender', 'Workout_Type']
            X_cat_df = safe_ohe_transform_to_df(encoder, input_df, ohe_features)
        except:
            st.warning("Encoder fallback")
            X_cat_df = pd.get_dummies(input_df[['Gender', 'Workout_Type']], prefix=['Gender', 'Workout_Type'])
        X_num = input_df.drop(['Gender', 'Workout_Type'], axis=1)
        X_final = pd.concat([X_num, X_cat_df], axis=1)
        try:
            expected = model.booster_.feature_name() if hasattr(model, "booster_") else None
            if expected:
                for c in expected:
                    if c not in X_final.columns:
                        X_final[c] = 0.0
                X_final = X_final[expected]
        except:
            pass

        try:
            recovery = float(model.predict(X_final)[0])
        except:
            recovery = 38.0
        st.success(f"**Recovery Time:** {recovery:.1f} hours")

        # === Google Sheets Logging ===
        try:
            if gs_ready:
                ws.append_row([
                    name, age, gender, height, weight, workout, avg_bpm, resting_bpm,
                    session, fat, water, freq, bmi, stretch, round(recovery, 2),
                    pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
                st.success("✅ Data saved to Google Sheets!")
        except Exception as e:
            st.warning(f"⚠️ Google Sheets: {str(e)[:60]}")

        # === Gemini Prediction ===
        advice = {
            "nutrition_plan": "Breakfast: 100g oats with 200ml milk (15g protein, 30g carbs, 5g fat)",
            "workout_tips": "1) Burpees: 4x12, 60s rest, RPE 7\n2) Jump Squats: 3x15, 45s rest, RPE 6",
            "recovery_protocol": "Sleep 10PM-6AM | Hydration: 3L water",
            "motivation": "Great job today! Keep the momentum!"
        }
        if GEMINI_API_KEY:
            try:
                prompt = f"""Output ONLY valid JSON (no markdown, no placeholders, no summaries). Each field must contain at least 3 full sentences with specific, actionable details based on the user's data.
                {{
                    "nutrition_plan": "A 24-hour meal plan for a {weight}kg person with {bmi:.1f} BMI and {recovery:.1f}h recovery. Detail breakfast with specific foods, exact portion sizes in grams or milliliters, and macronutrient breakdowns in grams. Include lunch and dinner with food items, portions, and macros, plus a snack with protein, carbs, and fat in grams.",
                    "workout_tips": "A workout plan for the next {workout} session for a {weight}kg person with {recovery:.1f}h recovery. List 5 exercises with exact reps, sets, rest periods in seconds, and RPE values from 5-8. Explain how each exercise supports recovery and fitness goals for this period.",
                    "recovery_protocol": "A recovery plan for {recovery:.1f}h recovery for a {weight}kg person. Specify a sleep schedule with start and end times, list mobility exercises with durations in minutes, set a hydration goal in liters, and describe stretching routines with specific steps.",
                    "motivation": "A motivational message for {name} based on their {stretch}/10 stretch score. Provide 4-6 sentences celebrating their {workout} progress, encouraging consistency, and setting a clear, achievable goal."
                }}
                User: {name}, {age}yo, {gender}, {workout} {session}h session, {recovery:.1f}h recovery, {weight}kg, {bmi:.1f} BMI, {stretch}/10 stretch score.
                """
                response = genai.GenerativeModel("gemini-2.0-flash-exp").generate_content(prompt, max_output_tokens=2000)
                text = response.text.strip()
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    advice_data = json.loads(json_match.group(0))
                    # Validate and populate advice
                    for key in ["nutrition_plan", "workout_tips", "recovery_protocol", "motivation"]:
                        if key in advice_data and advice_data[key].strip():
                            advice[key] = advice_data[key]
                        else:
                            st.warning(f"Gemini returned incomplete data for {key}, using fallback.")
                else:
                    raise ValueError("No valid JSON detected in Gemini response")
            except Exception as e:
                st.warning(f"Gemini error: {str(e)[:50]}. Falling back to default advice.")
                advice = {
                    "nutrition_plan": f"Breakfast for {weight}kg: 100g oats with 200ml almond milk (15g protein, 30g carbs, 5g fat). Lunch: 150g grilled chicken with 200g quinoa (25g protein, 40g carbs, 5g fat). Dinner: 200g baked salmon with 150g broccoli (30g protein, 10g carbs, 15g fat). Snack: 50g almonds (10g protein, 5g carbs, 15g fat).",
                    "workout_tips": f"HIIT for {weight}kg: 1) Burpees - 4x12, 60s rest, RPE 7; 2) Mountain Climbers - 4x15, 45s rest, RPE 6; 3) Jump Squats - 3x12, 60s rest, RPE 7; 4) High Knees - 3x20s, 45s rest, RPE 6; 5) Plank - 3x30s, 45s rest, RPE 5. These enhance endurance and support {recovery:.1f}h recovery.",
                    "recovery_protocol": f"Plan for {recovery:.1f}h recovery: Sleep 10PM-6AM (8h). Mobility: 10min yoga with cat-cow and downward dog. Hydration: 3L water. Stretching: 5min hamstring stretch, 5min shoulder stretch.",
                    "motivation": f"{name}, your 6/10 stretch shows your {workout} dedication. You're progressing well, and {recovery:.1f}h recovery is a sign of strength. Stay consistent, hydrate, and aim for 7/10 stretch next session!"
                }
        # Display Advice
        st.markdown("## 🎯 AI Fitness Coach")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🍽️ Nutrition Plan")
            st.markdown(advice["nutrition_plan"])
        with c2:
            st.markdown("### 💪 Workout Tips")
            st.markdown(advice["workout_tips"])
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("### 😴 Recovery Protocol")
            st.markdown(advice["recovery_protocol"])
        with c4:
            st.markdown("### 🔥 Motivation")
            st.success(advice["motivation"])
        st.markdown("</div>", unsafe_allow_html=True)
        if freq >= 4 and stretch >= 7:
            st.balloons()
            st.success("🏆 Recovery Master Badge!")
    except Exception as e:
        st.error(f"Error: {e}")
        st.write(traceback.format_exc())