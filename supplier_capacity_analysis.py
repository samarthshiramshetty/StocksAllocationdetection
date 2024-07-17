import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

# Load the datasets
@st.cache_data
def load_data():
    data = pd.read_excel('NIUDataVisualizationCompetition.xlsx')
    data2 = pd.read_excel('book2.xlsx')
    data3 = pd.read_excel('book3.xlsx')
    return data, data2, data3

# Merge datasets to gather all relevant information
@st.cache_data
def merge_data(data, data2, data3):
    merged_data = pd.merge(data, data2, on=['geonode_id', 'sku_id'])
    merged_data = pd.merge(merged_data, data3, on='geonode_id')
    merged_data['utilization'] = (merged_data['num_of_max_prod_days'] / merged_data['max_capacity']) * 100
    merged_data['demand_change'] = merged_data.groupby(['geonode_id', 'sku_id'])['forecast'].transform('sum')
    merged_data['start_date'] = pd.to_datetime(merged_data['start_date'])
    return merged_data

# Identify high-risk suppliers
def identify_high_risk_suppliers(filtered_data):
    high_risk_suppliers = filtered_data[(filtered_data['utilization'] > 80) & (filtered_data['demand_change'] > 0)]
    return high_risk_suppliers

# Streamlit app
def main():
    st.title("Supplier Capacity Risk Analysis")
    data, data2, data3 = load_data()
    merged_data = merge_data(data, data2, data3)

    # Date and Year filters
    selected_year = st.selectbox("Select Year", merged_data['start_date'].dt.year.unique(), key='year_filter')
    selected_date = st.date_input("Select Start Date", value=merged_data.loc[merged_data['start_date'].dt.year == selected_year, 'start_date'].min().date(), min_value=merged_data.loc[merged_data['start_date'].dt.year == selected_year, 'start_date'].min().date(), max_value=merged_data.loc[merged_data['start_date'].dt.year == selected_year, 'start_date'].max().date(), key='date_filter')
    start_date = datetime.combine(selected_date, datetime.min.time())  # Convert to datetime object
    end_date = start_date + timedelta(days=90)  # Three months or a quarter
    filtered_data = merged_data[(merged_data['start_date'].dt.year == selected_year) & (merged_data['start_date'] >= start_date) & (merged_data['start_date'] < end_date)]

    # Capacity utilization distribution by organization
    st.subheader("Capacity Utilization Distribution by Organization")
    org_filter = st.multiselect("Select Organizations", filtered_data['org_id'].unique(), default=filtered_data['org_id'].unique())
    org_filtered_data = filtered_data[filtered_data['org_id'].isin(org_filter)]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=org_filtered_data, x='org_id', y='utilization', ax=ax)
    ax.set_title('Capacity Utilization Distribution by Organization', fontsize=16)
    ax.set_xlabel('Organization ID', fontsize=14)
    ax.set_ylabel('Average Capacity Utilization (%)', fontsize=14)
    plt.xticks(rotation=90)
    st.pyplot(fig)
    st.write("This bar plot shows the average capacity utilization percentage for each organization. The x-axis represents the organization IDs, and the y-axis represents the average capacity utilization percentage.")

    # Demand change by product
    st.subheader("Demand Change by Product")
    sku_filter = st.multiselect("Select Products", filtered_data['sku_id'].unique(), default=filtered_data['sku_id'].unique())
    sku_filtered_data = filtered_data[filtered_data['sku_id'].isin(sku_filter)]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=sku_filtered_data, x='sku_id', y='demand_change', ax=ax)
    ax.set_title('Demand Change by Product', fontsize=16)
    ax.set_xlabel('Product (SKU ID)', fontsize=14)
    ax.set_ylabel('Total Demand Change', fontsize=14)
    plt.xticks(rotation=90)
    st.pyplot(fig)
    st.write("This bar plot shows the total demand change for each product (SKU ID). The x-axis represents the product SKU IDs, and the y-axis represents the total demand change.")

    # Identify high-risk suppliers
    high_risk_suppliers = identify_high_risk_suppliers(filtered_data)
    st.subheader("High-Risk Suppliers")
    if not high_risk_suppliers.empty:
        st.write(high_risk_suppliers[['geonode_id', 'sku_id', 'utilization', 'demand_change']])
    else:
        st.write("No high-risk suppliers found for the selected filters.")

    # Potential Mitigation Options
    st.subheader("Potential Mitigation Options")
    st.write("1. Production adjustments: Work with high-risk suppliers to adjust their production schedules, shift resources, or implement capacity optimization strategies.")
    st.write("2. Seek alternative suppliers: Explore alternative suppliers or reallocate orders to suppliers with lower capacity utilization and better ability to handle demand fluctuations.")
    st.write("3. Demand smoothing: Implement strategies to smooth out demand patterns and reduce fluctuations that may strain supplier capacity.")
    st.write("4. Capacity expansion: Collaborate with critical suppliers to invest in capacity expansion projects, such as facility upgrades, equipment purchases, or process improvements.")
    st.write("5. Supplier development: Work closely with suppliers facing capacity challenges to identify bottlenecks, provide training and support, and help them implement best practices.")
    st.write("6. Risk mitigation strategies: Develop contingency plans and risk mitigation strategies for suppliers with high capacity risks.")

if __name__ == "__main__":
    main()
