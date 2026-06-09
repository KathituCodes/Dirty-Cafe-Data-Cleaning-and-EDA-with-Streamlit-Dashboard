# Cafe Sales: End-to-End Data Wrangling and Exploratory Analysis

This is a systematic, documented data cleaning and EDA pipeline applied to a 10,000-row intentionally corrupted cafe sales dataset. The project demonstrates multi-layered handling of real-world data quality problems: type corruption, placeholder errors, missing value imputation via unit-economics logic and distribution-preserving sampling, outlier validation, and business-context analysis.

---

## Project Objectives

- Transform a raw, "dirty" dataset riddled with `ERROR` and `UNKNOWN` placeholders, wrong data types, and structural gaps into a fully analysis-ready table.
- Apply principled, documented decisions at every cleaning step rather than brute-force dropping or mode-filling.
- Derive business insights from the cleaned data on revenue drivers, payment preferences, location behavior, and sales trends.

---

## Dataset

| Property | Detail |
|---|---|
| Source | Synthetic dirty cafe sales data |
| Raw shape | 10,000 rows x 8 columns |
| Columns | Transaction ID, Item, Quantity, Price Per Unit, Total Spent, Payment Method, Location, Transaction Date |
| Known issues | `ERROR` / `UNKNOWN` text in numerical fields, all columns loaded as `object`, missing values across all columns, financial inconsistencies |

---

## Cleaning Pipeline

### 1. Initial Audit
- Shape inspection, `df.info()`, and unique value enumeration across all object columns.
- Confirmed all columns loaded as `object` due to string placeholders in numeric fields.
- Generated automated profiling reports (before and after) using `ydata-profiling`.

### 2. Placeholder Standardization
- Replaced `ERROR` and `UNKNOWN` with `np.nan` across the entire dataframe for uniform null handling.

### 3. Data Type Conversion
- Converted `Quantity`, `Price Per Unit`, and `Total Spent` from object to numeric using `pd.to_numeric(errors='coerce')`.
- Converted `Transaction Date` to datetime using `pd.to_datetime(errors='coerce')`.
- Documented why `errors='coerce'` was chosen over strict parsing.

### 4. Missing Value Imputation

| Column | Strategy | Rationale |
|---|---|---|
| `Price Per Unit` | Mode by Item group | Items have fixed prices; mode recovery is deterministic |
| `Item` | Reverse price-to-item map (unique-price-only) | Only applied where a price maps to exactly one item to avoid ambiguous assignment |
| `Total Spent` | `Quantity * Price Per Unit` | Unit economics recovery preserves financial integrity |
| `Quantity` | `Total Spent / Price Per Unit` | Inverse recovery from verified total |
| `Payment Method` | Random distribution-proportional sampling | Preserves real payment split; avoids inflating the modal category |
| `Location` | Random distribution-proportional sampling | Same reasoning as Payment Method |
| `Item` (residual) | Fill with `"Unknown"` | Preserves row count while flagging unresolvable records |
| `Quantity`, `Price Per Unit`, `Total Spent`, `Transaction Date` (residual) | Drop rows | Converting to string breaks numerical operations; volume is negligible (~0.7% of rows) |

### 5. Outlier Detection and Handling
- Visualized distributions using boxplots.
- Applied IQR method across `Quantity`, `Price Per Unit`, and `Total Spent`.
- Validated outliers against business domain logic: maximum possible transaction = 5 units x $5.00 = $25.00.
- Decision to **retain** all flagged outliers after confirming they fall within the physically possible range. No artificial capping required.

### 6. Duplicate Check
- Confirmed zero duplicate rows in the cleaned dataset.

---

## Exploratory Data Analysis

| Analysis | Key Finding |
|---|---|
| Best-selling items by revenue | Salads and Sandwiches lead revenue despite Coffee having the highest transaction frequency |
| Transaction value distribution | Majority of transactions cluster in the $3 to $10 range |
| Daily sales trend | Stable and consistent across the observation period with no significant growth signal |
| Payment method share | Digital Wallets outperform Cash and Credit Card, pointing to a speed-oriented customer base |
| Revenue by item and payment method | Revenue split is broadly proportional across payment types with no strong item-payment affinity |
| Revenue by item and location | Takeaway orders generate significantly more revenue than in-store, indicating a grab-and-go dominant business |

---

## Business Recommendations

1. **Optimize for speed.** The dominance of Takeaway and Digital Wallet payments confirms customers prioritize fast transactions. Streamlining order preparation and contactless checkout is higher-ROI than dine-in investment.
2. **Investigate the flat growth signal.** Stable daily sales with no upward trend indicate market saturation or a loyalty ceiling. Bundled promotions or upsell prompts (e.g., Coffee + Sandwich deals) could increase average transaction value without requiring new customer acquisition.
3. **Fix upstream data collection.** The volume of `ERROR` and `UNKNOWN` placeholders in `Location` and `Payment Method` suggests Point-of-Sale data entry gaps. Cleaner source data reduces imputation dependency and improves future analysis reliability.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| pandas | Data manipulation and cleaning |
| numpy | Numerical operations and NaN handling |
| matplotlib / seaborn | Static visualizations |
| plotly | Interactive sales trend chart |
| ydata-profiling | Automated before/after profiling reports |

---

## Repository Structure

```
cafe-sales-data-cleaning-eda/
|
|-- Dirty_Cafe_Sales_Data_Cleaning_and_EDA.ipynb   # Full notebook
|-- dirty_cafe_sales.csv                            # Raw input data
|-- cafe_sales_clean.csv                            # Cleaned output data
|-- README.md
```

---

## How to Run

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install pandas numpy matplotlib seaborn plotly ydata-profiling
   ```
3. Open the notebook in Jupyter or Google Colab.
4. Run all cells sequentially. The notebook is structured to be executed top to bottom with outputs displayed at each stage.

---

## Author

**Urbanus Kathitu** | [github.com/KathituCodes](https://github.com/KathituCodes)
