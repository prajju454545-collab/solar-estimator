import math
import streamlit as st
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
    "requested_size": "✏️ Requested System Size",
    "actual_size": "🔧 Actual Installed Size (after panels)",
    "base_cost": "🪙 Estimated Cost",
    "subsidy": "💸 Subsidy",
    "final_cost": "🧾 Final Cost after Subsidy",
    "panels": "🔌 Panels Required (525W)",
    "generation": "☀️ Monthly Generation",
    "savings": "💰 Annual Savings",
    "roi": "📈 Simple ROI",
    "download": "📄 Download Estimate as PDF",
    "buyback_income": "💵 Buyback Income (Surplus Units)",
    "import_cost": "🧾 Grid Import Cost (Deficit Units)",
    "future_savings": "🌞 20-Year Savings (with price escalation)"
}

if language == "Kannada":
    text.update({
        "monthly_units": "ತಿಂಗಳಿಗೆ ಸರಾಸರಿ ಬಳಕೆ (ಯುನಿಟ್‌ಗಳಲ್ಲಿ) ನಮೂದಿಸಿ",
        "manual_kw": "ಅಥವಾ ನೀವು ಬಯಸುವ ಸಿಸ್ಟಂ ಗಾತ್ರ (kW) ನಮೂದಿಸಿ",
        "apply_subsidy": "PM ಸೂರ್ಯ ಗೃಹ ಸಬ್ಸಿಡಿಗೆ ಅರ್ಜಿ ಹಾಕಿದೀರಿ?",
        "estimate_result": "📊 ಅಂದಾಜು ಫಲಿತಾಂಶ:",
        "requested_size": "✏️ ವಿನಂತಿಸಿದ ಸಿಸ್ಟಂ ಗಾತ್ರ",
        "actual_size": "🔧 ಸ್ಥಾಪಿತ ಗಾತ್ರ (ಪ್ಯಾನೆಲ್‌ಗಳ ನಂತರ)",
        "base_cost": "🪙 ಅಂದಾಜಿತ ವೆಚ್ಚ",
        "subsidy": "💸 ಸಬ್ಸಿಡಿ",
        "final_cost": "🧾 ಸಬ್ಸಿಡಿಯ ನಂತರದ ವೆಚ್ಚ",
        "panels": "🔌 ಬೇಕಾಗುವ ಪ್ಯಾನೆಲ್‌ಗಳು (525W)",
        "generation": "☀️ ತಿಂಗಳ ಉತ್ಪಾದನೆ",
        "savings": "💰 ವಾರ್ಷಿಕ ಉಳಿತಾಯ",
        "roi": "📈 ಹೂಡಿಕೆ ಮರುಪಾವತಿ",
        "download": "📄 PDF ಆಗಿ ಡೌನ್ಲೋಡ್ ಮಾಡಿ",
        "buyback_income": "💵 ಮಾರಾಟ ಆದಾಯ",
        "import_cost": "🧾 ಜಾಲಿಸಿದ ವಿದ್ಯುತ್ ಖರ್ಚು",
        "future_savings": "🌞 20 ವರ್ಷದ ಉಳಿತಾಯ (ಬೆಲೆ ಏರಿಕೆ ಒಳಗೊಂಡು)"
    })

# --- Inputs ---
monthly_units = st.number_input(text["monthly_units"], min_value=0, step=10, value=300)
suggested_kw = max(0.5, round(monthly_units / 126, 2))  # 1 kW ~126 units/month
requested_kw = st.number_input(text["manual_kw"], value=suggested_kw, min_value=0.5, step=0.1)
apply_subsidy = st.checkbox(text["apply_subsidy"])

# --- Constants ---
panel_watt = 525
cost_per_kw = 65000
daily_gen_per_kw = 4.2
electricity_rate = 6.2
tax_rate = 0.09
total_rate = electricity_rate * (1 + tax_rate)
price_increase_rate = 0.05  # 5% per year escalation

# --- Panel & Size ---
panels_required = math.ceil((requested_kw * 1000) / panel_watt)
actual_kw = round((panels_required * panel_watt) / 1000, 3)

