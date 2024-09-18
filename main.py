import streamlit as st
import pandas as pd

# Set page configuration to wide layout
st.set_page_config(layout="wide")

def load_data():
    # Load the dataset
    df = pd.read_csv("./data/project_metrics.csv")
    
    # Calculate the Activity Score
    df['Activity Score'] = (df['commit_count_6_months'] * 0.5) + \
                           (df['merged_pull_request_count_6_months'] * 0.3) + \
                           (df['active_developer_count_6_months'] * 0.2)
    
    # Select and rename relevant columns
    df = df.rename(columns={
        'display_name': 'Project Name',
        'repository_count': 'Repository Count',
        'commit_count_6_months': 'Commit Count',
        'merged_pull_request_count_6_months': 'Merged Pull Request Count',
        'active_developer_count_6_months': 'Active Developer Count',
        'contributor_count_6_months': 'Contributor Count',
        'new_contributor_count_6_months': 'New Contributor Count',
        'opened_pull_request_count_6_months': '# of Open PRs',	
        'merged_pull_request_count_6_months': '# of Merged PRs',
        'opened_issue_count_6_months': '# of Issues Opened',
        'closed_issue_count_6_months': '# of Issues Closed'

    })

    columns = [
        'Project Name', 'Activity Score', 'Commit Count', 
        'Merged Pull Request Count', 'Active Developer Count', 
        'Contributor Count', 'New Contributor Count', 'Repository Count',
        '# of Open PRs', '# of Merged PRs',
        '# of Issues Opened', '# of Issues Closed'
    ]
    
    # Sort by Activity Score in descending order
    df = df[columns].sort_values(by='Activity Score', ascending=False)
    
    return df[columns]

# Set up the Streamlit interface
st.title("Thank Arb Impact Analysis - DRAFT")

st.markdown("This analysis focuses on a list of 54 projects uploaded in the [Thank Arb Grantee Collection](https://github.com/opensource-observer/oss-directory/blob/main/data/collections/thank-arb-grantees.yaml) \
            in OSO Directory. Note that this is a static data extracted as of September 18th, 2024. Refer [this](https://docs.google.com/spreadsheets/d/1Ka6x8GKcBNf1kmic2AjJMEeo7aGN8PBO3phvKcCW1hk/edit?gid=1301894510#gid=1301894510) spreadsheet for the coverage of artifacts for each projects used in this analysis.")

# Load data
data = load_data()

project_count = len(data)
total_repos = data['Repository Count'].sum()
total_contributors = data['Contributor Count'].sum()
new_contributors = data['New Contributor Count'].sum()
total_open_PR = data['# of Open PRs'].sum()
total_merged_PR = data['# of Merged PRs'].sum()
total_issues_opened = data['# of Issues Opened'].sum()
total_issues_closed = data['# of Issues Closed'].sum()

st.markdown(f"\n Overall, Thank Arb is helping support: \
            \n - {project_count} out of 54 projects projects with at least some recent OSS component to their work \
            \n - {total_repos:,} Github repos \
            \n - {total_contributors:,} contributors")

st.markdown(f"\n In the last 6 months, these {project_count} projects: \
            \n - Attracted {new_contributors:,} new contributors \
            \n - Closed over {total_issues_closed:,} issues (and created {total_issues_opened:,} new ones) \
            \n - Merged over {total_merged_PR:,} pull requests (and opened {total_open_PR:,} new ones)")

st.markdown("### Profiling based on code metrics in last 6 months")
st.markdown("Projects are sorted based on their Activity Score. This is a composite metric based on code commits (50%), merged pull requests (30%), and active developer count (20%)")

# Analyze top performers
top_performers = data.sort_values(by='Activity Score', ascending=False).head(5)

# Projects with increasing new contributors
emerging_projects = data[data['New Contributor Count'] > 0].sort_values(by='New Contributor Count', ascending=False).head(5)

# Display summaries of top performers and emerging projects
st.markdown("- Top 5 Performers based on Activity Score")
st.text(', '.join(top_performers['Project Name'].tolist()))

st.markdown("- Top 5 Emerging Projects (by New Contributors)")
st.text(', '.join(emerging_projects['Project Name'].tolist()))

# Display the dataframe without index
st.caption("Click on a column name to sort the table.")


# Display the dataframe
st.dataframe(
    data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Activity Score": st.column_config.NumberColumn(format="%d"),
    }
)
