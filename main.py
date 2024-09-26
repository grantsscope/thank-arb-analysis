import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
    
# Set page configuration to wide layout
st.set_page_config(layout="wide")

def min_max_normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def load_code_metrics_data():
    # Load the dataset
    df = pd.read_csv("./data/project_metrics.csv")
    
    # Apply logarithmic transformation to commit count
    df['log_commit_count'] = np.log1p(df['commit_count_6_months'])

    # Normalize each metric
    df['normalized_commits'] = min_max_normalize(df['log_commit_count'])
    df['normalized_prs'] = min_max_normalize(df['merged_pull_request_count_6_months'])
    df['normalized_devs'] = min_max_normalize(df['active_developer_count_6_months'])

    # Calculate the new Development Activity Index
    df['Development Activity Index'] = (
        df['normalized_commits'] * 0.5 +
        df['normalized_prs'] * 0.3 +
        df['normalized_devs'] * 0.2
    )

    # Scale the index to a 0-100 range for easier interpretation
    df['Development Activity Index'] = df['Development Activity Index'] * 100

    # Select and rename relevant columns
    df = df.rename(columns={
        'project_name': 'Project Key',
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
        'Project Key','Project Name', 'Development Activity Index', 'Commit Count', 'Active Developer Count', '# of Merged PRs',
        'Contributor Count', 'New Contributor Count', 'Repository Count',
        '# of Open PRs', 
        '# of Issues Opened', '# of Issues Closed', 'Last Commit'
    ]
    
    # Sort by Development Activity Index in descending order
    df = df[columns].sort_values(by='Development Activity Index', ascending=False)
    
    return df[columns]

# Set up the Streamlit interface
st.title("Thank ARB Impact Analysis - DRAFT")
st.markdown("[Powered by OSO](https://www.opensource.observer/)")

st.markdown("This analysis focuses on a list of 84 projects uploaded in the [Thank ARB Grantee Collection](https://github.com/opensource-observer/oss-directory/blob/main/data/collections/thank-arb-grantees.yaml) \
            in OSO Directory. Note that this is a static data extracted as of September 25th, 2024.")

# Load data
metrics_data = load_code_metrics_data()

project_count = len(metrics_data)
total_repos = round(metrics_data['Repository Count'].sum())
total_contributors = round(metrics_data['Contributor Count'].sum())
new_contributors = round(metrics_data['New Contributor Count'].sum())
total_open_PR = round(metrics_data['# of Open PRs'].sum())
total_merged_PR = round(metrics_data['# of Merged PRs'].sum())
total_issues_opened = round(metrics_data['# of Issues Opened'].sum())
total_issues_closed = round(metrics_data['# of Issues Closed'].sum())

st.markdown(f"\n Overall, Thank ARB is helping support: \
            \n - {project_count} out of 84 projects with at least some recent OSS component to their work \
            \n - a total of {total_repos:,} Github repos \
            \n - {total_contributors:,} contributors over 6 months")

st.markdown(f"\n In the last 6 months, these {project_count} projects: \
            \n - Attracted {new_contributors:,} new contributors \
            \n - Closed over {total_issues_closed:,} issues (and created {total_issues_opened:,} new ones) \
            \n - Merged over {total_merged_PR:,} pull requests (and opened {total_open_PR:,} new ones)")

overall_summary, onchain_metrics, code_metrics = st.tabs(["Overall Summary", "Onchain Transactions", "Code Metrics"])

with code_metrics:
    st.markdown("### What are the top projects based on development activities in the last 6 months?")
    st.markdown("""
    The Development Activity Index is a custom metric designed to measure the overall coding activity of a project. \
    This index helps identify projects with high levels of coding activity, which can be an indicator of project health, \
    community engagement, and ongoing development. However, it's important to consider this alongside other factors like project goals, \
    maturity, and specific grant objectives.
    """)

    with st.expander("Understanding the Development Activity Index 👇"):
        st.markdown("""
            The composite index combines three key indicators of development activity:
            
            1. **Code Commits** (50% weight): The number of code changes submitted to the project.
            2. **Merged Pull Requests** (30% weight): The number of code contributions successfully integrated into the project.
            3. **Active Developer Count** (20% weight): The number of developers actively working on the project.
            
            **How it's calculated:**
            1. We apply a logarithmic transformation to the commit count to balance the impact of projects with very high commit numbers.
            2. Each metric is normalized to ensure fair comparison across projects of different sizes and activity levels.
            3. The normalized metrics are then combined using the weights shown above.
            4. The final score is scaled to a 0-100 range for easier interpretation.
            
            **Interpreting the Index:**
            - A higher score indicates more development activity.
            - Scores are relative within this group of projects, not absolute measures.
            - A low score doesn't necessarily mean a project is inactive; it might be in a stable phase or have a different development model.
            """)
    
    st.info("""
    **Note on Development Activity Index:** The Development Activity Index is a proposed custom composite metric tailored to reflect coding activities. Depending on grant objectives, different combinations of metrics might be employed to more accurately evaluate grantee performance.
    """)
    
    # Analyze top performers
    top_performers = metrics_data.sort_values(by='Development Activity Index', ascending=False).head(5)
    
    # Projects with increasing new contributors
    emerging_projects = metrics_data[metrics_data['New Contributor Count'] > 0].sort_values(by='New Contributor Count', ascending=False).head(5)
    
    st.markdown("**Key insights:**")
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
    display_data = metrics_data[columns_to_display]
    
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
    metrics_data['Last Commit'] = pd.to_datetime(metrics_data['Last Commit'], format='%Y-%m-%d %H:%M:%S%z')
    inactive_projects = metrics_data[metrics_data['Last Commit'] < three_months_ago]
    
    # Sort inactive projects by last commit date
    inactive_projects = inactive_projects.sort_values('Last Commit')
    
    # Display the list of inactive projects
    st.markdown("**Other notes:**")
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
    metrics_data['Activity per Developer'] = metrics_data['Development Activity Index'] / metrics_data['Active Developer Count']
    
    # Sort the data by the ratio in descending order
    sorted_data = metrics_data.sort_values('Activity per Developer', ascending=True)
    
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
        height=max(600, len(metrics_data) * 25),  # Adjust height based on number of projects
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

with onchain_metrics:
    onchain_data = pd.read_csv("./data/monthly transactions by projects.csv")

    st.markdown("""
    ### Which projects have gained most momentum in # of onchain transactions since July 1st, 2024?
    
    - **Logarithmic Scale**: The x-axis represents the transaction counts on a log scale. This compresses the range of values, making it easier to compare projects with very large or very small transaction counts.
    - **Before and After**: 
        - **Blue markers** represent transaction counts for each project before July 1st (April to June 2024).
        - **Green markers** represent transaction counts from July 1st, 2024 onward.
    - **Connecting Lines**:
        - **Gray lines** indicate projects where transaction counts increased or stayed the same after July 1st.
        - **Red lines** highlight projects that experienced a drop in transaction counts after July 1st.
    - **Sorting**: Projects are sorted by the percentage change in transaction count, with projects showing the largest positive changes at the top.
    """)

    
    # Create two separate dataframes, one for before and one for after July 1st
    df_before_july = onchain_data[onchain_data['month'] < '2024-07']
    df_after_july = onchain_data[onchain_data['month'] >= '2024-07']
    
    # Group by project and calculate total transaction count for both periods
    before_july_summary = df_before_july.groupby('project_name')['transaction_count'].sum().reset_index()
    after_july_summary = df_after_july.groupby('project_name')['transaction_count'].sum().reset_index()
    
    # Merge the two summaries into one dataframe
    merged_summary = pd.merge(before_july_summary, after_july_summary, on='project_name', how='outer', suffixes=('_before_july', '_after_july')).fillna(0)
    
    # Calculate percentage change ((after - before) / before) * 100
    merged_summary['pct_change'] = ((merged_summary['transaction_count_after_july'] - merged_summary['transaction_count_before_july']) / 
                                    merged_summary['transaction_count_before_july'].replace(0, 1)) * 100
    
    # Sort the data by percentage change in descending order (highest to lowest)
    merged_summary = merged_summary.sort_values(by='pct_change', ascending=False)
    
    # Identify projects with drops (transaction count after July is less than before July)
    merged_summary['dropped'] = merged_summary['transaction_count_after_july'] < merged_summary['transaction_count_before_july']
    
    # Create the dumbbell plot
    fig = go.Figure()
    
    # Add 1 to avoid log(0) errors (since log scale cannot handle zero values)
    merged_summary['transaction_count_before_july'] = merged_summary['transaction_count_before_july'] + 1
    merged_summary['transaction_count_after_july'] = merged_summary['transaction_count_after_july'] + 1
    
    # Add "before July" points
    fig.add_trace(go.Scatter(
        x=merged_summary['transaction_count_before_july'],
        y=merged_summary['project_name'],
        mode='markers',
        name='Apr to June 2024',
        marker=dict(color='blue', size=10, opacity=0.7),  # Opacity to maintain distinction
        hovertext=merged_summary['project_name']
    ))
    
    # Add "after July" points
    fig.add_trace(go.Scatter(
        x=merged_summary['transaction_count_after_july'],
        y=merged_summary['project_name'],
        mode='markers',
        name='From July 1st, 2024',
        marker=dict(color='green', size=10, opacity=0.7),
        hovertext=merged_summary['project_name']
    ))
    
    # Add lines connecting the two points, red lines for projects with drops
    for i in range(len(merged_summary)):
        line_color = 'red' if merged_summary['dropped'].iloc[i] else 'gray'
        fig.add_shape(type='line',
                      x0=merged_summary['transaction_count_before_july'].iloc[i],
                      y0=i,
                      x1=merged_summary['transaction_count_after_july'].iloc[i],
                      y1=i,
                      line=dict(color=line_color, width=2))
    
    # Update layout with two x-axes (top and bottom) and logarithmic scale
    fig.update_layout(
        title='Dumbbell Plot of Transaction Count Before and After July 1st, 2024 by Project (Log Scale)',
        xaxis=dict(
            title='Transaction Count (Log Scale)',
            type='log',
            side='bottom',  # Set the first x-axis on the bottom
            mirror='allticks',  # Ensure that tick marks and labels are mirrored
        ),
        
        yaxis=dict(
            title='Projects (Sorted by % Change)',
            autorange="reversed"  # Reverse the Y-axis to show descending order
        ),
        height=len(merged_summary) * 40 + 400,  # Adjust height based on the number of projects
        hovermode='y unified'
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

with overall_summary:
    summary = pd.read_csv("./data/Info by program.csv")

    # Merge summary with metrics_data
    merged_data = pd.merge(summary, 
                        metrics_data[['Project Key', 'Development Activity Index', 'Last Commit']], 
                        left_on='project_name', 
                        right_on='Project Key', 
                        how='left')

    # If you want to drop the redundant 'Project Key' column after merging
    merged_data = merged_data.drop('Project Key', axis=1)

    # Rename 'Project Name' to 'OSO Project Name' and fill blank values
    merged_data = merged_data.rename(columns={'Project Name': 'OSO Project Name'})
    merged_data['OSO Project Name'] = merged_data['OSO Project Name'].fillna('No Data')

    # Format Development Activity Index without decimal
    merged_data['Development Activity Index'] = merged_data['Development Activity Index'].apply(lambda x: f"{x:.0f}" if pd.notnull(x) else 'No Data')

    # Update Last Commit to show days ago
    def days_ago(date_string):
        if pd.isnull(date_string) or date_string == 'No data':
            return 'No Data'
        try:
            commit_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S%z')
            days = (datetime.now(commit_date.tzinfo) - commit_date).days
            return f"{days} days ago"
        except ValueError:
            return 'Invalid Date'

    merged_data['Last Commit'] = merged_data['Last Commit'].apply(days_ago)

    # Display the dataframe
    st.dataframe(
        merged_data,
        use_container_width=True,
        hide_index=True
    )
