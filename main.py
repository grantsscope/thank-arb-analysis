import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Set page configuration to wide layout
st.set_page_config(layout="wide")

def load_data():
    # Load the dataset
    df = pd.read_csv("./data/project_metrics.csv")
    
    # Calculate the Development Activity Index
    df['Development Activity Index'] = (df['commit_count_6_months'] * 0.5) + \
                           (df['merged_pull_request_count_6_months'] * 0.3) + \
                           (df['active_developer_count_6_months'] * 0.2)
    
    # Select and rename relevant columns
    df = df.rename(columns={
        'display_name': 'Project Name',
        'repository_count': 'Repository Count',
        'commit_count_6_months': 'Commit Count',
        'active_developer_count_6_months': 'Active Developer Count',
        'contributor_count_6_months': 'Contributor Count',
        'new_contributor_count_6_months': 'New Contributor Count',
        'opened_pull_request_count_6_months': '# of Open PRs',	
        'merged_pull_request_count_6_months': '# of Merged PRs',
        'opened_issue_count_6_months': '# of Issues Opened',
        'closed_issue_count_6_months': '# of Issues Closed',
        'last_commit_date': 'Last Commit'
    })

    columns = [
        'Project Name', 'Development Activity Index', 'Commit Count', 'Active Developer Count', '# of Merged PRs',
        'Contributor Count', 'New Contributor Count', 'Repository Count',
        '# of Open PRs', 
        '# of Issues Opened', '# of Issues Closed', 'Last Commit'
    ]
    
    # Sort by Development Activity Index in descending order
    df = df[columns].sort_values(by='Development Activity Index', ascending=False)
    
    return df[columns]

# Set up the Streamlit interface
st.title("Thank ARB Impact Analysis - DRAFT")

st.markdown("This analysis focuses on a list of 54 projects uploaded in the [Thank ARB Grantee Collection](https://github.com/opensource-observer/oss-directory/blob/main/data/collections/thank-arb-grantees.yaml) \
            in OSO Directory. Note that this is a static data extracted as of September 18th, 2024. Refer [this](https://docs.google.com/spreadsheets/d/1Ka6x8GKcBNf1kmic2AjJMEeo7aGN8PBO3phvKcCW1hk/edit?gid=1301894510#gid=1301894510) spreadsheet for the coverage of artifacts for each projects used in this analysis.")

# Load data
data = load_data()

project_count = len(data)
total_repos = round(data['Repository Count'].sum())
total_contributors = round(data['Contributor Count'].sum())
new_contributors = round(data['New Contributor Count'].sum())
total_open_PR = round(data['# of Open PRs'].sum())
total_merged_PR = round(data['# of Merged PRs'].sum())
total_issues_opened = round(data['# of Issues Opened'].sum())
total_issues_closed = round(data['# of Issues Closed'].sum())

st.markdown(f"\n Overall, Thank ARB is helping support: \
            \n - {project_count} out of 54 projects with at least some recent OSS component to their work \
            \n - a total of {total_repos:,} Github repos \
            \n - {total_contributors:,} contributors over 6 months")

st.markdown(f"\n In the last 6 months, these {project_count} projects: \
            \n - Attracted {new_contributors:,} new contributors \
            \n - Closed over {total_issues_closed:,} issues (and created {total_issues_opened:,} new ones) \
            \n - Merged over {total_merged_PR:,} pull requests (and opened {total_open_PR:,} new ones)")

st.markdown("### What are the top projects based on development activities?")
st.markdown("""
Projects are ranked according to their Development Activity Index, a composite metric derived from:
- **Code Commits** (50%)
- **Merged Pull Requests** (30%)
- **Active Developer Count** (20%)
""")

st.info("""
**Note on Development Activity Index:** The Development Activity Index is a proposed custom composite metric tailored to reflect coding activities. Depending on grant objectives, different combinations of metrics might be employed to more accurately evaluate grantee performance.
""")

# Analyze top performers
top_performers = data.sort_values(by='Development Activity Index', ascending=False).head(5)

# Projects with increasing new contributors
emerging_projects = data[data['New Contributor Count'] > 0].sort_values(by='New Contributor Count', ascending=False).head(5)

st.markdown("#### Key Findings:")
# Display summaries of top performers and emerging projects
st.markdown("- Top 5 Performers based on Development Activity Index: " + 
            ", ".join(top_performers['Project Name'].tolist()) +
            "\n - Top 5 Emerging Projects (by New Contributors): " + 
            ", ".join(emerging_projects['Project Name'].tolist()))

# Calculate the date 3 months ago from today in UTC
three_months_ago = datetime.now(pytz.UTC) - timedelta(days=90)

# Convert 'Last Commit' to datetime and filter projects
data['Last Commit'] = pd.to_datetime(data['Last Commit'], format='%Y-%m-%d %H:%M:%S%z')
inactive_projects = data[data['Last Commit'] < three_months_ago]

# Sort inactive projects by last commit date
inactive_projects = inactive_projects.sort_values('Last Commit')

# Display the list of inactive projects
st.markdown("- Projects with no commits in the last 3 months:")
if not inactive_projects.empty:
    for _, project in inactive_projects.iterrows():
        st.markdown(f"    - {project['Project Name']} (Last commit: {project['Last Commit'].strftime('%d-%b-%Y')})")
else:
    st.markdown("No projects found with last commit dates older than 3 months.")


# Display the dataframe without index
st.caption("Click on a column name to sort the table.")

# Define the columns you want to display and their order
columns_to_display = [
    'Project Name', 
    'Development Activity Index', 
    'Commit Count', 
    '# of Merged PRs',
    'Active Developer Count', 
    'Contributor Count', 
    'New Contributor Count'
]

# Create a new dataframe with only the selected columns
display_data = data[columns_to_display]

# Display the dataframe
st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Development Activity Index": st.column_config.NumberColumn(format="%d"),
    }
)
