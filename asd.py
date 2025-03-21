# # # import streamlit as st
# # # import pandas as pd
# # # import plotly.express as px

# # # st.title("Rolling Correlation Plot with Fullscreen Toggle")

# # # # ให้ผู้ใช้เลือกไฟล์ CSV
# # # uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# # # if uploaded_file is not None:
# # #     # อ่านข้อมูลจาก CSV และ parse คอลัมน์ 'date_only' ให้เป็น datetime
# # #     df = pd.read_csv(uploaded_file, parse_dates=['date_only'])
    
# # #     # แสดงตัวอย่างข้อมูล
# # #     st.subheader("Data Preview")
# # #     st.dataframe(df.head())
    
# # #     # สร้าง Line Plot โดยใช้ Plotly Express
# # #     fig = px.line(
# # #         df,
# # #         x='date_only',
# # #         y='rolling_corr',
# # #         color='symbol',
# # #         title='Rolling Correlation (6-month window) for Dow Jones 30 Stocks',
# # #         labels={'date_only': 'Date', 'rolling_corr': 'Rolling Correlation'}
# # #     )
    
# # #     # กำหนด config เพื่อเพิ่มปุ่ม Fullscreen ใน Mode Bar
# # #     config = {
# # #         'displayModeBar': True,
# # #         'modeBarButtonsToAdd': ['toggleFullscreen'],
# # #         'displaylogo': False
# # #     }
    
# # #     st.subheader("Plot")
# # #     # แสดงกราฟพร้อมปุ่ม Fullscreen
# # #     st.plotly_chart(fig, config=config, use_container_width=True)
# # # else:
# # #     st.info("Please upload a CSV file.")



# # import streamlit as st
# # import pandas as pd
# # import plotly.express as px

# # st.title("Monthly Analysis: Top 10 Positive Rolling Correlation & Stocks Above 0.3 Threshold")

# # # ให้ผู้ใช้เลือกไฟล์ CSV
# # uploaded_file = st.file_uploader("Upload CSV file", type="csv")

# # if uploaded_file is not None:
# #     # อ่านไฟล์ CSV โดย parse คอลัมน์ 'date_only' ให้เป็น datetime
# #     df = pd.read_csv(uploaded_file, parse_dates=['date_only'])
    
# #     st.subheader("Data Preview")
# #     st.dataframe(df.head())
    
# #     # ตรวจจับเฉพาะข้อมูลของวันที่ 1 ของทุกเดือน
# #     df_first = df[df['date_only'].dt.day == 1].copy()
    
# #     if df_first.empty:
# #         st.warning("ไม่พบข้อมูลในวันที่ 1 ของเดือน")
# #     else:
# #         st.subheader("Monthly Analysis on the 1st Day of Each Month")
        
# #         # Group ตาม 'date_only'
# #         for date, group in df_first.groupby('date_only'):
# #             st.markdown(f"### Date: {date.date()}")
            
# #             # 1. Top 10 หุ้นที่มี rolling correlation ฝั่งบวก (positive) สูงสุด
# #             group_positive = group[group['rolling_corr'] > 0]
# #             top10 = group_positive.sort_values('rolling_corr', ascending=False).head(10)
            
# #             st.markdown("**Top 10 Stocks with Highest Positive Rolling Correlation**")
# #             if not top10.empty:
# #                 st.dataframe(top10)
# #             else:
# #                 st.write("ไม่พบหุ้นที่มี rolling correlation ฝั่งบวก")
            
# #             # 2. หุ้นที่มี rolling_corr > 0.3
# #             stocks_above = group[group['rolling_corr'] > 0.3]
# #             st.markdown("**Stocks with Rolling Correlation > 0.3**")
# #             if not stocks_above.empty:
# #                 st.dataframe(stocks_above)
# #             else:
# #                 st.write("ไม่พบหุ้นที่มี rolling correlation > 0.3")
            
