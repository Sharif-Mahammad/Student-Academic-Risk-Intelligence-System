import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import os
def load_and_prepare_data(filepath):
    # Load the dataset from the given CSV file path
    df = pd.read_csv("data/maths.csv")

    # Create Result based on the final grade (G3)
    # G3 = 0 is treated as Dropout, not as a normal zero score
    df["Result"] = df["G3"].apply(
        lambda x: "Dropout" if x == 0 else ("Fail" if 1 <= x <= 9 else "Pass")
    )

    # Convert the final grade (G3) into percentage
    df["Percentage"] = (df["G3"] / 20) * 100

    # Calculate average alcohol consumption from weekday and weekend values
    df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

    # Calculate the average education level of both parents
    df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

    # Calculate the change in grade from the first period to the final grade
    df["grade_trend"] = df["G3"] - df["G1"]

    # Count the number of "yes" values across school support,
    # family support, and paid extra classes
    df["total_support"] = (
        df[["schoolsup", "famsup", "paid"]]
        .eq("yes")
        .sum(axis=1)
    )

    # Calculate the academic risk score
    # Higher failures, absences, and alcohol consumption increase risk,
    # while higher study time reduces risk
    df["risk_score"] = (
        (df["failures"] * 2)
        + (df["absences"] / 10)
        + df["avg_alcohol"]
        - df["studytime"]
    )

    # Calculate the average of first and second period grades
    df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2

    # Return the complete prepared DataFrame
    return df

def calculate_statistics(df):
    # Exclude students with G3 = 0 (dropouts) for academic performance calculations
    non_dropout_df = df[df["G3"] != 0]

    # Calculate the average final grade (G3) of non-dropout students
    class_avg_g3 = np.mean(non_dropout_df["G3"])

    # Calculate the pass rate among non-dropout students
    # Students with G3 >= 10 are considered to have passed
    passed_students = np.sum(non_dropout_df["G3"] >= 10)
    total_non_dropout = len(non_dropout_df)

    pass_rate = (passed_students / total_non_dropout) * 100

    # Count the total number of students who dropped out (G3 = 0)
    dropout_count = np.sum(df["G3"] == 0)

    # Count students who are at risk (G3 between 1 and 9)
    at_risk_count = np.sum((df["G3"] >= 1) & (df["G3"] <= 9))

    # Calculate the correlation matrix for G1, G2, and G3
    # Only non-dropout students are included
    correlation_matrix = np.corrcoef(
        non_dropout_df[["G1", "G2", "G3"]].values.T
    )

    # Return all calculated statistics as a dictionary
    return {
        "class_avg_g3": class_avg_g3,
        "pass_rate": pass_rate,
        "dropout_count": dropout_count,
        "at_risk_count": at_risk_count,
        "correlation_matrix": correlation_matrix
    }

def generate_static_charts(df):
    # Import os to create the output directory if it does not exist
    import os

    # Create the output folder if it does not already exist
    os.makedirs("output", exist_ok=True)

    # -------------------------------
    # Chart 1: Average G3 by Study Time
    # -------------------------------

    # Calculate the average G3 for each studytime level (1, 2, 3, 4)
    avg_g3 = df.groupby("studytime")["G3"].mean().reindex([1, 2, 3, 4])

    # Create the bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(avg_g3.index, avg_g3.values)

    # Add chart title and axis labels
    plt.title("Average G3 by Study Time")
    plt.xlabel("Study Time (1=<2hrs, 2=2-5hrs, 3=5-10hrs, 4=>10hrs)")
    plt.ylabel("Average G3")

    # Set the studytime levels on the X axis
    plt.xticks([1, 2, 3, 4])

    # Save the bar chart
    plt.savefig("output/avg_g3_by_studytime.png", bbox_inches="tight")

    # Close the chart to release memory
    plt.close()

    # -------------------------------
    # Chart 2: Student Result Distribution
    # -------------------------------

    # Count the number of students in each result category
    result_counts = df["Result"].value_counts().reindex(
        ["Pass", "Fail", "Dropout"], fill_value=0
    )

    # Create the pie chart
    plt.figure(figsize=(7, 7))
    plt.pie(
        result_counts.values,
        labels=result_counts.index,
        autopct="%1.1f%%"
    )

    # Add chart title
    plt.title("Student Result Distribution")

    # Save the pie chart
    plt.savefig("output/pass_fail_dropout_pie.png", bbox_inches="tight")

    # Close the chart to release memory
    plt.close()

def generate_interactive_charts(df):
    # Create the interactive scatter plot
    fig1 = px.scatter(
        df,
        x="studytime",
        y="G3",
        color="Result",
        hover_data=["absences", "G1", "G2"],
        title="Study Time vs Final Grade (G3)",
        color_discrete_map={
            "Pass": "green",
            "Fail": "red",
            "Dropout": "grey"
        }
    )

    # Display the interactive scatter plot
    fig1.show()

    # Calculate the average G3 for each internet access group
    avg_g3_internet = (
        df.groupby("internet")["G3"]
        .mean()
        .reset_index()
    )

    # Create the interactive bar chart
    fig2 = px.bar(
        avg_g3_internet,
        x="internet",
        y="G3",
        color="internet",
        title="Average G3 by Internet Access"
    )

    # Display the interactive bar chart
    fig2.show()

def print_summary(stats):
    # Print the formatted analysis summary
    print("=" * 48)
    print("STUDENT ACADEMIC RISK INTELLIGENCE SYSTEM")
    print()
    print("ANALYSIS SUMMARY")
    print("=" * 48)

    # Print the total number of students
    print(f"Total Students        : {stats.get('total_students', 'N/A')}")

    # Print the average final grade
    print(f"Class Average G3      : {stats['class_avg_g3']:.2f}")

    # Print the pass rate
    print(f"Pass Rate             : {stats['pass_rate']:.2f}%")

    # Print the number of at-risk students
    print(f"At-Risk Count         : {stats['at_risk_count']}")

    # Print the number of dropout students
    print(f"Dropout Count         : {stats['dropout_count']}")

    print("=" * 48)


# Main block: execute the complete analysis pipeline
if __name__ == "__main__":
    # Load and prepare the student dataset
    df = load_and_prepare_data("data/Maths.csv")

    # Calculate statistical information from the prepared data
    stats = calculate_statistics(df)

    # Store the total number of students for the summary
    stats["total_students"] = len(df)

    # Generate and save the static Matplotlib charts
    generate_static_charts(df)

    # Generate and display the interactive Plotly charts
    generate_interactive_charts(df)

    # Print the formatted analysis summary
    print_summary(stats)

    # Confirm that the analysis has completed
    print("Analysis complete. Charts saved to output/ folder")