# --- Cost & Subsidy ---
base_cost = actual_kw * cost_per_kw
if apply_subsidy:
    if panels_required <= 2:
        subsidy = 30000
    elif panels_required <= 4:
        subsidy = 60000
    else:
        subsidy = 78000
else:
    subsidy = 0

final_cost = base_cost - subsidy

# --- Generation & Annual Values ---
monthly_generation = round(actual_kw * daily_gen_per_kw * 30, 1)
annual_generation = round(monthly_generation * 12, 1)

# --- Buyback ---
if apply_subsidy:
    if actual_kw <= 2:
        buyback_rate = 2.3
    elif actual_kw <= 3:
        buyback_rate = 2.48
    else:
        buyback_rate = 2.93
else:
    buyback_rate = 3.86

surplus_units = round(max(0, monthly_generation - monthly_units), 1)
deficit_units = round(max(0, monthly_units - monthly_generation), 1)
buyback_income = round(surplus_units * buyback_rate * 12, 2)
import_cost = round(deficit_units * total_rate * 12, 2)

self_consumed_monthly = monthly_generation - surplus_units
annual_savings = round((self_consumed_monthly * total_rate * 12) + buyback_income, 2)
roi_years = round(final_cost / annual_savings, 2) if annual_savings > 0 else float('inf')

# --- 20-Year Savings Calculation ---
future_savings = 0
current_annual_savings = annual_savings
for _ in range(20):
    future_savings += current_annual_savings
    current_annual_savings *= (1 + price_increase_rate)
future_savings = round(future_savings, 2)

# --- Output ---
st.subheader(text["estimate_result"])
st.write(f"{text['requested_size']}: **{requested_kw} kW**")
st.write(f"{text['actual_size']}: **{actual_kw} kW** ({panels_required} panels)")
st.write(f"{text['base_cost']}: ₹{int(base_cost):,}")

if apply_subsidy:
    st.write(f"{text['subsidy']}: ₹{int(subsidy):,}")
    st.write(f"{text['final_cost']}: ₹{int(final_cost):,}")
else:
    st.write("Subsidy: Not applied")

st.write(f"{text['generation']}: **{monthly_generation} units/month**")
st.write(f"⚡ Consumption: **{monthly_units} units/month**")

if surplus_units > 0:
    st.write(f"📤 Surplus: {surplus_units} units/month")
    st.write(f"{text['buyback_income']}: ₹{int(buyback_income):,}/year (₹{buyback_rate}/unit)")
if deficit_units > 0:
    st.write(f"📥 Deficit: {deficit_units} units/month")
    st.write(f"{text['import_cost']}: ₹{int(import_cost):,}/year")

st.write(f"{text['savings']}: ₹{int(annual_savings):,}/year")
st.write(f"{text['future_savings']}: ₹{int(future_savings):,} (over 20 years)")
st.write(f"{text['roi']}: **{roi_years} years**")

# --- PDF Export ---
st.subheader(text["download"])
if st.button("Export PDF"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 800, "Solar Rooftop Estimation Summary")
    c.setFont("Helvetica", 11)
    y = 780
    lines = [
        f"Requested size: {requested_kw} kW",
        f"Actual installed size: {actual_kw} kW ({panels_required} panels)",
        f"Base cost: ₹{int(base_cost):,}",
        f"Subsidy: ₹{int(subsidy):,}" if apply_subsidy else "Subsidy: Not applied",
        f"Final cost: ₹{int(final_cost):,}" if apply_subsidy else "",
        f"Monthly generation: {monthly_generation} units",
        f"Monthly consumption: {monthly_units} units",
        f"Annual savings: ₹{int(annual_savings):,}",
        f"20-year projected savings (with escalation): ₹{int(future_savings):,}",
        f"ROI: {roi_years} years"
    ]
    for line in lines:
        c.drawString(100, y, line)
        y -= 18
    c.save()
    buffer.seek(0)
    st.download_button(
        label="📥 Download PDF",
        data=buffer,
        file_name="solar_estimate.pdf",
        mime="application/pdf"
    )
