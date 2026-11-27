import os
import requests
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Iris Species Classifier",
    page_icon="🌸",
    layout="centered",
)

# API endpoint configuration
# Inside Docker Compose, API_URL defaults to http://api:8000
# For local execution without Docker, users can set API_URL=http://localhost:8000
API_BASE_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"

# Header and Introduction
st.title("🌸 Iris Flower Species Classifier")
st.markdown(
    """
    This interactive application predicts the species of an **Iris** flower 
    based on its morphological measurements using a machine learning model 
    served by **FastAPI** and logged to **PostgreSQL**.
    """
)

st.markdown("---")

# Feature Input Section
st.subheader("📏 Enter Flower Measurements (in cm)")

col1, col2 = st.columns(2)

with col1:
    sepal_length = st.number_input(
        "Sepal Length (cm)",
        min_value=0.0,
        max_value=15.0,
        value=5.1,
        step=0.1,
        help="Length of the flower's sepal in centimetres (typical range: 4.3 - 7.9 cm)",
    )
    sepal_width = st.number_input(
        "Sepal Width (cm)",
        min_value=0.0,
        max_value=10.0,
        value=3.5,
        step=0.1,
        help="Width of the flower's sepal in centimetres (typical range: 2.0 - 4.4 cm)",
    )

with col2:
    petal_length = st.number_input(
        "Petal Length (cm)",
        min_value=0.0,
        max_value=15.0,
        value=1.4,
        step=0.1,
        help="Length of the flower's petal in centimetres (typical range: 1.0 - 6.9 cm)",
    )
    petal_width = st.number_input(
        "Petal Width (cm)",
        min_value=0.0,
        max_value=10.0,
        value=0.2,
        step=0.1,
        help="Width of the flower's petal in centimetres (typical range: 0.1 - 2.5 cm)",
    )

st.markdown("---")

# Predict Action
if st.button("🔍 Predict Species", type="primary", use_container_width=True):
    # Construct payload conforming exactly to FastAPI's PredictRequest schema
    payload = {
        "feature_array": [
            float(sepal_length),
            float(sepal_width),
            float(petal_length),
            float(petal_width),
        ]
    }

    with st.spinner("Contacting FastAPI inference service..."):
        try:
            response = requests.post(
                PREDICT_ENDPOINT,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                prediction_info = result.get("prediction", {})
                
                # Note: api/main.py returns 'class_id ' with a trailing space
                class_id = prediction_info.get("class_id ", prediction_info.get("class_id", "N/A"))
                class_name = prediction_info.get("class_name", "Unknown").capitalize()

                # Visual feedback based on species
                species_icons = {
                    "Setosa": "🌺",
                    "Versicolor": "🌷",
                    "Virginica": "🪻",
                }
                icon = species_icons.get(class_name, "🌸")

                st.success(f"### {icon} Predicted Species: **Iris {class_name}**")
                
                # Display details in an organized metrics card
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(label="Species Name", value=f"Iris {class_name}")
                with res_col2:
                    st.metric(label="Class ID", value=str(class_id))

                st.info(
                    f"✅ Prediction completed and recorded to PostgreSQL database."
                )

            elif response.status_code == 422:
                st.error("Validation Error: The input values did not match the expected API format.")
                st.json(response.json())
            else:
                st.error(f"API Error (HTTP {response.status_code}): {response.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                f"🚨 **Connection Error**: Unable to reach the API service at `{PREDICT_ENDPOINT}`.\n\n"
                "Please verify that the FastAPI container is running and accessible."
            )
        except requests.exceptions.Timeout:
            st.error(
                f"⏱️ **Timeout Error**: The API service at `{PREDICT_ENDPOINT}` took too long to respond."
            )
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)}")

# Sidebar information
with st.sidebar:
    st.header("⚙️ System Status")
    st.write(f"**Target API:** `{API_BASE_URL}`")
    st.write(f"**Endpoint:** `{PREDICT_ENDPOINT}`")
    st.markdown("---")
    st.markdown(
        """
        ### 📚 Species Reference
        - **Class 0:** Iris Setosa
        - **Class 1:** Iris Versicolor
        - **Class 2:** Iris Virginica
        
        ### 🧪 Quick Presets (cm)
        - **Setosa:** `[5.1, 3.5, 1.4, 0.2]`
        - **Versicolor:** `[7.0, 3.2, 4.7, 1.4]`
        - **Virginica:** `[6.3, 3.3, 6.0, 2.5]`
        """
    )