# #             # Plot กราฟสำหรับวันนั้น
# #             fig = px.bar(group, x='symbol', y='rolling_corr',
# #                          title=f"Rolling Correlation on {date.date()}",
# #                          labels={'symbol': 'Stock Symbol', 'rolling_corr': 'Rolling Correlation'})
            
# #             # เพิ่มเส้นแนวนอนที่ y = 0.3
# #             # สำหรับแกน x ที่เป็นประเภท category ให้ใช้ค่า x0, x1 ใหญ่พอครอบคลุมทุก bar
# #             fig.add_shape(
# #                 type="line",
# #                 x0=-0.5,
# #                 x1=len(group['symbol']) - 0.5,
# #                 y0=0.3,
# #                 y1=0.3,
# #                 line=dict(color="Red", dash="dash"),
# #             )
# #             # ปรับ range ของแกน y ให้เหมาะสม
# #             y_min = group['rolling_corr'].min() - 0.1
# #             y_max = group['rolling_corr'].max() + 0.1
# #             fig.update_yaxes(range=[y_min, y_max])
            
# #             st.plotly_chart(fig, use_container_width=True)
# # else:
# #     st.info("Please upload a CSV file.")
# # # 


# import streamlit as st
# import pandas as pd
# import plotly.express as px

# st.title("Monthly Analysis: Top 10 Positive Rolling Correlation & Stocks Above a User-Defined Threshold")

# # ให้ผู้ใช้เลือกไฟล์ CSV ที่มีคอลัมน์: date_only, symbol, rolling_corr
# uploaded_file = st.file_uploader("Upload CSV file", type="csv")

# # ให้ผู้ใช้กำหนด threshold สำหรับ rolling correlation (ค่า ts)
# threshold = st.number_input("Enter threshold for Rolling Correlation", value=0.3, step=0.05, format="%.2f")

# if uploaded_file is not None:
#     # อ่านไฟล์ CSV โดย parse คอลัมน์ 'date_only' ให้เป็น datetime
#     df = pd.read_csv(uploaded_file, parse_dates=['date_only'])
    
#     st.subheader("Data Preview")
#     st.dataframe(df.head())
    
#     # กรองเฉพาะข้อมูลในวันที่ 1 ของทุกเดือน
#     df_first = df[df['date_only'].dt.day == 1].copy()
    
#     if df_first.empty:
#         st.warning("ไม่พบข้อมูลในวันที่ 1 ของเดือน")
#     else:
#         st.subheader("Monthly Analysis on the 1st Day of Each Month")
        
#         # วนลูปแสดงผลสำหรับแต่ละวันที่ 1 ของเดือน
#         for date, group in df_first.groupby('date_only'):
#             st.markdown(f"### Date: {date.date()}")
            
#             # 1. หา Top 10 หุ้นที่มี rolling correlation ฝั่งบวกสูงสุด
#             group_positive = group[group['rolling_corr'] > 0]
#             top10 = group_positive.sort_values('rolling_corr', ascending=False).head(10)
            
#             st.markdown("**Top 10 Stocks with Highest Positive Rolling Correlation**")
#             if not top10.empty:
#                 st.dataframe(top10)
#             else:
#                 st.write("ไม่พบหุ้นที่มี rolling correlation ฝั่งบวก")
            
#             # 2. ตรวจจับหุ้นที่มี rolling_corr > threshold (ค่า ts ที่ผู้ใช้ระบุ)
#             stocks_above = group[group['rolling_corr'] > threshold]
#             st.markdown(f"**Stocks with Rolling Correlation > {threshold}**")
#             if not stocks_above.empty:
#                 st.dataframe(stocks_above)
#             else:
#                 st.write(f"ไม่พบหุ้นที่มี rolling correlation > {threshold}")
            
#             # Plot กราฟ: Bar chart แสดง rolling correlation ของแต่ละหุ้นในวันนั้น
#             fig = px.bar(
#                 group,
#                 x='symbol',
#                 y='rolling_corr',
#                 title=f"Rolling Correlation on {date.date()}",
#                 labels={'symbol': 'Stock Symbol', 'rolling_corr': 'Rolling Correlation'}
#             )
            
