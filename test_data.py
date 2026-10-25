import pandas as pd

df = pd.read_csv("data/city_hour.csv")

# ============================================================
# 1. CITY MATRIX COUNT
# ============================================================

print("\n--- CITY COUNT ---")
print("Total unique cities:", df["City"].nunique())
print(df["City"].value_counts().sort_index())


# ============================================================
# 2. RAW DATETIME PROFILE
# ============================================================

print("\n--- DATETIME PROFILE ---")
print("Data type:", df["Datetime"].dtype)
print("First value:", df["Datetime"].iloc[0])
print("Last value:", df["Datetime"].iloc[-1])


# ============================================================
# 3. PM2.5 BASELINE
# ============================================================

print("\n--- PM2.5 MISSING DATA ---")
print("Total rows:", len(df))
print("PM2.5 missing rows:", df["PM2.5"].isna().sum())
print("PM2.5 available rows:", df["PM2.5"].notna().sum())


# ============================================================
# 4. COLUMN PROFILE
# ============================================================

print("\n--- COLUMN PROFILE ---")

profile = pd.DataFrame({
    "Data_Type": df.dtypes.astype(str),
    "Missing_Count": df.isna().sum(),
    "Missing_Percentage": (df.isna().mean() * 100).round(2)
})

print(profile)


# ============================================================
# 5. DUPLICATE ROW CHECK
# ============================================================

print("\n--- DUPLICATE ROW CHECK ---")
print("Duplicate rows:", df.duplicated().sum())


# ============================================================
# 6. RAW DATETIME UNIQUENESS
# ============================================================

print("\n--- DATETIME UNIQUENESS ---")
print("Total datetime values:", df["Datetime"].count())
print("Unique datetime values:", df["Datetime"].nunique())


# ============================================================
# 7. DATETIME CONVERSION
# ============================================================

df["Datetime"] = pd.to_datetime(df["Datetime"])

print("\n--- CONVERTED DATETIME PROFILE ---")
print("Data type:", df["Datetime"].dtype)


# ============================================================
# 8. CITY-WISE TIME GAP ANALYSIS
# ============================================================

df = df.sort_values(["City", "Datetime"])

df["Time_Diff"] = df.groupby("City")["Datetime"].diff()

print("\n--- CITY-WISE TIME GAP ANALYSIS ---")

gap_counts = (
    df.groupby(["City", "Time_Diff"])
      .size()
      .reset_index(name="Count")
)

print(gap_counts.to_string(index=False))


# ============================================================
# 9. CITY-WISE NON-1-HOUR GAPS
# ============================================================

print("\n--- NON-1-HOUR GAPS BY CITY ---")

non_hourly = df[
    df["Time_Diff"].notna() &
    (df["Time_Diff"] != pd.Timedelta(hours=1))
]

non_hourly_summary = (
    non_hourly.groupby("City")
    .agg(
        Non_Hourly_Gaps=("Time_Diff", "count"),
        Largest_Gap=("Time_Diff", "max")
    )
    .sort_values("Non_Hourly_Gaps", ascending=False)
)

print(non_hourly_summary)


# ============================================================
# 10. CITY-WISE RECORD SUMMARY
# ============================================================

print("\n--- CITY-WISE RECORD SUMMARY ---")

city_summary = (
    df.groupby("City")
    .agg(
        Records=("Datetime", "size"),
        Start=("Datetime", "min"),
        End=("Datetime", "max"),
        PM25_Available=("PM2.5", "count"),
        PM25_Missing=("PM2.5", lambda x: x.isna().sum())
    )
)

print(city_summary)


# ============================================================
# 11. FINAL DATASET SHAPE
# ============================================================

print("\n--- FINAL DATASET SHAPE ---")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# 12. PM2.5 CITY-WISE MISSINGNESS
print("\n--- PM2.5 CITY-WISE MISSINGNESS ---")

pm25_city = (
    df.groupby("City")["PM2.5"]
    .agg(
        Total_Rows="size",
        Missing_Count=lambda x: x.isna().sum(),
        Available_Count=lambda x: x.notna().sum()
    )
)

pm25_city["Missing_Percentage"] = (
    pm25_city["Missing_Count"] / pm25_city["Total_Rows"] * 100
).round(2)

print(pm25_city.sort_values("Missing_Percentage", ascending=False))


