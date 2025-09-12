import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- Setup ---
st.set_page_config(page_title="Solar Estimator", page_icon="☀️")
st.title("☀️ Solar Rooftop Estimator - PM Surya Ghar")

# --- Language Toggle ---
language = st.radio("Select Language", ["English", "Kannada"])

text = {
    "monthly_units": "Enter your average monthly electricity consumption (in units)",
    "manual_kw": "Or enter your desired system size (in kW)",
    "apply_subsidy": "Apply for PM Surya Ghar Subsidy?",
    "estimate_result": "📊 Estimate Result:",
    "recommended_size": "✅ Recommended System Size",
    "base_cost": "🪙 Estimated Cost",
    "subsidy": "💸 Subsidy",
    "final_cost": "🧾 Final Cost after Subsidy",
    "panels": "🔌 Panels Required (525W)",
    "generation": "☀️ Monthly Generation",
    "savings": "💰 Annual Savings",
    "roi": "📈 Simple ROI",
    "download": "📄 Download Estimate as PDF",
    "buyback_income": "💵 Buyback Income (Surplus Units)",
    "import_cost": "🧾 Grid Import Cost (Deficit Units)"
}

if language == "Kannada":
    text.update({
        "monthly_units": "ತಿಂಗಳಿಗೆ ಸರಾಸರಿ ವಿದ್ಯುತ್ಬಳಕೆ (ಯುನಿಟ್ಲ್ಗಳ್ಲಿ) ನಮೂದಿಸಿ",
        "manual_kw": "ಅಥವಾ ನೀವು ಬಯಸುವ ಸಿಸ್ಟಂ ಗಾತ್ರವನ್ನನ್ನು (ಕ್W)ನಮೂದಿಸಿ",
        "apply_subsidy": "PM ಸೂರ್ಯ ಗಿಹ್ರ ಸಬ್ಸಿಡಿಗೆ ಅರ್ಜಿ ಹಾಕೆದೆಯೇ?",
        "estimate_result": "📊 ಅಂದಾಜು ಫಲಿತಾಂಶ:",
        "recommended_size": "✅ ಶಿಫಾರಸು ಮಾಡಿದ ವ್ಯವಸ್ಥೆಯ ಗಾತ್ರ",
        "base_cost": "🪙 ಅಂದಾಜಿತ ವೆಚ",
        "subsidy": "💸 ಸಬ್ಸಿಡಿ",
        "final_cost": "🧾 ಸಬ್ಸಿಡಿಯ ನಂತರದ ವೆಚ",
        "panels": "🔌 ಬೇಕಾಗುವ ಪ್ಯಾನೆಲ್ಗಳು (ವಾಟ್ಟ್ಸ್ 525W)",
        "generation": "☀️ ತಿಂಗಳ ಉತ್ಪಾದನೆ",
        "savings": "💰 ವಾರ್ಷಿಕ ಉಳಿತಾಯ",
        "roi": "📈 ಹೂಡಿಕೆಯ ಮರುಪಾವತಿ ಅವಧಿ",
        "download": "📄 PDF ರೂಪದಲ್ಲಿ ಡೌನ್ಲೋಡ್ ಮಾಡಿ",
        "buyback_income": "💵 ಜಾಲಾಡಿದ ವಿದ್ಯುತ್ತಿಗಾಗಿ ಆದಾಯ",
        "import_cost": "🧾 ಗ್ರಹ ಬಳಕೆಗಾಗಿ ಖರ್ಚ"
    })

# --- Inputs ---
monthly_units = st.number_input(text["monthly_units"], min_value=10, step=10)
suggested_kw = max(0.5, round(monthly_units / 126, 2))
system_kw_input = st.number_input(text["manual_kw"], value=suggested_kw, min_value=0.5, step=0.1)
apply_subsidy = st.checkbox(text["apply_subsidy"])

# --- Constants ---
panel_watt = 525
cost_per_kw = 65000
daily_gen_per_kw = 4.2
electricity_rate = 5.9 + 0.3  # 6.2 ₹/unit
tax_rate = 0.09
total_rate = electricity_rate * (1 + tax_rate)  # ~₹6.76

# --- Calculations ---
# Find number of panels first
panels_required = round((system_kw_input * 1000) / panel_watt)

# Recalculate exact system size from panels (to match subsidy slabs correctly)
system_kw = round((panels_required * panel_watt) / 1000, 3)
base_cost = system_kw * cost_per_kw

# Subsidy Slab (based on actual system size from panels)
subsidy = 0
if apply_subsidy:
    if system_kw <= 1:
        subsidy = 30000
    elif system_kw > 1 and system_kw <= 2:
        subsidy = 60000
    elif system_kw > 2 and system_kw <= 3:
        subsidy = 78000
    else:
        subsidy = 78000
final_cost = base_cost - subsidy

monthly_generation = round(system_kw * daily_gen_per_kw * 30, 1)
annual_generation = monthly_generation * 12

# --- Surplus/Deficit Logic ---
buyback_rate = 2.93  # Default
if apply_subsidy:
    if system_kw <= 2:
        buyback_rate = 2.3
    elif system_kw <= 3:
        buyback_rate = 2.48
    else:
        buyback_rate = 2.93
else:
    buyback_rate = 3.86

surplus_units = round(max(0, monthly_generation - monthly_units), 1)
deficit_units = round(max(0, monthly_units - monthly_generation), 1)

buyback_income = round(surplus_units * buyback_rate * 12, 2)
import_cost = round(deficit_units * total_rate * 12, 2)

annual_savings = round((monthly_generation - surplus_units) * total_rate * 12, 2) + buyback_income
roi_years = round(final_cost / annual_savings, 2)

# --- Output ---
st.subheader(text["estimate_result"])
st.write(f"{text['recommended_size']}: **{system_kw} kW**")
st.write(f"{text['base_cost']}: ₹{int(base_cost):,}")
if apply_subsidy:
    st.write(f"{text['subsidy']}: ₹{int(subsidy):,}")
    st.write(f"{text['final_cost']}: ₹{int(final_cost):,}")
st.write(f"{text['panels']}: **{panels_required}**")
st.write(f"{text['generation']}: **{monthly_generation} units/month**")
st.write(f"⚡ Consumption: **{monthly_units} units/month**")

if surplus_units > 0:
    st.write(f"📤 Surplus: {surplus_units} units/month")
    st.write(f"{text['buyback_income']}: ₹{int(buyback_income):,}/year")
if deficit_units > 0:
    st.write(f"📥 Deficit: {deficit_units} units/month")
    st.write(f"{text['import_cost']}: ₹{int(import_cost):,}/year")

st.write(f"{text['savings']}: ₹{int(annual_savings):,}")
st.write(f"{text['roi']}: **{roi_years} years**")