#             # เพิ่มเส้นแนวนอนที่ y = threshold
#             fig.add_shape(
#                 type="line",
#                 x0=-0.5,
#                 x1=len(group['symbol']) - 0.5,
#                 y0=threshold,
#                 y1=threshold,
#                 line=dict(color="Red", dash="dash"),
#             )
            
#             # ปรับ range ของแกน y ให้เหมาะสม
#             y_min = group['rolling_corr'].min() - 0.1
#             y_max = group['rolling_corr'].max() + 0.1
#             fig.update_yaxes(range=[y_min, y_max])
            
#             st.plotly_chart(fig, use_container_width=True)
# else:
#     st.info("Please upload a CSV file.")


import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Monthly Analysis: Top 10 Positive Rolling Correlation & Stocks Above Threshold")

# ระบุ path ของไฟล์ CSV (แก้ไขให้ตรงกับตำแหน่งไฟล์ของคุณ)
csv_path = "./output_folder/merged_rolling_corr.csv"

# อ่านไฟล์ CSV พร้อม parse คอลัมน์ 'date_only' เป็น datetime
df = pd.read_csv(csv_path, parse_dates=['date_only'])

st.subheader("Data Preview")
st.dataframe(df.head())

# ให้ผู้ใช้กำหนด threshold สำหรับ rolling correlation
threshold = st.number_input("Enter threshold for Rolling Correlation", value=0.3, step=0.05, format="%.2f")

# กรองเฉพาะข้อมูลในวันที่ 1 ของทุกเดือน
df_first = df[df['date_only'].dt.day == 1].copy()

if df_first.empty:
    st.warning("ไม่พบข้อมูลในวันที่ 1 ของเดือน")
else:
    st.subheader("Monthly Analysis on the 1st Day of Each Month")
    
    # วนลูปแสดงผลสำหรับแต่ละวันที่ 1 ของเดือน
    for date, group in df_first.groupby('date_only'):
        st.markdown(f"### Date: {date.date()}")
        
        # 1. หา Top 10 หุ้นที่มี rolling_corr ฝั่งบวกสูงสุด
        group_positive = group[group['rolling_corr'] > 0]
        top10 = group_positive.sort_values('rolling_corr', ascending=False).head(10)
        
        st.markdown("**Top 10 Stocks with Highest Positive Rolling Correlation**")
        if not top10.empty:
            st.dataframe(top10)
        else:
            st.write("ไม่พบหุ้นที่มี rolling correlation ฝั่งบวก")
        
        # 2. ตรวจจับหุ้นที่มี rolling_corr > threshold ที่ผู้ใช้ระบุ
        stocks_above = group[group['rolling_corr'] > threshold]
        st.markdown(f"**Stocks with Rolling Correlation > {threshold}**")
        if not stocks_above.empty:
            st.dataframe(stocks_above)
        else:
            st.write(f"ไม่พบหุ้นที่มี rolling correlation > {threshold}")
        
        # Plot กราฟ: Bar chart แสดง rolling_corr ของแต่ละหุ้นในวันนั้น
        fig = px.bar(group,
                     x='symbol',
                     y='rolling_corr',
                     title=f"Rolling Correlation on {date.date()}",
                     labels={'symbol': 'Stock Symbol', 'rolling_corr': 'Rolling Correlation'})
        
        # เพิ่มเส้นแนวนอนที่ y = threshold
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=len(group['symbol']) - 0.5,
            y0=threshold,
            y1=threshold,
            line=dict(color="Red", dash="dash")
        )
        
        # ปรับ range ของแกน y ให้เหมาะสม
        y_min = group['rolling_corr'].min() - 0.1
        y_max = group['rolling_corr'].max() + 0.1
        fig.update_yaxes(range=[y_min, y_max])
        
        st.plotly_chart(fig, use_container_width=True)
