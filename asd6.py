<<<<<<< HEAD
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Portfolio Status, Performance & Comparison Dashboard")

# ระบุ path ของไฟล์ CSV
csv_path = "./output_folder/merged_rolling_corr_with_return.csv"
filtered_csv_path = "./output_date/Cell output 2_filtered.csv"  # rebalancing dates
dji_csv_path = "./index_date/DJI_filtered_return.csv"              # Dow30 data

# อ่านข้อมูลจาก merged_rolling_corr_with_return.csv
df = pd.read_csv(csv_path, parse_dates=['date_only'])
if 'return' not in df.columns:
    st.error("ไฟล์ merged_rolling_corr_with_return.csv ต้องมีคอลัมน์ 'return'")
    st.stop()

# อ่าน rebalancing dates จาก 2_filtered.csv (สมมุติว่ามีคอลัมน์ 'date')
df_filter = pd.read_csv(filtered_csv_path, parse_dates=['date'])
if df_filter.empty:
    st.error("ไฟล์ 2_filtered.csv ไม่มีข้อมูล rebalancing dates")
    st.stop()

# อ่านข้อมูล Dow30 จาก DJI_filtered.csv โดย parse คอลัมน์ 'date'
dji_df = pd.read_csv(dji_csv_path, parse_dates=['date'])
if dji_df.empty:
    st.error("ไฟล์ DJI_filtered.csv ไม่มีข้อมูล")
    st.stop()

# ตรวจสอบและคำนวณ daily return สำหรับ Dow30 ถ้ายังไม่มีคอลัมน์ 'return'
if 'return' not in dji_df.columns:
    dji_df.sort_values('date', inplace=True)
    dji_df['return'] = dji_df['close'].pct_change().fillna(0)

st.subheader("Data Preview: Merged Rolling Correlation")
st.dataframe(df.head())

st.subheader("Data Preview: Rebalancing Dates")
st.dataframe(df_filter.head())

st.subheader("Data Preview: Dow30 Data")
st.dataframe(dji_df.head())

# ให้ผู้ใช้ระบุ threshold สำหรับ rolling_corr
threshold = st.number_input("Enter threshold for Rolling Correlation (ts)", value=0.3, step=0.05, format="%.2f")

# ใช้วันที่จาก df_filter เป็น rebalancing dates
rebal_dates = sorted(df_filter['date'].unique())
if not rebal_dates:
    st.warning("ไม่พบ rebalancing dates ในไฟล์ 2_filtered.csv")
    st.stop()

st.subheader("Portfolio Analysis Based on Rebalancing Dates")
portfolio_summary = []  # เก็บ portfolio composition ของแต่ละ rebalancing date
rebal_period_returns = []  # เก็บผลตอบแทนของแต่ละ period (portfolio)

# คำนวณผลตอบแทนของแต่ละ rebalancing period สำหรับ portfolio
for i, entry_date in enumerate(rebal_dates):
    st.markdown(f"### Rebalancing Date: {entry_date.date()}")
    
    # ดึงข้อมูลในวัน entry_date จาก df
    group = df[df['date_only'] == entry_date].copy()
    if group.empty:
        st.write("ไม่พบข้อมูลในวันที่นี้")
        continue

    # กรองหุ้นที่มี rolling_corr > threshold
    group_valid = group[group['rolling_corr'] > threshold].copy()
    if group_valid.empty:
        st.write("ในวันนี้ไม่มีหุ้นที่ผ่านเงื่อนไข threshold")
        continue

    # เลือก Top 10 หากมีหุ้นมากกว่า 10 ตัว
    group_valid = group_valid.sort_values('rolling_corr', ascending=False)
    if len(group_valid) > 10:
        group_valid = group_valid.head(10)
    
    # คำนวณน้ำหนักของแต่ละหุ้นในพอร์ต (normalize ค่า rolling_corr)
    total_corr = group_valid['rolling_corr'].sum()
    group_valid['weight'] = group_valid['rolling_corr'] / total_corr
    
    group_valid = group_valid[['symbol', 'rolling_corr', 'weight']].assign(portfolio_date=entry_date)
    portfolio_summary.append(group_valid)
    
    st.markdown("**Portfolio Weights**")
    st.dataframe(group_valid)
    
    fig_weight = px.bar(group_valid,
                        x='symbol',
                        y='weight',
                        title=f"Portfolio Allocation on {entry_date.date()}",
                        labels={'symbol': 'Stock Symbol', 'weight': 'Weight'})
    st.plotly_chart(fig_weight, use_container_width=True)
    
    # กำหนด exit_date ของ period นี้
    if i + 1 < len(rebal_dates):
        exit_date = rebal_dates[i+1]
    else:
        exit_date = df['date_only'].max()  # ใช้วันที่สุดท้ายใน df
    st.write(f"คำนวณผลตอบแทนระหว่าง {entry_date.date()} ถึง {exit_date.date()}")
    
    # ดึงข้อมูลผลตอบแทนของหุ้นใน period นี้จาก df
    period_data = df[(df['date_only'] >= entry_date) & (df['date_only'] < exit_date)]
    
    port_return = 0.0
    for symbol in group_valid['symbol']:
        stock_data = period_data[period_data['symbol'] == symbol]
        if stock_data.empty:
            stock_cum_return = 0.0
        else:
            stock_cum_return = (1 + stock_data['return']).prod() - 1
        weight = group_valid.loc[group_valid['symbol'] == symbol, 'weight'].values[0]
        port_return += weight * stock_cum_return
    st.write(f"ผลตอบแทนของพอร์ตใน period นี้: {port_return:.2%}")
    rebal_period_returns.append({'entry_date': entry_date, 'exit_date': exit_date, 'period_return': port_return})