# 13. CONSECUTIVE PM2.5 MISSING RUNS
print("\n--- CONSECUTIVE PM2.5 MISSING RUNS ---")

df["PM25_Missing"] = df["PM2.5"].isna()

df["Missing_Group"] = (
    df.groupby("City")["PM25_Missing"]
    .transform(lambda x: x.ne(x.shift()).cumsum())
)

missing_runs = (
    df[df["PM25_Missing"]]
    .groupby(["City", "Missing_Group"])
    .size()
    .reset_index(name="Missing_Hours")
)

print("Total missing runs:", len(missing_runs))


# 14. MISSING RUN DISTRIBUTION
print("\n--- MISSING RUN DISTRIBUTION ---")

def classify_run(hours):
    if hours == 1:
        return "1 hour"
    elif hours == 2:
        return "2 hours"
    elif hours == 3:
        return "3 hours"
    elif 4 <= hours <= 6:
        return "4-6 hours"
    elif 7 <= hours <= 23:
        return "7-23 hours"
    elif 24 <= hours <= 99:
        return "24-99 hours"
    else:
        return "100+ hours"

missing_runs["Run_Category"] = (
    missing_runs["Missing_Hours"].apply(classify_run)
)

run_distribution = (
    missing_runs["Run_Category"]
    .value_counts()
    .reindex(
        [
            "1 hour",
            "2 hours",
            "3 hours",
            "4-6 hours",
            "7-23 hours",
            "24-99 hours",
            "100+ hours"
        ],
        fill_value=0
    )
)

print(run_distribution)


# 15. MAXIMUM CONSECUTIVE MISSING HOURS BY CITY
print("\n--- MAX CONSECUTIVE PM2.5 MISSING HOURS BY CITY ---")

max_missing = (
    missing_runs.groupby("City")["Missing_Hours"]
    .max()
    .sort_values(ascending=False)
)

print(max_missing)


# 16. CITY-WISE MISSING RUN SUMMARY
print("\n--- CITY-WISE MISSING RUN SUMMARY ---")

run_summary = (
    missing_runs.groupby("City")
    .agg(
        Total_Missing_Runs=("Missing_Hours", "count"),
        Max_Missing_Hours=("Missing_Hours", "max"),
        Avg_Missing_Run=("Missing_Hours", "mean")
    )
    .sort_values("Max_Missing_Hours", ascending=False)
)

run_summary["Avg_Missing_Run"] = run_summary["Avg_Missing_Run"].round(2)

print(run_summary)


# 17. FINAL PM2.5 MISSINGNESS SUMMARY
print("\n--- FINAL PM2.5 SUMMARY ---")

print("Total PM2.5 missing:", df["PM2.5"].isna().sum())
print("Total PM2.5 available:", df["PM2.5"].notna().sum())
print(
    "Overall PM2.5 missing percentage:",
    round(df["PM2.5"].isna().mean() * 100, 2),
)

# 18. PREDICTOR MISSINGNESS
print("\n--- PREDICTOR MISSINGNESS ---")

predictor_columns = [
    "PM10", "NO", "NO2", "NOx", "NH3",
    "CO", "SO2", "O3", "Benzene",
    "Toluene", "Xylene"
]

predictor_profile = pd.DataFrame({
    "Missing_Count": df[predictor_columns].isna().sum(),
    "Missing_Percentage": (
        df[predictor_columns].isna().mean() * 100
    ).round(2),
    "Available_Count": df[predictor_columns].notna().sum()
})

print(
    predictor_profile
    .sort_values("Missing_Percentage", ascending=False)
)


# 19. ROW-WISE PREDICTOR AVAILABILITY
print("\n--- PREDICTOR AVAILABILITY PER ROW ---")

df["Available_Predictors"] = (
    df[predictor_columns].notna().sum(axis=1)
)

availability = (
    df["Available_Predictors"]
    .value_counts()
    .sort_index()
)

print(availability)


# 20. COMPLETE PREDICTOR ROWS
print("\n--- COMPLETE PREDICTOR ROWS ---")

complete_rows = (
    df[predictor_columns]
    .notna()
    .all(axis=1)
)

print("Rows with all predictors available:", complete_rows.sum())
print("Rows with at least one predictor missing:", (~complete_rows).sum())
print(
    "Complete predictor percentage:",
    round(complete_rows.mean() * 100, 2)
)


