import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

# Set page config
st.set_page_config(page_title="Performance Tracker", layout="wide")

# Title
st.title("Performance Tracker")

# File upload section
st.sidebar.header("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload your data (CSV or Excel)", type=['csv', 'xlsx'])

# Date range input
st.sidebar.header("Date Range Selection")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=pd.to_datetime("2025-01-01"))
with col2:
    end_date = st.date_input("End Date", value=pd.to_datetime("2025-03-31"))

# Main content
if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Show raw data preview
        st.subheader("All Status")


        main_status = pd.pivot_table(
            data=df,
            values='Issue id',
            index='Assignee',
            columns=['Status','Work type'],
            aggfunc='count',
            margins=True
        )
    

        st.dataframe(main_status.head().style.background_gradient(cmap='coolwarm'))
        
        #
        
        # Process the data
        st.subheader("Data Processing")
        
        # Create date range bins
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        month_bin = pd.DataFrame({"Date": date_range})

        def assign_week_label(date):
            week_number = ((date.day - 1) // 7) + 1
            month_name = date.strftime("%b")
            return f"{month_name} Week {week_number}"

        month_bin["Week Bin"] = month_bin["Date"].apply(assign_week_label)
        month_bin['Created'] = month_bin['Date']
        month_bin['week'] = month_bin['Week Bin']

        # Categorize status
        def categorize_status(status):
            if status in ['QA Verified', 'Resolved']:
                return 'QA Verified'
            elif status in ['Open', 'Reopened', 'In Progress']:
                return 'In Progress'
            else:
                return 'Other'

        qav = df.copy()
        qav['status_group'] = qav['Status'].apply(categorize_status)

        # Convert dates and merge
        month_bin['Created'] = pd.to_datetime(month_bin['Created'])
        qav['Created'] = pd.to_datetime(qav['Created'])
        merged_df = qav.merge(month_bin, on='Created', how='left')

        # Create pivot table
        st.subheader("Performance Analysis")
        pivot = pd.pivot_table(
            data=merged_df,
            values='Issue id',
            index='Week Bin',
            columns=['Assignee', 'status_group'],
            aggfunc='count',
            margins=True
        )

        # Display pivot table
        st.dataframe(pivot.style.background_gradient(cmap='coolwarm'))

        # Download buttons
        st.subheader("Download Results")
        
        # CSV Download
        csv = merged_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Merged Data as CSV",
            data=csv,
            file_name='merged_data.csv',
            mime='text/csv'
        )
        
        # Excel Download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            merged_df.to_excel(writer, sheet_name='Merged Data', index=False)
            pivot.to_excel(writer, sheet_name='Pivot Table')
        
        st.download_button(
            label="Download Full Report as Excel",
            data=output.getvalue(),
            file_name='performance_report.xlsx',
            mime='application/vnd.ms-excel'
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload a file to get started")