# ============================================================
# Student Academic Risk Intelligence System
# Streamlit Dashboard - Initial Setup
# ============================================================

# Import required libraries
import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Student Academic Risk Intelligence System",
    layout="wide",
    page_icon="🎓"
)


# ============================================================
# Load and Prepare Data
# ============================================================

# Load the Maths.csv dataset
df = pd.read_csv("data/maths.csv")


# Create Result based on final grade G3
# G3 = 0       -> Dropout
# G3 = 1 to 9  -> Fail
# G3 = 10 to 20 -> Pass
df["Result"] = df["G3"].apply(
    lambda x: "Dropout" if x == 0
    else "Fail" if x < 10
    else "Pass"
)


# Convert final grade into percentage
df["Percentage"] = (df["G3"] / 20) * 100


# Calculate average alcohol consumption
df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2


# Calculate average parent education level
df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2


# Calculate grade trend from G1 to G3
df["grade_trend"] = df["G3"] - df["G1"]


# Count the number of "yes" values in support-related columns
support_columns = ["schoolsup", "famsup", "paid"]

df["total_support"] = (
    df[support_columns]
    .apply(lambda row: (row == "yes").sum(), axis=1)
)


# Calculate academic risk score
df["risk_score"] = (
    (df["failures"] * 2)
    + (df["absences"] / 10)
    + df["avg_alcohol"]
    - df["studytime"]
)


# Calculate average of G1 and G2
df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2


# ============================================================
# Main Dashboard Title
# ============================================================

st.title("🎓 Student Academic Risk Intelligence System")


# ============================================================
# Calculate KPI Values
# ============================================================

# Total number of students
total_students = len(df)


# Select only non-dropout students
non_dropout = df[df["G3"] != 0]


# Calculate average G3 excluding dropouts
class_average_g3 = round(non_dropout["G3"].mean(), 2)


# Count students who passed
pass_count = len(non_dropout[non_dropout["G3"] >= 10])


# Calculate pass rate among non-dropout students
pass_rate = round(
    (pass_count / len(non_dropout)) * 100,
    1
)


# Count students with G3 between 1 and 9
at_risk_count = len(
    df[(df["G3"] >= 1) & (df["G3"] <= 9)]
)


# ============================================================
# KPI Cards
# ============================================================

# Create four columns so all KPI cards appear in one row
col1, col2, col3, col4 = st.columns(4)


# Card 1: Total Students
with col1:
    st.metric(
        label="Total Students",
        value=total_students
    )


# Card 2: Class Average G3
with col2:
    st.metric(
        label="Class Average G3",
        value=class_average_g3
    )


# Card 3: Pass Rate
with col3:
    st.metric(
        label="Pass Rate %",
        value=f"{pass_rate}%"
    )


# Card 4: At-Risk Count
with col4:
    st.metric(
        label="At-Risk Count",
        value=at_risk_count
    )
# ============================================================
# Performance Charts
# ============================================================

st.subheader("📊 Performance Charts")

# Create two columns so the charts appear side by side
chart_col1, chart_col2 = st.columns(2)


# ============================================================
# Left Chart - Study Time vs Final Grade
# ============================================================

with chart_col1:

    # Create scatter plot
    scatter_fig = px.scatter(
        df,
        x="studytime",
        y="G3",
        color="Result",
        hover_data=["absences", "G1", "G2"],
        title="Study Time vs Final Grade",
        color_discrete_map={
            "Pass": "green",
            "Fail": "red",
            "Dropout": "grey"
        }
    )

    # Display the scatter plot in Streamlit
    st.plotly_chart(
        scatter_fig,
        use_container_width=True
    )


# ============================================================
# Right Chart - Average G3 by Internet Access
# ============================================================

with chart_col2:

    # Calculate average G3 for each internet access group
    internet_avg = (
        df.groupby("internet", as_index=False)["G3"]
        .mean()
        .rename(columns={"G3": "Average G3"})
    )

    # Create bar chart
    bar_fig = px.bar(
        internet_avg,
        x="internet",
        y="Average G3",
        color="internet",
        title="Average G3 by Internet Access"
    )

    # Display the bar chart in Streamlit
    st.plotly_chart(
        bar_fig,
        use_container_width=True
    )
# ============================================================
# Student Analysis Table
# ============================================================

st.subheader("🚨 Student Analysis Table")


# Create a dropdown to filter students by their result
result_filter = st.selectbox(
    "Filter by Result",
    ["All", "Pass", "Fail", "Dropout"]
)


# Filter the DataFrame based on the selected result
if result_filter == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Result"] == result_filter].copy()


# Select only the required columns for the student table
student_columns = [
    "G1",
    "G2",
    "G3",
    "Result",
    "Percentage",
    "absences",
    "studytime",
    "failures",
    "risk_score"
]


# Display the filtered student DataFrame
st.dataframe(
    filtered_df[student_columns],
    use_container_width=True
)


# ============================================================
# At-Risk Students
# ============================================================

st.subheader("⚠️ At-Risk Students")


# Select students whose G3 is between 1 and 9
at_risk_df = df[
    (df["G3"] >= 1) &
    (df["G3"] <= 9)
].copy()


# Sort by G3 in ascending order
# Lowest G3 appears first (worst performing student)
at_risk_df = at_risk_df.sort_values(
    by="G3",
    ascending=True
)


# Select only the required columns
at_risk_columns = [
    "G1",
    "G2",
    "G3",
    "absences",
    "studytime",
    "failures"
]


# Display the total number of at-risk students
st.write(
    f"Total at-risk students: {len(at_risk_df)}"
)


# Display the at-risk student table
st.dataframe(
    at_risk_df[at_risk_columns],
    use_container_width=True
)