# รวม portfolio composition ทั้งหมด
if portfolio_summary:
    portfolio_df = pd.concat(portfolio_summary)
    st.subheader("Combined Portfolio Overview")
    st.dataframe(portfolio_df.sort_values('portfolio_date'))
    
    # คำนวณ cumulative return ของพอร์ตตลอดช่วง rebalancing
    period_returns_df = pd.DataFrame(rebal_period_returns).sort_values('entry_date')
    period_returns_df['cum_return'] = (1 + period_returns_df['period_return']).cumprod()
    
    st.subheader("Portfolio Performance Over Rebalancing Periods")
    st.dataframe(period_returns_df)
    
    fig_perf = px.line(period_returns_df, x='entry_date', y='cum_return',
                       title="Cumulative Return of the Portfolio Over Time",
                       labels={'entry_date': 'Rebalancing Date', 'cum_return': 'Cumulative Return'})
    st.plotly_chart(fig_perf, use_container_width=True)
    
    final_cum_return = period_returns_df['cum_return'].iloc[-1]
    st.write(f"**ผลตอบแทนสะสมของพอร์ตทั้งหมด:** {final_cum_return:.2%}")
    
    # --- เปรียบเทียบกับ Dow30 ---
    st.subheader("Comparison: Portfolio vs Dow30")
    # คำนวณผลตอบแทนของ Dow30 ในแต่ละ rebalancing period
    dji_df.sort_values('date', inplace=True)
    
    dji_period_returns = []
    for i, entry_date in enumerate(rebal_dates):
        if i + 1 < len(rebal_dates):
            exit_date = rebal_dates[i+1]
        else:
            exit_date = dji_df['date'].max()
        period_dji = dji_df[(dji_df['date'] >= entry_date) & (dji_df['date'] < exit_date)]
        if period_dji.empty:
            dji_return = 0.0
        else:
            dji_return = (1 + period_dji['return']).prod() - 1
        dji_period_returns.append({'entry_date': entry_date, 'exit_date': exit_date, 'dji_period_return': dji_return})
    
    dji_returns_df = pd.DataFrame(dji_period_returns).sort_values('entry_date')
    dji_returns_df['dji_cum_return'] = (1 + dji_returns_df['dji_period_return']).cumprod()
    
    # Merge portfolio and Dow30 performance for comparison
    performance_df = period_returns_df.merge(dji_returns_df[['entry_date', 'dji_cum_return']], on='entry_date', how='left')
    st.dataframe(performance_df)
    
    fig_compare = px.line(performance_df, x='entry_date', y=['cum_return', 'dji_cum_return'],
                          title="Cumulative Return: Portfolio vs Dow30",
                          labels={'entry_date': 'Rebalancing Date', 'value': 'Cumulative Return'},
                          markers=True)
    st.plotly_chart(fig_compare, use_container_width=True)
    
    final_dji_return = performance_df['dji_cum_return'].iloc[-1]
    st.write(f"**ผลตอบแทนสะสมของ Dow30:** {final_dji_return:.2%}")
    st.write(f"**ผลตอบแทนสะสมของ cumre:** {final_cum_return:.2%}")
