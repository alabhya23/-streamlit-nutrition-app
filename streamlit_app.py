
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("Labeled_Data.csv")

# Disease-condition mapping
condition_weights = {
    'diabetes': {'fibre_g': 0.15, 'protein_g': 0.12, 'freesugar_g': -0.15, 'carb_g': -0.12, 'fat_g': -0.08},
    'obesity': {'fibre_g': 0.15, 'protein_g': 0.12, 'freesugar_g': -0.12, 'fat_g': -0.10, 'carb_g': -0.08},
    'high_bp': {'sodium_mg': -0.18, 'potassium_mg': 0.12, 'magnesium_mg': 0.08, 'calcium_mg': 0.08},
    'low_bp': {'sodium_mg': 0.15, 'iron_mg': 0.10, 'protein_g': 0.08, 'fibre_g': -0.05}
}

condition_avoid = {
    'diabetes': ["Sugary drinks", "White bread", "Pastries", "Fried foods"],
    'obesity': ["Fast food", "Processed snacks", "Sugary beverages", "Refined carbs"],
    'high_bp': ["Salty snacks", "Pickles", "Canned soups", "Red meat"],
    'low_bp': ["Alcohol", "High-carb meals without protein", "Bananas", "High potassium fruits"]
}

nutrient_info = {
    'fibre_g': "Helps in digestion and regulates blood sugar.",
    'protein_g': "Essential for muscle repair and satiety.",
    'freesugar_g': "Should be limited to control sugar spikes.",
    'carb_g': "Primary energy source, but should be moderated.",
    'fat_g': "Necessary for hormones, but excess leads to weight gain.",
    'sodium_mg': "Excess sodium increases blood pressure.",
    'potassium_mg': "Helps reduce sodium effects and maintain BP.",
    'iron_mg': "Essential for blood production."
}

def recommend_top_foods(df, condition, top_n=10):
    weights = condition_weights[condition]
    df_filtered = df.copy().fillna(0)
    df_filtered['score'] = sum(df_filtered[nutrient] * weight for nutrient, weight in weights.items() if nutrient in df_filtered.columns)
    top_foods = df_filtered.sort_values(by='score', ascending=False).head(top_n)
    return top_foods[['food_name', 'score'] + list(weights.keys())]

# UI layout
st.set_page_config(page_title="Smart Food Recommender", layout="wide")
st.title("🥗 Smart Health-Based Food Recommendation System")

# Input: Age, Gender, Condition
age = st.slider("Select Age", 10, 90, 30)
gender = st.radio("Select Gender", ["Male", "Female"])
condition = st.selectbox("Select Health Condition", ["Diabetes", "Obesity", "High_BP", "Low_BP"])

# Once selected, show results
if condition:
    condition_key = condition.lower()
    st.success(f"🎯 Based on your input (Age: {age}, Gender: {gender}, Condition: {condition}), here are your top food recommendations:")

    top_foods_df = recommend_top_foods(df, condition_key)

    # Section 1: Recommended Foods
    st.subheader("🍱 Top 10 Healthy Food Recommendations")
    st.dataframe(top_foods_df[['food_name', 'score']], use_container_width=True)

    # Section 2: Macronutrient Comparison
    st.subheader("📉 Macronutrient Comparison")
    nutrients = [col for col in ['carb_g', 'protein_g', 'fat_g'] if col in top_foods_df.columns]
    compare_df = top_foods_df.set_index('food_name')[nutrients]
    st.bar_chart(compare_df)

    # Section 3: Nutrient Tips
    st.subheader("🧠 Key Nutrient Benefits")
    for nutrient in list(condition_weights[condition_key].keys())[:3]:
        if nutrient in nutrient_info:
            st.markdown(f"**{nutrient}**: {nutrient_info[nutrient]}")

    # Section 4: Foods to Avoid
    st.subheader("📛 Foods to Avoid")
    avoid_list = condition_avoid.get(condition_key, [])
    st.markdown("Avoid consuming:")
    st.markdown("- " + "
- ".join(avoid_list))

    # Section 5: Download CSV
    st.subheader("📥 Export Your Recommendations")
    csv = top_foods_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Recommendations as CSV", data=csv, file_name="recommended_foods.csv", mime="text/csv")

    # Section 6: Explore Full Nutrients
    st.subheader("📋 Explore Nutrients in Recommended Foods")
    with st.expander("Click to Expand Full Nutrient Table"):
        st.dataframe(top_foods_df, use_container_width=True)

st.markdown("---")
st.caption("Built using Streamlit • Personalized food guidance with tips 💡")
