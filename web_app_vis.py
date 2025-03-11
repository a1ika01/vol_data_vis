import streamlit as st
import pandas as pd
import os
from task_1 import GenerateVolatilityGrids
from task_2 import VisualiseCarryPerTenor


st.set_page_config(page_title="data visualiser", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main-container {
        background-color: #f4f4f4;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 16px;
        display: block;
        margin: 0 auto;
    }
    .stSelectbox label {
        font-weight: bold;
        font-size: 16px;
    }
    .stHeader {
        color: #007BFF;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
    }
    .stImage {
        display: flex;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for File Upload
st.sidebar.title("📂 Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Select a CSV file", type=["csv"], help="Upload a volatility data file for processing.")

if not uploaded_file:
    st.markdown("### Please upload volatility csv", unsafe_allow_html=True)

if uploaded_file:
    # Save uploaded file temporarily
    file_path = "vol_data.csv"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    generator = GenerateVolatilityGrids()
    available_ccys = list(generator.get_existing_ccys())
    
    # Ensure at least three unique currencies for default selection
    default_currencies = available_ccys[:3] if len(available_ccys) >= 3 else available_ccys
    
    # Volatility Analysis
    st.markdown("### Task 1 (volatility grids)", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    selected_ccy1 = col1.selectbox("Select Currency pair 1", available_ccys, index=0)
    selected_ccy2 = col2.selectbox("Select Currency pair 2", available_ccys, index=1 if len(available_ccys) > 1 else 0)
    selected_ccy3 = col3.selectbox("Select Currency pair 3", available_ccys, index=2 if len(available_ccys) > 2 else 0)
    
    for i, (col, selected_ccy) in enumerate(zip([col1, col2, col3], [selected_ccy1, selected_ccy2, selected_ccy3])):
        if selected_ccy:
            ccy_png = selected_ccy.replace("/", "|") + ".png"
            if os.path.exists(ccy_png):
                col.image(ccy_png, caption=f"Volatility Grids for {selected_ccy}",  use_container_width=True)
                col.download_button("📥 Download PNG", data=open(ccy_png, "rb").read(), file_name=ccy_png, key=f"vol_download_{i}")
            else:
                generator.run([selected_ccy])
                col.image(ccy_png, caption=f"Volatility Grids for {selected_ccy}",  use_container_width=True)
                col.download_button("📥 Download PNG", data=open(ccy_png, "rb").read(), file_name=ccy_png, key=f"vol_download_{i}")

    # Carry Tables for G10 Currencies
    st.markdown("### Task 2 (carry data by tenor)", unsafe_allow_html=True)
    carry_visualizer = VisualiseCarryPerTenor()
    g10_ccy_options = carry_visualizer.get_g10_ccys()
    col1, col2, col3 = st.columns(3)
    selected_g10_1 = col1.selectbox("Select G10 Currency pair 1", g10_ccy_options, index=0)
    selected_g10_2 = col2.selectbox("Select G10 Currency pair 2", g10_ccy_options, index=1 if len(g10_ccy_options) > 1 else 0)
    selected_g10_3 = col3.selectbox("Select G10 Currency pair 3", g10_ccy_options, index=2 if len(g10_ccy_options) > 2 else 0)
    
    for i, (col, selected_g10) in enumerate(zip([col1, col2, col3], [selected_g10_1, selected_g10_2, selected_g10_3])):
        if selected_g10:
            carry_png = selected_g10.replace("/", "|") + "_carry.png"
            if os.path.exists(carry_png):
                col.image(carry_png, caption=f"Carry Table for {selected_g10}",  use_container_width=True)
                col.download_button("📥 Download PNG", data=open(carry_png, "rb").read(), file_name=carry_png, key=f"carry_vol_download_{i}")
            else:
                carry_visualizer.run()
                col.image(carry_png, caption=f"Carry Table for {selected_g10}",  use_container_width=True)
                col.download_button("📥 Download PNG", data=open(carry_png, "rb").read(), file_name=carry_png, key=f"carry_vol_download_{i}")

st.markdown("""
    <div style="text-align: center; padding-top: 20px; font-size: 12px; color: grey;">
        By Alex C
    </div>
""", unsafe_allow_html=True)
