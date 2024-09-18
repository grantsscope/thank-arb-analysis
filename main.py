import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import plotly.express as px
import plotly.graph_objects as go

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

# Convert 'Last Commit' to datetime and filter projects
data['Last Commit'] = pd.to_datetime(data['Last Commit'], format='%Y-%m-%d %H:%M:%S%z')
inactive_projects = data[data['Last Commit'] < three_months_ago]

# Sort inactive projects by last commit date
inactive_projects = inactive_projects.sort_values('Last Commit')

# Display the list of inactive projects
st.markdown("#### Other notes:")
st.error("Projects with no commits in the last 3 months:")
if not inactive_projects.empty:
    for i, (_, project) in enumerate(inactive_projects.iterrows(), 1):
        st.markdown(f"{i}. {project['Project Name']} (Last commit: {project['Last Commit'].strftime('%d-%b-%Y')})")
else:
    st.markdown("No projects found with last commit dates older than 3 months.")


st.markdown("""
### Project Activity Efficiency

This chart displays the 'Activity per Developer' ratio for each project. This ratio is calculated by dividing the Development Activity Index by the Active Developer Count.

**What does this mean?**
- A higher ratio indicates that a project is achieving more activity with fewer active developers, which could suggest higher efficiency or intensity of development work.
- A lower ratio might indicate projects with larger teams or those with more distributed workloads.

**How to interpret:**
- Projects at the top of the chart are achieving the highest activity per developer.
- This metric can help identify projects that are particularly productive relative to their team size.
- However, it's important to consider this alongside other metrics, as high activity per developer isn't always indicative of overall project health or success.
""")

st.info("**Note:** This ratio should be considered alongside other factors such as project complexity, stage of development, and specific project goals.")


# Calculate the ratio
data['Activity per Developer'] = data['Development Activity Index'] / data['Active Developer Count']

# Sort the data by the ratio in descending order
sorted_data = data.sort_values('Activity per Developer', ascending=True)

# Create a horizontal bar chart
fig = go.Figure(go.Bar(
    y=sorted_data['Project Name'],
    x=sorted_data['Activity per Developer'],
    orientation='h',
    marker_color='lightgreen',
    text=sorted_data['Activity per Developer'].round(2),  # Display the ratio value on each bar
    textposition='outside'
))

# Update the layout
fig.update_layout(
    title='Project Activity per Active Developer',
    xaxis_title='Development Activity Index per Active Developer',
    yaxis_title='Project Name',
    height=max(600, len(data) * 25),  # Adjust height based on number of projects
    width=800
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)


st.markdown("""
### Trend Analysis: Active Developer Engagement Over the Past 6 Months

This heatmap visualizes the daily active developer count for each project across its repositories over the last 6 months.

**Key insights:**
- Regular, consistent activity might indicate stable, ongoing development.
- Sporadic intense activity could suggest sprint-based development or periodic major updates.
- Long gray periods might indicate paused development or potential issues requiring attention.
""")

st.info("Remember that this visualization shows quantity, not quality, of engagement. It's best used alongside other metrics for a comprehensive understanding of project health and progress.")

df_repos = pd.read_csv("./data/repos.csv")

df_repos['sample_date'] = pd.to_datetime(df_repos['sample_date'])
df_repos['day'] = df_repos['sample_date'].dt.strftime('%Y-%m-%d')  # Formatting to ensure discrete daily data

# Filter for 'active_developers' metric and dates after March 1st, 2024
df_filtered = df_repos[(df_repos['metric_name'] == 'active_developers') & 
                       (df_repos['sample_date'] > '2024-03-01')]

# Create the pivot table with the filtered data
heatmap_data = df_filtered.pivot_table(index='project_name', 
                                       columns='day', 
                                       values='amount', 
                                       aggfunc='sum', 
                                       fill_value=0)

# Calculate the number of projects (rows) in your heatmap
num_projects = len(heatmap_data.index)

# Creating the heatmap with custom color scale and adjusted height
fig = px.imshow(heatmap_data,
                labels=dict(x="Day", y="Project", color="Number of Active Developers across Project Repositories"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                aspect="auto",  # Changed from "equal" to "auto"
                color_continuous_scale=[
                    [0, "rgb(220,220,220)"],    # Light gray for 0
                    [0.01, "rgb(220,220,220)"], # Light gray for 0
                    [0.01, "rgb(237,248,233)"], # Very light green for 1-2
                    [0.2, "rgb(186,228,179)"],  # Light green for 3-5
                    [0.4, "rgb(116,196,118)"],  # Medium green for 6-10
                    [1, "rgb(35,139,69)"]       # Dark green for 11+
                ],
                zmin=0,
                zmax=11)

# Update the layout to ensure proper sizing
fig.update_layout(
    xaxis={'type': 'category'},
    yaxis={'type': 'category'},
    coloraxis_colorbar=dict(
        tickvals=[0, 1.5, 4, 8, 11],
        ticktext=["0", "1-2", "3-5", "6-10", "11+"]
    ),
    height=max(600, num_projects * 20),  # Adjust height based on number of projects
    width=800,  # Adjust width as needed
    yaxis_nticks=num_projects  # Ensure all project names are shown
)
fig.update_xaxes(side="top")

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