=======
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Portfolio Status, Performance & Comparison Dashboard")

# ระบุ path ของไฟล์ CSV
csv_path = "./output_folder/merged_rolling_corr_with_return.csv"
filtered_csv_path = "./output_date/Cell output 2_filtered_t.csv"  # rebalancing dates
dji_csv_path = "./index_date/DJI_filtered_return.csv"              # Dow30 data

# อ่านข้อมูลจาก merged_rolling_corr_with_return.csv
df = pd.read_csv(csv_path, parse_dates=['date_only'])
if 'return' not in df.columns:
    st.error("ไฟล์ merged_rolling_corr_with_return.csv ต้องมีคอลัมน์ 'return'")
    st.stop()

# อ่าน rebalancing dates จาก 2_filtered.csv (สมมุติว่ามีคอลัมน์ 'date')
df_filter = pd.read_csv(filtered_csv_path, parse_dates=['date'])
if df_filter.empty:
    st.error("ไฟล์ 2_filtered.csv ไม่มีข้อมูล rebalancing dates")
    st.stop()

# อ่านข้อมูล Dow30 จาก DJI_filtered.csv โดย parse คอลัมน์ 'date'
dji_df = pd.read_csv(dji_csv_path, parse_dates=['date'])
if dji_df.empty:
    st.error("ไฟล์ DJI_filtered.csv ไม่มีข้อมูล")
    st.stop()

# ตรวจสอบและคำนวณ daily return สำหรับ Dow30 ถ้ายังไม่มีคอลัมน์ 'return'
if 'return' not in dji_df.columns:
    dji_df.sort_values('date', inplace=True)
    dji_df['return'] = dji_df['close'].pct_change().fillna(0)

st.subheader("Data Preview: Merged Rolling Correlation")
st.dataframe(df.head())

st.subheader("Data Preview: Rebalancing Dates")
st.dataframe(df_filter.head())

st.subheader("Data Preview: Dow30 Data")
st.dataframe(dji_df.head())

# ให้ผู้ใช้ระบุ threshold สำหรับ rolling_corr
threshold = st.number_input("Enter threshold for Rolling Correlation (ts)", value=0.3, step=0.05, format="%.2f")

# ใช้วันที่จาก df_filter เป็น rebalancing dates
rebal_dates = sorted(df_filter['date'].unique())
if not rebal_dates:
    st.warning("ไม่พบ rebalancing dates ในไฟล์ 2_filtered.csv")
    st.stop()

st.subheader("Portfolio Analysis Based on Rebalancing Dates")
portfolio_summary = []  # เก็บ portfolio composition ของแต่ละ rebalancing date
rebal_period_returns = []  # เก็บผลตอบแทนของแต่ละ period (portfolio)

# คำนวณผลตอบแทนของแต่ละ rebalancing period สำหรับ portfolio
for i, entry_date in enumerate(rebal_dates):
    st.markdown(f"### Rebalancing Date: {entry_date.date()}")
    
    # ดึงข้อมูลในวัน entry_date จาก df
    group = df[df['date_only'] == entry_date].copy()
    if group.empty:
        st.write("ไม่พบข้อมูลในวันที่นี้")
        continue

    # กรองหุ้นที่มี rolling_corr > threshold
    group_valid = group[group['rolling_corr'] > threshold].copy()
    if group_valid.empty:
        st.write("ในวันนี้ไม่มีหุ้นที่ผ่านเงื่อนไข threshold")
        continue

    # เลือก Top 10 หากมีหุ้นมากกว่า 10 ตัว
    group_valid = group_valid.sort_values('rolling_corr', ascending=False)
    if len(group_valid) > 10:
        group_valid = group_valid.head(10)
    
    # คำนวณน้ำหนักของแต่ละหุ้นในพอร์ต (normalize ค่า rolling_corr)
    total_corr = group_valid['rolling_corr'].sum()
    group_valid['weight'] = group_valid['rolling_corr'] / total_corr
    
    group_valid = group_valid[['symbol', 'rolling_corr', 'weight']].assign(portfolio_date=entry_date)
    portfolio_summary.append(group_valid)
    
    st.markdown("**Portfolio Weights**")
    st.dataframe(group_valid)
    
    fig_weight = px.bar(group_valid,
                        x='symbol',
                        y='weight',
                        title=f"Portfolio Allocation on {entry_date.date()}",
                        labels={'symbol': 'Stock Symbol', 'weight': 'Weight'})
    st.plotly_chart(fig_weight, use_container_width=True)
    
    # กำหนด exit_date ของ period นี้
    if i + 1 < len(rebal_dates):
        exit_date = rebal_dates[i+1]
    else:
        exit_date = df['date_only'].max()  # ใช้วันที่สุดท้ายใน df
    st.write(f"คำนวณผลตอบแทนระหว่าง {entry_date.date()} ถึง {exit_date.date()}")
    
    # ดึงข้อมูลผลตอบแทนของหุ้นใน period นี้จาก df
    period_data = df[(df['date_only'] >= entry_date) & (df['date_only'] < exit_date)]
    
    port_return = 0.0
    for symbol in group_valid['symbol']:
        stock_data = period_data[period_data['symbol'] == symbol]
        if stock_data.empty:
            stock_cum_return = 0.0
        else:
            stock_cum_return = (1 + stock_data['return']).prod() - 1
        weight = group_valid.loc[group_valid['symbol'] == symbol, 'weight'].values[0]
        port_return += weight * stock_cum_return
    st.write(f"ผลตอบแทนของพอร์ตใน period นี้: {port_return:.2%}")
    rebal_period_returns.append({'entry_date': entry_date, 'exit_date': exit_date, 'period_return': port_return})

