# Import required libraries
from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import uvicorn


# Create the FastAPI application
app = FastAPI(
    title="Student Academic Risk Intelligence System API",
    description="API for analyzing student performance data",
    version="1.0.0"
)


# Function to load and prepare student data
def load_data():
    # Load the Maths.csv dataset from the data folder
    df = pd.read_csv("data/maths.csv")

    # Create Result based on final grade G3
    # G3 = 0       -> Dropout
    # G3 = 1 to 9  -> Fail
    # G3 = 10 to 20 -> Pass
    df["Result"] = np.where(
        df["G3"] == 0,
        "Dropout",
        np.where(df["G3"] < 10, "Fail", "Pass")
    )

    # Convert G3 into percentage
    df["Percentage"] = (df["G3"] / 20) * 100

    # Calculate average alcohol consumption
    df["avg_alcohol"] = (df["Dalc"] + df["Walc"]) / 2

    # Calculate average education level of parents
    df["parent_edu_avg"] = (df["Medu"] + df["Fedu"]) / 2

    # Calculate the improvement or decline from G1 to G3
    df["grade_trend"] = df["G3"] - df["G1"]

    # Count the number of "yes" values across support-related columns
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

    # Calculate average of first and second period grades
    df["g1_g2_avg"] = (df["G1"] + df["G2"]) / 2

    # Return the completely prepared DataFrame
    return df


# Load the dataset when the application starts
df = load_data()

# ============================================================
# Endpoint 1: GET /summary
# Returns overall academic performance summary
# ============================================================

@app.get("/summary")
def get_summary():
    # Total number of students
    total_students = len(df)

    # Select only non-dropout students (G3 != 0)
    non_dropout = df[df["G3"] != 0]

    # Calculate average G3 for non-dropout students
    class_average_g3 = round(non_dropout["G3"].mean(), 2)

    # Calculate number of students who passed (G3 >= 10)
    pass_count = len(non_dropout[non_dropout["G3"] >= 10])

    # Calculate pass rate among non-dropout students only
    pass_rate_percent = round(
        (pass_count / len(non_dropout)) * 100, 2
    )

    # Count students at risk (G3 between 1 and 9)
    at_risk_count = len(df[(df["G3"] >= 1) & (df["G3"] <= 9)])

    # Count dropouts (G3 = 0)
    dropout_count = len(df[df["G3"] == 0])

    # Return the summary as JSON
    return {
        "total_students": int(total_students),
        "class_average_g3": float(class_average_g3),
        "pass_rate_percent": float(pass_rate_percent),
        "at_risk_count": int(at_risk_count),
        "dropout_count": int(dropout_count)
    }


# ============================================================
# Endpoint 2: GET /at-risk
# Returns students whose G3 is between 1 and 9
# ============================================================

@app.get("/at-risk")
def get_at_risk_students():
    # Filter students with G3 between 1 and 9
    at_risk = df[
        (df["G3"] >= 1) &
        (df["G3"] <= 9)
    ].copy()

    # Sort by G3 ascending so the lowest grades appear first
    at_risk = at_risk.sort_values(by="G3", ascending=True)

    # Create the required response format
    result = []

    for index, student in at_risk.iterrows():
        result.append({
            "student_index": int(index),
            "G1": int(student["G1"]),
            "G2": int(student["G2"]),
            "G3": int(student["G3"]),
            "absences": int(student["absences"])
        })

    # Return the list of at-risk students
    return result


# ============================================================
# Endpoint 3: GET /top-students
# Returns the top 5 students by G3, excluding dropouts
# ============================================================

@app.get("/top-students")
def get_top_students():
    # Select only non-dropout students
    non_dropout = df[df["G3"] != 0].copy()

    # Sort students by G3 in descending order
    # and select only the top 5
    top_students = non_dropout.sort_values(
        by="G3",
        ascending=False
    ).head(5)

    # Create the required response format
    result = []

    for index, student in top_students.iterrows():
        result.append({
            "student_index": int(index),
            "G1": int(student["G1"]),
            "G2": int(student["G2"]),
            "G3": int(student["G3"])
        })

    # Return the top 5 students
    return result
# ============================================================
# Pydantic Model: StudentInput
# Validates student information received by the API
# ============================================================

class StudentInput(BaseModel):
    # First period grade: must be between 0 and 20
    G1: float = Field(
        ...,
        ge=0,
        le=20,
        description="G1 must be between 0 and 20"
    )

    # Second period grade: must be between 0 and 20
    G2: float = Field(
        ...,
        ge=0,
        le=20,
        description="G2 must be between 0 and 20"
    )

    # Study time level: must be between 1 and 4
    studytime: int = Field(
        ...,
        ge=1,
        le=4,
        description="Study time must be between 1 and 4"
    )

    # Number of absences: must be between 0 and 100
    absences: int = Field(
        ...,
        ge=0,
        le=100,
        description="Absences must be between 0 and 100"
    )

    # Number of previous failures: must be between 0 and 4
    failures: int = Field(
        ...,
        ge=0,
        le=4,
        description="Failures must be between 0 and 4"
    )


# ============================================================
# Endpoint: POST /predict-result
# Predicts the student's academic result
# ============================================================

@app.post("/predict-result")
def predict_result(student: StudentInput):

    # Calculate estimated G3 using the given formula
    estimated_g3 = (
        (student.G1 * 0.3)
        + (student.G2 * 0.6)
        + (student.studytime * 0.3)
        - (student.failures * 1.5)
        - (student.absences * 0.05)
    )

    # Clamp estimated G3 between 0 and 20
    estimated_g3 = max(0, min(20, estimated_g3))

    # Determine the predicted result
    if estimated_g3 == 0:
        prediction = "Dropout Risk"
    elif estimated_g3 < 10:
        prediction = "Fail"
    else:
        prediction = "Pass"

    # Determine prediction confidence
    # High confidence when both grades are above 12
    # OR both grades are below 8
    if (student.G1 > 12 and student.G2 > 12) or \
       (student.G1 < 8 and student.G2 < 8):
        confidence = "High"
    else:
        confidence = "Medium"

    # Return the prediction details as JSON
    return {
        "estimated_g3": round(estimated_g3, 2),
        "prediction": prediction,
        "confidence": confidence
    }
# ============================================================
# Root Endpoint: GET /
# Provides basic information about the API
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Student Academic Risk Intelligence System API",
        "docs": "Visit /docs for full API documentation",
        "version": "1.0.0"
    }


# ============================================================
# Main Block
# Starts the FastAPI application using Uvicorn
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )