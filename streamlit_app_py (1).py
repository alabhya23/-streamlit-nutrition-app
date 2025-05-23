
import pandas as pd
import numpy as np

file_path = 'DataCleaned.csv'

# Read the CSV file
df = pd.read_csv(file_path)

data = pd.read_csv(file_path)

df.head()

df.columns

def convert_units(df, unit_mapping):
    """
    Converts units in a DataFrame based on the provided mapping.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the columns to convert.
        unit_mapping (dict): Dictionary mapping column suffixes (e.g., '_g', '_ug') to conversion factors.

    Returns:
        pd.DataFrame: A new DataFrame with updated values and column names.
    """
    df_converted = df.copy()

    for col in df.columns:
        for unit, factor in unit_mapping.items():
            if col.endswith(unit):  # Check if column has the unit suffix
                df_converted[col] = df[col] * factor  # Apply conversion
                df_converted.rename(columns={col: col.replace(unit, "_mg")}, inplace=True)  # Rename column

    return df_converted

# Define conversion factors
unit_mapping = {
    "_g": 1000,   # Convert grams to mg
    "_ug": 0.001  # Convert micrograms to mg
}

# Apply the function to df_selected
df = convert_units(df, unit_mapping)
# Display updated column names
print(df.columns)

df = df.drop(columns=['food_code', 'food_name', 'primarysource'])

df.head()

df.info()

df.columns

#df = df[['energy_kcal', 'carb_g', 'protein_g','fat_g','freesugar_g','fibre_g']]

def remove_outliers(df):
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[~((df < lower_bound) | (df > upper_bound)).any(axis=1)]

def find_multicollinear_features(corr_matrix, threshold=0.8):
    """
    Identify highly correlated (multicollinear) features based on a correlation matrix.

    Parameters:
        corr_matrix (pd.DataFrame): Correlation matrix of the dataset (df.corr()).
        threshold (float): Correlation coefficient threshold for considering features as collinear.

    Returns:
        list: A list of tuples with highly correlated feature pairs.
    """
    collinear_pairs = []
    cols = corr_matrix.columns

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):  # Avoid duplicate pairs and self-correlation
            if abs(corr_matrix.iloc[i, j]) > threshold:
                collinear_pairs.append((cols[i], cols[j], corr_matrix.iloc[i, j]))

    return collinear_pairs

top_20_nutrition_features = [
    'energy_kcal',     # Total energy is a key dietary measure
    'carb_mg',          # Major macronutrient
    'protein_mg',       # Essential macronutrient for body functions
    'fat_mg',           # Macronutrient, affects energy and health
    'freesugar_mg',     # High relevance for metabolic and dental health
    'fibre_mg',         # Important for gut health and satiety
    'sfa_mg',          # Saturated fat – linked to heart health
    'cholesterol_mg',  # Cardiovascular risk factor
    'sodium_mg',       # Blood pressure and heart health
    'potassium_mg',    # Balances sodium, essential for muscle and nerve function
    'calcium_mg',      # Bone health
    'iron_mg',         # Oxygen transport in blood
    'zinc_mg',         # Immunity and cellular metabolism
    'vita_mg',         # Vitamin A – vision and immune function
    'vite_mg',         # Vitamin E – antioxidant
    'vitd3_mg',        # Vitamin D3 – bone and immune health
    'vitk1_mg',        # Blood clotting and bone health
    'folate_mg',       # DNA synthesis and pregnancy nutrition
    'vitc_mg'          # Immune function and antioxidant
]


df_copy = df[top_20_nutrition_features]
df_copy = remove_outliers(df_copy)

indexes = df_copy.index

df_with_food_names = data.loc[indexes]
df = df.loc[indexes]
df_with_food_names.info()

"""# Diabetric Version

## Preprocessing
"""

df_selected_diabetes = pd.DataFrame()

diabetes_feature_weights = {
    "carb_mg": -1.5,           # High carbs can spike blood sugar
    "freesugar_mg": -3.0,      # Free sugars cause rapid glucose spikes
    "fibre_mg": 2.5,           # Fiber helps regulate blood sugar
    "energy_kcal": -1.0,      # Excess energy intake contributes to obesity and insulin resistance
    "energy_kj": -1.0,        # Same as kcal, included for consistency
    "protein_mg": 1.0,         # Moderate protein helps with satiety and glucose control
    "sfa_mg": -2.0,           # Saturated fats can contribute to insulin resistance
    "mufa_mg": 1.5,           # Monounsaturated fats improve insulin sensitivity
    "pufa_mg": 1.5,           # Polyunsaturated fats support metabolic health
    "cholesterol_mg": -0.5,   # High cholesterol is linked to cardiovascular risk
    "sodium_mg": -1.0,        # High sodium can lead to hypertension, a diabetes risk factor
    "potassium_mg": 1.5,      # Potassium supports insulin function
    "magnesium_mg": 2.0,      # Essential for insulin sensitivity
    "zinc_mg": 1.0,           # Supports insulin production
    "chromium_mg": 2.0,       # Involved in carbohydrate metabolism
    "vitd2_mg": 1.0,          # Vitamin D improves glucose metabolism
    "vitd3_mg": 1.0,          # Same as above
    "vitb3_mg": 0.5,          # Niacin impacts glucose regulation
    "vitb6_mg": 0.5,          # Involved in glucose metabolism
    "vitc_mg": 1.0,           # Antioxidant effects help with insulin function
    "carotenoids_mg": 1.0     # Antioxidants that support metabolic health
}