# 21. TARGET + PREDICTOR AVAILABILITY
print("\n--- PM2.5 + PREDICTOR AVAILABILITY ---")

target_available = df["PM2.5"].notna()

target_predictor_complete = (
    target_available & complete_rows
)

print(
    "PM2.5 + all predictors available:",
    target_predictor_complete.sum()
)

print(
    "PM2.5 + all predictors percentage:",
    round(target_predictor_complete.mean() * 100, 2)
)

# 22. PM2.5 STATISTICAL PROFILE
print("\n--- PM2.5 STATISTICAL PROFILE ---")

print(
    df["PM2.5"].describe(
        percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
    )
)


# 23. PM2.5 ZERO AND NEGATIVE VALUES
print("\n--- PM2.5 INVALID VALUES ---")

print("Zero values:", (df["PM2.5"] == 0).sum())
print("Negative values:", (df["PM2.5"] < 0).sum())


# 24. PM2.5 OUTLIER ANALYSIS USING IQR
print("\n--- PM2.5 IQR OUTLIER ANALYSIS ---")

pm25_valid = df["PM2.5"].dropna()

Q1 = pm25_valid.quantile(0.25)
Q3 = pm25_valid.quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = pm25_valid[
    (pm25_valid < lower_bound) |
    (pm25_valid > upper_bound)
]

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower Bound:", lower_bound)
print("Upper Bound:", upper_bound)
print("Outlier Count:", len(outliers))
print(
    "Outlier Percentage:",
    round(len(outliers) / len(pm25_valid) * 100, 2)
)


# 25. EXTREME PM2.5 VALUES
print("\n--- EXTREME PM2.5 VALUES ---")

print("Minimum:", pm25_valid.min())
print("Maximum:", pm25_valid.max())

print("\nTop 10 highest PM2.5 values:")
print(
    df[["City", "Datetime", "PM2.5"]]
    .dropna(subset=["PM2.5"])
    .nlargest(10, "PM2.5")
    .to_string(index=False)
)


# 26. PM2.5 CITY-WISE STATISTICS
print("\n--- CITY-WISE PM2.5 STATISTICS ---")

city_pm25_stats = (
    df.groupby("City")["PM2.5"]
    .agg(
        Mean="mean",
        Median="median",
        Minimum="min",
        Maximum="max"
    )
    .round(2)
    .sort_values("Mean", ascending=False)
)

print(city_pm25_stats)

# 27. TIME-BASED PM2.5 ANALYSIS
print("\n--- TIME-BASED PM2.5 ANALYSIS ---")

# Extract temporal features
df["Hour"] = df["Datetime"].dt.hour
df["Month"] = df["Datetime"].dt.month
df["DayOfWeek"] = df["Datetime"].dt.dayofweek


# 28. HOURLY PM2.5 PATTERN
print("\n--- HOURLY PM2.5 PATTERN ---")

hourly_pm25 = (
    df.groupby("Hour")["PM2.5"]
    .agg(
        Mean="mean",
        Median="median",
        Count="count"
    )
    .round(2)
)

print(hourly_pm25)


# 29. MONTHLY PM2.5 PATTERN
print("\n--- MONTHLY PM2.5 PATTERN ---")

monthly_pm25 = (
    df.groupby("Month")["PM2.5"]
    .agg(
        Mean="mean",
        Median="median",
        Count="count"
    )
    .round(2)
)

print(monthly_pm25)


# 30. DAY-OF-WEEK PM2.5 PATTERN
print("\n--- DAY-OF-WEEK PM2.5 PATTERN ---")

day_names = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

daily_pm25 = (
    df.groupby("DayOfWeek")["PM2.5"]
    .agg(
        Mean="mean",
        Median="median",
        Count="count"
    )
    .round(2)
)

daily_pm25.index = daily_pm25.index.map(day_names)

print(daily_pm25)


# 31. CITY-WISE MONTHLY PATTERN
print("\n--- CITY-WISE MONTHLY PM2.5 PATTERN ---")

city_monthly_pm25 = (
    df.groupby(["City", "Month"])["PM2.5"]
    .mean()
    .round(2)
)

print(city_monthly_pm25)


# 32. TEMPORAL FEATURE CHECK
print("\n--- TEMPORAL FEATURE CHECK ---")

print(
    df[
        ["Datetime", "Hour", "Month", "DayOfWeek"]
    ].head(10)
)