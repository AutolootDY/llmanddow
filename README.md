# แดชบอร์ดแสดงผลพอร์ตโฟลิโอ, ประสิทธิภาพ และการเปรียบเทียบกับ NASDAQ

โครงการนี้เป็นแดชบอร์ดอินเทอร์แอคทีฟที่พัฒนาด้วย **Streamlit** และ **Plotly** เพื่อวิเคราะห์และแสดงผลการจัดพอร์ตโฟลิโอโดยใช้ข้อมูลหุ้นที่คำนวณ rolling correlation (รวมถึง ADX) พร้อมทั้งคำนวณผลตอบแทนรายวันและผลตอบแทนสะสมในแต่ละช่วง rebalancing โดยเปรียบเทียบประสิทธิภาพของพอร์ตกับดัชนี NASDAQ

## ภาพรวมงาน

โค้ดหลักในโปรเจกต์นี้ทำสิ่งต่าง ๆ ดังนี้:

1. **อ่านข้อมูลจากไฟล์ CSV**  
   - อ่านข้อมูลหุ้นจากไฟล์ `merged_rolling_corr_with_adx_return.csv` ซึ่งมีคอลัมน์หลัก ได้แก่  
     `date_only, datetime, symbol, open, high, low, close, volume, llm, rolling_corr, return`  
     โดยคอลัมน์ `return` จะเป็นผลตอบแทนรายวันของหุ้นที่คำนวณไว้ล่วงหน้า
   - อ่านวัน rebalancing จากไฟล์ `Cell output 2_filtered_t.csv` (มีคอลัมน์ `date`) ซึ่งใช้เป็นจุดเข้าออกของการจัดพอร์ต
   - อ่านข้อมูลของดัชนี NASDAQจากไฟล์ `DJI_filtered_return.csv` (แม้ในโค้ดตัวแปรยังใช้ชื่อ `dji_df`) และตรวจสอบว่ามีคอลัมน์ `return` หากไม่มีจะคำนวณจากคอลัมน์ `close`

2. **แสดงตัวอย่างข้อมูล (Data Preview)**  
   - แสดงตัวอย่างข้อมูลจากไฟล์ทั้งสามเพื่อให้แน่ใจว่าข้อมูลถูกต้องและครบถ้วน

3. **ตั้งค่าและคัดกรองหุ้นสำหรับพอร์ต**  
   - ผู้ใช้ระบุค่า threshold สำหรับ `rolling_corr` ผ่านตัวเลือก (เช่น ค่า default = 0.3)
   - ใช้วัน rebalancingจากไฟล์ rebalancing (`Cell output 2_filtered_t.csv`) เป็นจุดตัดแบ่งช่วงในการจัดพอร์ต
   - สำหรับแต่ละ rebalancing date จะดึงข้อมูลจากไฟล์หุ้นที่มี `date_only` ตรงกับ rebalancing date นั้น  
   - จากนั้นคัดกรองหุ้นที่มี `rolling_corr` มากกว่า threshold  
   - หากมีหุ้นเกิน 10 ตัว จะเลือกเฉพาะ Top 10 โดยจัดเรียงตามค่าสัมประสิทธิ์ (descending order)
   - คำนวณน้ำหนักของหุ้นในพอร์ตโดย normalize ค่า `rolling_corr` (น้ำหนัก = ค่า rolling_corr ของหุ้นนั้น / ผลรวมค่า rolling_corr ของหุ้นทั้งหมดที่ผ่านเงื่อนไข)

4. **คำนวณผลตอบแทนพอร์ตโฟลิโอ (Portfolio Return)**  
   - ในแต่ละ rebalancing period (ระหว่างวัน entry และ exit) จะดึงข้อมูลผลตอบแทนของหุ้นในช่วงนั้นจากไฟล์หุ้น  
   - สำหรับหุ้นแต่ละตัว คำนวณผลตอบแทนสะสมโดยใช้สูตร:
     
     \[
     \text{ผลตอบแทนสะสม} = \prod (1 + \text{ผลตอบแทนรายวัน}) - 1
     \]
     
     (ยกตัวอย่าง ถ้าหุ้นมีผลตอบแทนรายวัน \(r_1, r_2, \dots, r_n\) แล้ว ผลตอบแทนสะสมจะคำนวณจาก \((1+r_1)(1+r_2)\dots (1+r_n) - 1\))
   - ผลตอบแทนของพอร์ตในช่วง period นั้นคำนวณเป็นผลรวมของ (น้ำหนัก × ผลตอบแทนสะสมของหุ้น)
   - จากนั้น นำผลตอบแทนในแต่ละ period มาคำนวณ cumulative return ของพอร์ตโดยใช้การ compounding เช่น:
     
     \[
     \text{ผลตอบแทนสะสมพอร์ต} = \prod (1 + \text{ผลตอบแทน period}) - 1
     \]

5. **เปรียบเทียบกับดัชนี NASDAQ**  
   - สำหรับข้อมูลดัชนี NASDAQ ที่อ่านจาก `DJI_filtered_return.csv` (ในโค้ดใช้ตัวแปร `dji_df`) จะถูกใช้คำนวณผลตอบแทนในแต่ละ period โดยใช้หลักการเดียวกับพอร์ต  
   - ในแต่ละช่วง rebalancing จะดึงข้อมูลผลตอบแทนรายวันของ NASDAQ แล้วคำนวณ period return ด้วยสูตร:
     
     \[
     \text{ผลตอบแทน period NASDAQ} = \prod (1 + \text{ผลตอบแทนรายวัน}) - 1
     \]
     
     พร้อมทั้งเก็บ log รายละเอียดของผลตอบแทนรายวันในแต่ละ period
   - คำนวณ cumulative return ของ NASDAQ จากผลตอบแทนแต่ละ periodโดยใช้การคูณแบบ compounding
   - ผลลัพธ์ของ NASDAQ (ทั้ง period return และ cumulative return) จะถูกแสดงในตารางและกราฟ เพื่อให้สามารถเปรียบเทียบกับพอร์ตโฟลิโอได้

6. **การแสดงผล (Dashboard Visualization)**  
   - แสดงตารางของ portfolio composition ในแต่ละ rebalancing date (แสดงสัญลักษณ์หุ้น, ค่า rolling_corr, และน้ำหนักของหุ้น)
   - ใช้ Plotly สร้างกราฟ Bar Chart เพื่อแสดงการจัดสรรพอร์ตในแต่ละวัน rebalancing
   - สร้างกราฟ Line Chart แสดง cumulative return ของพอร์ตตลอดช่วง rebalancing
   - แสดงตารางและกราฟสำหรับดัชนี NASDAQ ได้แก่ period return และ cumulative return พร้อมทั้ง log รายละเอียดของผลตอบแทนรายวันในแต่ละ period
   - มีการ merge ข้อมูล performance ของพอร์ตและ NASDAQ เพื่อเปรียบเทียบด้วยกราฟ Line Chart

## ข้อกำหนดและการติดตั้ง

- **ภาษา:** Python 3.x
- **ไลบรารีที่ใช้:**
  - [pandas](https://pandas.pydata.org/)
  - [numpy](https://numpy.org/)
  - [plotly](https://plotly.com/python/)
  - [streamlit](https://streamlit.io/)

ติดตั้ง dependencies ด้วยคำสั่ง:
```bash
pip install pandas numpy plotly streamlit