df_selected_diabetes = df[list(diabetes_feature_weights.keys())].copy(deep = True)
df_selected_diabetes = df_selected_diabetes.mul(pd.Series(diabetes_feature_weights), axis=1)

df_selected_diabetes.corr()

multicollinear_features_list = find_multicollinear_features(df_selected_diabetes.corr(),threshold = 0.85)
multicollinear_features_list

df_selected_diabetes.drop(['energy_kcal','energy_kj','zinc_mg','sfa_mg'],axis=1,inplace = True)

from sklearn.preprocessing import MinMaxScaler

# Normalizing the data
scaler = MinMaxScaler()
df_selected_scaled_diabetes = pd.DataFrame(scaler.fit_transform(df_selected_diabetes), columns=df_selected_diabetes.columns, index=df_selected_diabetes.index)

df_selected_scaled_diabetes.head()

df_selected_diabetes.info()

"""## Clustering"""

from sklearn.decomposition import PCA

pca = PCA(n_components=3)  # Reduce to 3 main components
df_pca = pd.DataFrame(pca.fit_transform(df_selected_scaled_diabetes), columns=["PC1", "PC2", "PC3"])


import skfuzzy as fuzz
import numpy as np

# Ensure data is in correct shape (samples, features) before clustering
data_array = df_pca.to_numpy()  # ✅ No transposition

# Apply Fuzzy C-Means clustering
n_clusters = 3
cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(data_array.T, c=n_clusters, m=2, error=0.005, maxiter=1000, init=None)

# Assign cluster labels based on maximum membership
cluster_labels = np.argmax(u, axis=0)  # Labels correspond to original sample order

# Verify label assignment to ensure they match index positions
assert len(cluster_labels) == len(df_selected_scaled_diabetes), "Mismatch in label assignment!"

# Assign labels to all dataframes
df_selected_scaled_diabetes["Health_Label"] = cluster_labels
df_selected_diabetes["Health_Label"] = cluster_labels
df_with_food_names['Health_Label_Diabetes'] = cluster_labels
# Display cluster distribution
print(df_selected_scaled_diabetes["Health_Label"].value_counts())

"""## Visualisation"""

import matplotlib.pyplot as plt
import seaborn as sns



list_of_columns = ['fibre_g','protein_g','freesugar_g','carb_g','Health_Label']

df_with_food_names.columns


"""1 cluster is healthy"""

df_pca.shape

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the data
ax.scatter(df_pca.iloc[:,0], df_pca.iloc[:,1], df_pca.iloc[:,2], c=df_selected_scaled_diabetes['Health_Label'], marker='o')


# Label axes
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')

# Show plot
plt.show()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the data

selected_df = df_selected_scaled_diabetes  # or obesity / high_bp etc.

ax.scatter(df_pca.iloc[:,0], df_pca.iloc[:,1], df_pca.iloc[:,2], c=selected_df['Health_Label'], marker='o')

# Label axes
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')

# Show plot
plt.show()

selected_df = df_selected_scaled_diabetes  # or obesity / high_bp etc.

ax.scatter(df_pca.iloc[:,0], df_pca.iloc[:,1], df_pca.iloc[:,2], c=selected_df['Health_Label'], marker='o')

from sklearn.metrics import silhouette_score
"""
# Compute Fuzzy Partition Coefficient (FPC)
fpc = np.sum(u**2) / u.shape[1]
print(f"Fuzzy Partition Coefficient (FPC): {fpc:.4f}")
"""
# Compute Silhouette Score
silhouette_avg = silhouette_score(df_pca, cluster_labels)
print(f"Silhouette Score: {silhouette_avg:.4f}")

df_with_food_names[df_with_food_names['Health_Label_Diabetes'] == 1]

"""# Obesity Centric

## Preprocessing
"""

df_selected_obesity = pd.DataFrame()

