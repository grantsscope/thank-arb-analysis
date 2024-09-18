import streamlit as st
import pandas as pd

def load_data():
    # Load the dataset
    df = pd.read_csv("./data/project_metrics.csv")
    
    # Calculate the Activity Score
    df['activity_score'] = (df['commit_count_6_months'] * 0.5) + \
                           (df['merged_pull_request_count_6_months'] * 0.3) + \
                           (df['active_developer_count_6_months'] * 0.2)
    
    # Select relevant columns
    columns = ['display_name', 'activity_score', 'contributor_count_6_months',
               'new_contributor_count_6_months', 'active_developer_count_6_months',
               'commit_count_6_months', 'merged_pull_request_count_6_months']
    
    return df[columns]

# Set up the Streamlit interface
st.title("Project Activity Dashboard")

# Load data
data = load_data()

# Display the dataframe
st.dataframe(data)
