# 🎓 Student Academic Risk Intelligence System

A Python-based student performance analysis and academic risk intelligence system built using the **UCI Student Performance dataset**.

The system analyzes student academic performance, identifies at-risk students, provides result predictions, and presents insights through a Streamlit dashboard and FastAPI REST API.

## 🚀 Features

* Student academic performance analysis
* Feature engineering from raw student data
* Student result classification:

  * **Dropout** → G3 = 0
  * **Fail** → G3 = 1–9
  * **Pass** → G3 = 10–20
* Academic risk score calculation
* Class performance statistics
* At-risk student identification
* Top-performing student identification
* Static charts using Matplotlib
* Interactive charts using Plotly
* REST API using FastAPI
* Interactive dashboard using Streamlit
* Student result prediction API
* Input validation using Pydantic

## 🛠️ Technologies Used

* **Python**
* **Pandas** – Data loading and feature engineering
* **NumPy** – Statistical calculations
* **Matplotlib** – Static visualizations
* **Plotly** – Interactive visualizations
* **FastAPI** – REST API
* **Pydantic** – Input validation
* **Uvicorn** – API server
* **Streamlit** – Interactive dashboard

## 📁 Project Structure

```text
Student-Risk-Analysis-System/
│
├── data/
│   └── Maths.csv
│
├── output/
│   ├── avg_g3_by_studytime.png
│   └── pass_fail_dropout_pie.png
│
├── analysis.py
├── main.py
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation

Clone or download the project and open a terminal inside the project folder.

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## 📊 Run Data Analysis

Run:

```bash
python analysis.py
```

This performs feature engineering, calculates statistics, and generates static and interactive visualizations.

Static charts are saved in the `output/` folder.

## 🌐 Run FastAPI

Start the REST API using:

```bash
python main.py
```

The API will run on:

```text
http://127.0.0.1:8000
```

### API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

### Available Endpoints

| Method | Endpoint          | Description                         |
| ------ | ----------------- | ----------------------------------- |
| GET    | `/`               | API information                     |
| GET    | `/summary`        | Overall student performance summary |
| GET    | `/at-risk`        | List of at-risk students            |
| GET    | `/top-students`   | Top 5 students by G3                |
| POST   | `/predict-result` | Predict student academic result     |

## 📈 Run Streamlit Dashboard

Start the dashboard using:

```bash
streamlit run app.py
```

The dashboard provides:

* KPI metrics
* Performance charts
* Student analysis table
* Result filtering
* At-risk student analysis

## 🧮 Feature Engineering

The system creates the following derived features:

* **Result** – Student result category based on G3
* **Percentage** – Final grade converted to percentage
* **avg_alcohol** – Average of weekday and weekend alcohol consumption
* **parent_edu_avg** – Average education level of parents
* **grade_trend** – Difference between G3 and G1
* **total_support** – Number of support-related factors marked as yes
* **risk_score** – Calculated academic risk indicator
* **g1_g2_avg** – Average of G1 and G2

## 🎯 Academic Risk Classification

| G3 Range | Classification |
| -------- | -------------- |
| 0        | Dropout        |
| 1–9      | Fail / At-Risk |
| 10–20    | Pass           |

For pass-rate calculations, **dropout students (G3 = 0) are excluded**.

## 🔮 Result Prediction

The `/predict-result` API accepts:

* G1
* G2
* Study time
* Absences
* Previous failures

It calculates an estimated G3 score and returns:

* Estimated G3
* Prediction
* Confidence level

## 📌 Dataset

The project uses the **UCI Student Performance dataset – Mathematics (`Maths.csv`)**.

The dataset contains academic, demographic, family, lifestyle, and school-related information about students.

## 👩‍💻 Project

**Student Academic Risk Intelligence System**

Built as a Python data analysis, REST API, and dashboard project.