obesity_nutrition_weights = {
    'energy_kcal': 0.15,       # Critical to control for weight loss
    'freesugar_mg': 0.12,      # Reduce to avoid excess calories
    'fat_mg': 0.08,            # Total fat control
    'sfa_mg': 0.08,            # Limit saturated fat
    'fibre_mg': 0.12,          # High fiber promotes satiety
    'protein_mg': 0.10,        # Maintain lean mass
    'carb_mg': 0.05,           # Manage refined carbs
    'sodium_mg': 0.07,         # Often co-managed in obesity/hypertension
    'potassium_mg': 0.04,      # Balance sodium, support heart health
    'vitc_mg': 0.03,           # Antioxidant and metabolic support
    'vitb6_mg': 0.02,          # Supports metabolism
    'vitb3_mg': 0.02,          # Same here
    'folate_mg': 0.02,         # DNA synthesis, general health
    'vite_mg': 0.02,           # Antioxidant
    'calcium_mg': 0.03,        # Bone health during weight loss
    'iron_mg': 0.02,           # Avoid deficiencies
    'zinc_mg': 0.02,           # Metabolic function
    'magnesium_mg': 0.02,      # Cardiovascular and insulin sensitivity
    'vitd3_mg': 0.02,          # Often deficient in obesity
    'carotenoids_mg': 0.01     # Antioxidant marker
}


df_selected_obesity = df[list(obesity_nutrition_weights.keys())].copy(deep = True)
df_selected_obesity = df_selected_obesity.mul(pd.Series(obesity_nutrition_weights), axis=1)

df_selected_obesity.corr()

multicollinear_features_list = find_multicollinear_features(df_selected_obesity.corr(),threshold = 0.85)
multicollinear_features_list

df_selected_obesity.drop(['fat_mg'],axis=1,inplace = True)

from sklearn.preprocessing import MinMaxScaler

# Normalizing the data
scaler = MinMaxScaler()
df_selected_scaled_obesity = pd.DataFrame(scaler.fit_transform(df_selected_obesity), columns=df_selected_obesity.columns, index=df_selected_obesity.index)

df_selected_scaled_obesity.head()

df_selected_scaled_obesity.info()



"""## Clustering"""

from sklearn.decomposition import PCA

pca = PCA(n_components=3)  # Reduce to 3 main components
df_pca = pd.DataFrame(pca.fit_transform(df_selected_scaled_obesity), columns=["PC1", "PC2", "PC3"])


import skfuzzy as fuzz
import numpy as np

# Ensure data is in correct shape (samples, features) before clustering
data_array = df_pca.to_numpy()  # ✅ No transposition

# Apply Fuzzy C-Means clustering
n_clusters = 3
cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(data_array.T, c=n_clusters, m=2, error=0.005, maxiter=1000, init=None)

# Assign cluster labels based on maximum membership
cluster_labels = np.argmax(u, axis=0)  # Labels correspond to original sample order

# Verify label assignment to ensure they match index positions
assert len(cluster_labels) == len(df_selected_scaled_diabetes), "Mismatch in label assignment!"

# Assign labels to all dataframes
df_selected_scaled_obesity["Health_Label"] = cluster_labels
df_selected_obesity["Health_Label"] = cluster_labels
df_with_food_names['Health_Label_Obesity'] = cluster_labels
# Display cluster distribution
print(df_selected_scaled_obesity["Health_Label"].value_counts())





"""# Blood Pressure Centric

## Preprocessing
"""

df_selected_high_bp = pd.DataFrame()
df_selected_low_bp = pd.DataFrame()

high_bp_counter_weights = {
    'sodium_mg': -0.18,           # Strongly limit
    'freesugar_mg': -0.06,        # Limit added sugars
    'sfa_mg': -0.07,              # Limit saturated fat
    'cholesterol_mg': -0.05,      # Limit cholesterol
    'fat_mg': -0.04,              # Moderate fat

    'potassium_mg': 0.12,         # Increase potassium
    'magnesium_mg': 0.08,         # Support blood vessel relaxation
    'calcium_mg': 0.08,           # Improve blood pressure control
    'fibre_mg': 0.08,             # Cardiovascular benefits
    'protein_mg': 0.04,           # Helps balance meals

    'carb_mg': 0.03,              # Prefer complex carbs
    'vite_mg': 0.02,              # Antioxidant support
    'vitc_mg': 0.02,              # Vessel protection
    'folate_mg': 0.02,            # Lowers homocysteine
    'vitb6_mg': 0.02,             # Works with folate
    'zinc_mg': 0.02,              # General support
    'vitk1_mg': 0.01,             # Supports vascular function
    'vitd3_mg': 0.02,             # Often deficient
    'carotenoids_mg': 0.02,       # Antioxidant benefits
    'iron_mg': 0.02               # Balanced intake
}

