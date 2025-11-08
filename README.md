
# 📊 Daily Market Prices of Agricultural Commodities in India (2001–2025)

## 🧾 About the Dataset
This dataset provides **daily market prices of agricultural commodities across India** from **2001 to 2025**.  
It contains over **75 million records** covering **374 unique commodities** and **1,504 varieties** traded across various **mandis (wholesale markets)**.  
Commodities include **vegetables, fruits, grains, spices**, and more.

The dataset is **cleaned, deduplicated, and sorted** by date and commodity for easy analysis.

---

## 📂 Column Schema

| Column Name       | Description                                                                 | Type       |
|--------------------|------------------------------------------------------------------------------|-------------|
| **State**          | Name of the Indian state where the market is located                        | Province    |
| **District**       | Name of the district within the state where the market is located           | City        |
| **Market**         | Name of the specific market (mandi) where the commodity is traded            | String      |
| **Commodity**      | Name of the agricultural commodity being traded                             | String      |
| **Variety**        | Specific variety or type of the commodity                                   | String      |
| **Grade**          | Quality grade of the commodity (e.g., FAQ, Medium, Good)                    | String      |
| **Arrival_Date**   | Date of price recording (ISO 8601 format: YYYY-MM-DD)                       | Datetime    |
| **Min_Price**      | Minimum price of the commodity (in INR per quintal)                         | Decimal     |
| **Max_Price**      | Maximum price of the commodity (in INR per quintal)                         | Decimal     |
| **Modal_Price**    | Most frequent (modal) price of the commodity (in INR per quintal)           | Decimal     |
| **Commodity_Code** | Unique code identifier for the commodity                                    | Numeric     |

---

## 🏛️ Data Source
Data is sourced from the **Government of India’s Open Data Platform**:  
[https://data.gov.in/](https://data.gov.in/)

---

## ⚖️ License
**Government Open Data License - India (GODL-India)**  
You are free to use, share, and adapt the data with proper attribution.

---

## 💡 Usage
This dataset can be used for:
- Time-series price analysis of agricultural commodities  
- Market trend prediction and forecasting  
- Supply chain and policy research  
- Visualization of regional price variations across states and districts

---

📅 **Data Range:** 2001–2025  
📈 **Records:** 75M+  
🌾 **Commodities:** 374  
🏪 **Markets (Mandis):** 1,500+
