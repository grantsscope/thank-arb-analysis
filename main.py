import streamlit as st
import pandas as pd

def load_data():
    # Load the dataset
    df = pd.read_csv("project_metrics.csv")
    
    # Calculate the Activity Score
    df['Activity Score'] = (df['commit_count_6_months'] * 0.5) + \
                           (df['merged_pull_request_count_6_months'] * 0.3) + \
                           (df['active_developer_count_6_months'] * 0.2)
    
    # Select and rename relevant columns
    df = df.rename(columns={
        'display_name': 'Project Name',
        'commit_count_6_months': 'Commit Count',
        'merged_pull_request_count_6_months': 'Merged Pull Request Count',
        'active_developer_count_6_months': 'Active Developer Count',
        'contributor_count_6_months': 'Contributor Count',
        'new_contributor_count_6_months': 'New Contributor Count'
    })

    columns = [
        'Project Name', 'Activity Score', 'Commit Count', 
        'Merged Pull Request Count', 'Active Developer Count', 
        'Contributor Count', 'New Contributor Count'
    ]

    return df[columns]

# Set up the Streamlit interface
st.title("Thank Arb Impact Analysis")

st.markdown("### Profiling based on code metrics in last 6 months")
st.markdown("Projects are sorted based on their Activity Score. This is a composite metric based on code commits (50%), merged pull requests (30%), and active developer count (20%)")
# Load data
data = load_data()

# Display the dataframe
st.dataframe(data)