low_bp_counter_weights = {
    'sodium_mg': 0.15,            # Increase sodium intake
    'iron_mg': 0.10,              # Prevent anemia-related hypotension
    'protein_mg': 0.08,           # Support blood volume
    'fibre_mg': -0.05,            # Too much may lower BP further
    'carb_mg': 0.05,              # Helps prevent drops post-meal

    'fat_mg': 0.04,               # Maintain energy
    'cholesterol_mg': 0.03,       # Less concern here
    'potassium_mg': -0.06,        # Excess can worsen hypotension
    'magnesium_mg': 0.05,         # Supports vascular tone
    'calcium_mg': 0.05,           # Balances vascular activity

    'folate_mg': 0.05,            # Prevents folate-deficiency anemia
    'vitb1_mg': 0.04,             # Deficiency linked to low BP
    'vitb6_mg': 0.04,             # Circulation support
    'vitc_mg': 0.02,              # General support
    'vite_mg': 0.02,              # Antioxidant
    'vitk1_mg': 0.01,             # Blood clotting
    'zinc_mg': 0.02,              # General balance
    'carotenoids_mg': 0.03,       # Antioxidant
    'freesugar_mg': 0.02          # Can help with acute hypotension
}



df_selected_high_bp = df[list(high_bp_counter_weights.keys())].copy(deep = True)
df_selected_high_bp = df_selected_high_bp.mul(pd.Series(high_bp_counter_weights), axis=1)

df_selected_low_bp = df[list(low_bp_counter_weights.keys())].copy(deep = True)
df_selected_low_bp = df_selected_low_bp.mul(pd.Series(low_bp_counter_weights), axis=1)

df_selected_high_bp.corr()

multicollinear_features_list1 = find_multicollinear_features(df_selected_high_bp.corr(),threshold = 0.85)
multicollinear_features_list1

df_selected_high_bp.drop(['sfa_mg'],axis=1,inplace = True)

multicollinear_features_list2 = find_multicollinear_features(df_selected_low_bp.corr(),threshold = 0.85)
multicollinear_features_list2

from sklearn.preprocessing import MinMaxScaler

# Normalizing the data
scaler = MinMaxScaler()
df_selected_scaled_high_bp = pd.DataFrame(scaler.fit_transform(df_selected_high_bp), columns=df_selected_high_bp.columns, index=df_selected_high_bp.index)
scaler = MinMaxScaler()
df_selected_scaled_low_bp = pd.DataFrame(scaler.fit_transform(df_selected_low_bp), columns=df_selected_low_bp.columns, index=df_selected_low_bp.index)



"""## Clustering"""

from sklearn.decomposition import PCA

pca = PCA(n_components=3)  # Reduce to 3 main components
df_pca1 = pd.DataFrame(pca.fit_transform(df_selected_scaled_high_bp), columns=["PC1", "PC2", "PC3"])
df_pca2 = pd.DataFrame(pca.fit_transform(df_selected_scaled_low_bp), columns=["PC1", "PC2", "PC3"])


import skfuzzy as fuzz
import numpy as np

# Ensure data is in correct shape (samples, features) before clustering
data_array = df_pca1.to_numpy()  # ✅ No transposition

# Apply Fuzzy C-Means clustering
n_clusters = 3
cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(data_array.T, c=n_clusters, m=2, error=0.005, maxiter=1000, init=None)

# Assign cluster labels based on maximum membership
cluster_labels = np.argmax(u, axis=0)  # Labels correspond to original sample order

# Verify label assignment to ensure they match index positions
assert len(cluster_labels) == len(df_selected_scaled_diabetes), "Mismatch in label assignment!"

# Assign labels to all dataframes
df_selected_scaled_high_bp["Health_Label"] = cluster_labels
df_selected_high_bp["Health_Label"] = cluster_labels
df_with_food_names['Health_Label_HighBP'] = cluster_labels

# Ensure data is in correct shape (samples, features) before clustering
data_array = df_pca2.to_numpy()  # ✅ No transposition

# Apply Fuzzy C-Means clustering
n_clusters = 3
cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(data_array.T, c=n_clusters, m=2, error=0.005, maxiter=1000, init=None)

# Assign cluster labels based on maximum membership
cluster_labels = np.argmax(u, axis=0)  # Labels correspond to original sample order

# Verify label assignment to ensure they match index positions
assert len(cluster_labels) == len(df_selected_scaled_diabetes), "Mismatch in label assignment!"

# Assign labels to all dataframes
df_selected_scaled_low_bp["Health_Label"] = cluster_labels
df_selected_low_bp["Health_Label"] = cluster_labels
df_with_food_names['Health_Label_LowBP'] = cluster_labels

"""# Final Labeled Data Export"""

df_with_food_names.head()

df_with_food_names.to_csv('Labeled_Data.csv',index = False)

df_with_food_names.to_excel('Labeled_Data.xlsx',index = False)













"""Streamlit"""
import streamlit as st

with open("streamlit_app.py", "w") as f:
    f.write('''
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
    st.markdown("- " + "\n- ".join(avoid_list))

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
''')


