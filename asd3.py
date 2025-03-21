import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Portfolio Based on Correlation Weighting")

# ระบุ path ของไฟล์ CSV (ปรับแก้ตามตำแหน่งจริง)
csv_path = "./output_folder/merged_rolling_corr.csv"

# อ่านไฟล์ CSV พร้อม parse คอลัมน์ 'date_only' ให้เป็น datetime
df = pd.read_csv(csv_path, parse_dates=['date_only'])

st.subheader("Data Preview")
st.dataframe(df.head())

# ให้ผู้ใช้ระบุ threshold (เช่น ค่า ts) ที่ใช้กรองหุ้น (default 0.3)
threshold = st.number_input("Enter threshold for Rolling Correlation (ts)", value=0.3, step=0.05, format="%.2f")

st.write("Calculating portfolio for each 1st day of the month...")

# กรองเฉพาะข้อมูลของวันที่ 1 ของทุกเดือน
df_first = df[df['date_only'].dt.day == 1].copy()

if df_first.empty:
    st.warning("ไม่พบข้อมูลในวันที่ 1 ของเดือน")
else:
    portfolio_results = []  # เก็บผลลัพธ์ของพอร์ตแต่ละวัน
    # วนลูปสำหรับแต่ละวันที่ 1 (group โดย 'date_only')
    for date, group in df_first.groupby('date_only'):
        st.markdown(f"### Date: {date.date()}")
        # กรองหุ้นที่มี rolling_corr (หรือ ts) > threshold
        group_valid = group[group['rolling_corr'] > threshold].copy()
        
        if group_valid.empty:
            st.write("ไม่พบหุ้นที่ผ่านเงื่อนไข threshold ในวันนี้")
        else:
            # ถ้ามีหุ้นเกิน 10 ตัว ให้เลือก Top 10 โดยเรียงจาก rolling_corr มากไปน้อย
            if len(group_valid) > 10:
                group_valid = group_valid.sort_values('rolling_corr', ascending=False).head(10)
            else:
                group_valid = group_valid.sort_values('rolling_corr', ascending=False)
            
            # คำนวณน้ำหนักให้กับแต่ละหุ้น (น้ำหนัก = rolling_corr / ผลรวม rolling_corr ของหุ้นที่ผ่านเงื่อนไข)
            total_corr = group_valid['rolling_corr'].sum()
            group_valid['weight'] = group_valid['rolling_corr'] / total_corr
            
            # เพิ่มคอลัมน์วันที่ของพอร์ตเพื่อเก็บผลลัพธ์รวม
            group_valid['portfolio_date'] = date
            
            st.subheader("Portfolio Weights")
            st.dataframe(group_valid[['symbol', 'rolling_corr', 'weight']])
            
            # Plot กราฟ Bar แสดงน้ำหนักของแต่ละหุ้นในวันนั้น
            fig = px.bar(group_valid, x='symbol', y='weight',
                         title=f"Portfolio Weights on {date.date()}",
                         labels={'symbol': 'Stock Symbol', 'weight': 'Weight'})
            st.plotly_chart(fig, use_container_width=True)
            
            portfolio_results.append(group_valid)
    
    # รวมผลลัพธ์ของทุกวันเข้าเป็น DataFrame เดียว
    if portfolio_results:
        portfolio_df = pd.concat(portfolio_results)
        st.subheader("Combined Portfolio Results")
        st.dataframe(portfolio_df[['portfolio_date', 'symbol', 'rolling_corr', 'weight']])
