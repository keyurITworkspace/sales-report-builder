import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile

st.title("Sales Dashboard")
st.subheader("Interactive dashboard with dynamic data upload (CSV / Excel / ZIP)")
st.markdown(
            "<h2 style='color:red; font-size:35px; font-weight:bold; font-style:italic;'>Made With ❤️ by KP </h2>",
            unsafe_allow_html=True
        )

# ----------------------------
# Step 1: File uploader
uploaded_file = st.file_uploader("Upload CSV, Excel, or ZIP file", type=["csv", "xlsx", "zip"])
if uploaded_file is not None:

    # ----------------------------
    # Step 2: Load data based on file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file,encoding = "latin 1")

    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    elif uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file) as z:
            file_list = z.namelist()
            csv_file = [f for f in file_list if f.endswith('.csv')][0]  # first CSV
            with z.open(csv_file) as f:
                df = pd.read_csv(f)

    # ----------------------------
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Map only existing columns to standard dashboard names
    column_mapping = {
        'order date': 'order_date',
        'region': 'region',
        'sales': 'sales',
        'profit': 'profit',
        'category': 'category',
        'product name': 'product_name'
    }

    df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

    # ----------------------------
    # Step 4: Safety check
    required_cols = ['order_date', 'region', 'sales', 'profit', 'category']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Missing columns in the dataset: {missing}")
    else:
        # Convert dates & clean
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        df = df.dropna().drop_duplicates()

        # ----------------------------
        # Step 4.1: Convert numeric columns
        numeric_cols = ['sales', 'profit']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=numeric_cols)

        # ----------------------------
        # Step 5: Filters
        region = st.selectbox("Select Region", ["All"] + list(df["region"].unique()))
        if region != "All":
            filtered = df[df["region"] == region]
        else:
            filtered = df

        # Optional: date filter
        start_date = st.date_input("Start Date", df["order_date"].min())
        end_date = st.date_input("End Date", df["order_date"].max())
        filtered = filtered[(filtered["order_date"] >= pd.to_datetime(start_date)) &
                            (filtered["order_date"] <= pd.to_datetime(end_date))]

        # ----------------------------
        # Step 6: Summary stats
        st.subheader("Summary")
        st.write("Total Sales:", filtered["sales"].sum().round(2))
        st.write("Average Sales:", filtered["sales"].mean().round(2))
        st.write("Total Profit:", filtered["profit"].sum().round(2))

        # ----------------------------
        # Step 7: Pie Chart - Sales by Category
        st.subheader("Sales Distribution by Category")
        sales_by_category = filtered.groupby("category")["sales"].sum()
        fig1, ax1 = plt.subplots()
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        ax1.pie(sales_by_category, labels=sales_by_category.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')
        st.pyplot(fig1)

        # ----------------------------
        # Step 8: Line Chart - Sales Trend
        st.subheader("Sales Trend")
        filtered_sorted = filtered.sort_values("order_date")
        st.line_chart(filtered_sorted.groupby("order_date")["sales"].sum())

        # ----------------------------
        # Step 9: Bar Chart - Profit by Category
        st.subheader("Profit by Category")
        st.bar_chart(filtered.groupby("category")["profit"].sum())

        # ----------------------------
        # Step 10: Top Products
        st.subheader("Top 10 Products by Sales")
        if 'product_name' in filtered.columns:
            top10 = filtered.groupby("product_name")["sales"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top10)
        st.subheader("lowest 10 Products by Sales")
        if 'product_name' in filtered.columns:
            lowest10 = filtered.groupby("product_name")["sales"].sum().sort_values(ascending=False).tail(10)
            st.bar_chart(lowest10)

        #st.markdown("---")  # horizontal line
        #st.markdown(
         #   "<h2 style='color:red; font-size:35px; font-weight:bold; font-style:italic;'>Made With ❤️ by KP </h2>",
           #  unsafe_allow_html=True
        #)