# รวม portfolio composition ทั้งหมด
if portfolio_summary:
    portfolio_df = pd.concat(portfolio_summary)
    st.subheader("Combined Portfolio Overview")
    st.dataframe(portfolio_df.sort_values('portfolio_date'))
    
    # คำนวณ cumulative return ของพอร์ตตลอดช่วง rebalancing
    period_returns_df = pd.DataFrame(rebal_period_returns).sort_values('entry_date')
    period_returns_df['cum_return'] = (1 + period_returns_df['period_return']).cumprod()
    
    st.subheader("Portfolio Performance Over Rebalancing Periods")
    st.dataframe(period_returns_df)
    
    fig_perf = px.line(period_returns_df, x='entry_date', y='cum_return',
                       title="Cumulative Return of the Portfolio Over Time",
                       labels={'entry_date': 'Rebalancing Date', 'cum_return': 'Cumulative Return'})
    st.plotly_chart(fig_perf, use_container_width=True)
    
    final_cum_return = period_returns_df['cum_return'].iloc[-1]
    st.write(f"**ผลตอบแทนสะสมของพอร์ตทั้งหมด:** {final_cum_return:.2%}")
    
    # --- เปรียบเทียบกับ Dow30 ---
    st.subheader("Comparison: Portfolio vs Dow30")
    # คำนวณผลตอบแทนของ Dow30 ในแต่ละ rebalancing period
    dji_df.sort_values('date', inplace=True)
    
    dji_period_returns = []
    for i, entry_date in enumerate(rebal_dates):
        if i + 1 < len(rebal_dates):
            exit_date = rebal_dates[i+1]
        else:
            exit_date = dji_df['date'].max()
        period_dji = dji_df[(dji_df['date'] >= entry_date) & (dji_df['date'] < exit_date)]
        if period_dji.empty:
            dji_return = 0.0
        else:
            dji_return = (1 + period_dji['return']).prod() - 1
        dji_period_returns.append({'entry_date': entry_date, 'exit_date': exit_date, 'dji_period_return': dji_return})
    
    dji_returns_df = pd.DataFrame(dji_period_returns).sort_values('entry_date')
    dji_returns_df['dji_cum_return'] = (1 + dji_returns_df['dji_period_return']).cumprod()
    
    # Merge portfolio and Dow30 performance for comparison
    performance_df = period_returns_df.merge(dji_returns_df[['entry_date', 'dji_cum_return']], on='entry_date', how='left')
    st.dataframe(performance_df)
    
    fig_compare = px.line(performance_df, x='entry_date', y=['cum_return', 'dji_cum_return'],
                          title="Cumulative Return: Portfolio vs Dow30",
                          labels={'entry_date': 'Rebalancing Date', 'value': 'Cumulative Return'},
                          markers=True)
    st.plotly_chart(fig_compare, use_container_width=True)
    
    final_dji_return = performance_df['dji_cum_return'].iloc[-1]
    st.write(f"**ผลตอบแทนสะสมของ Dow30:** {final_dji_return:.2%}")
    st.write(f"**ผลตอบแทนสะสมของ cumre:** {final_cum_return:.2%}")
>>>>>>> 6772277 (first commit)
