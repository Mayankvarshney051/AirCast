import pandas as pd


DATA_PATH = "data/city_hour.csv"

SELECTED_FEATURES = [
    "PM10",
    "NO",
    "NO2",
    "NOx",
    "NH3",
    "CO",
    "SO2",
    "O3"
]

ALL_POLLUTANTS = [
    "PM10",
    "NO",
    "NO2",
    "NOx",
    "NH3",
    "CO",
    "SO2",
    "O3",
    "Benzene",
    "Toluene",
    "Xylene"
]

TIME_FEATURES = [
    "Hour",
    "Month",
    "DayOfWeek"
]

LAG_FEATURES = [
    "PM2.5_lag_24",
    "PM2.5_lag_48"
]

TARGET = "PM2.5_target_24h"

def load_data():
    df = pd.read_csv(DATA_PATH)

    df["Datetime"] = pd.to_datetime(df["Datetime"])

    df = df.sort_values(
        ["City", "Datetime"]
    ).reset_index(drop=True)

    return df


def handle_pm25_missing(df):
    df = df.copy()

    df["PM2.5"] = (
        df.groupby("City")["PM2.5"]
        .transform(
            lambda x: x.interpolate(
                method="linear",
                limit=3,
                limit_area="inside"
            )
        )
    )

    return df


def create_time_features(df):
    df = df.copy()

    df["Hour"] = df["Datetime"].dt.hour
    df["Month"] = df["Datetime"].dt.month
    df["DayOfWeek"] = df["Datetime"].dt.day_of_week

    return df


def create_lag_and_target_features(df):
    df = df.copy()

    grouped_pm25 = df.groupby("City")["PM2.5"]

    df["PM2.5_lag_24"] = grouped_pm25.shift(24)

    df["PM2.5_lag_48"] = grouped_pm25.shift(48)

    df["PM2.5_target_24h"] = grouped_pm25.shift(-24)

    return df


def impute_selected_features(df):
    df = df.copy()

    for feature in SELECTED_FEATURES:
        df[feature] = (
            df.groupby("City")[feature]
            .transform(
                lambda x: x.fillna(x.median())
            )
        )

    for feature in SELECTED_FEATURES:
        overall_median = df[feature].median()

        df[feature] = df[feature].fillna(overall_median)

    return df


def create_model_dataset(df):
    df = df.copy()

    model_features = (
        SELECTED_FEATURES
        + TIME_FEATURES
        + LAG_FEATURES
    )

    required_columns = model_features + [TARGET]

    model_df = df[
        ["City", "Datetime"] + required_columns
    ].copy()

    model_df = model_df.dropna(
        subset=[
            "PM2.5_lag_24",
            "PM2.5_lag_48",
            TARGET
        ]
    )

    return model_df


def time_based_split(df):
    df = df.copy()

    split_date = df["Datetime"].quantile(0.80)

    train_df = df[
        df["Datetime"] <= split_date
    ].copy()

    test_df = df[
        df["Datetime"] > split_date
    ].copy()

    return train_df, test_df, split_date


def validate_lag_timestamps(df):
    validation = df[
        [
            "City",
            "Datetime"
        ]
    ].copy()

    validation["lag_24_datetime"] = (
        df.groupby("City")["Datetime"]
        .shift(24)
    )

    validation["lag_48_datetime"] = (
        df.groupby("City")["Datetime"]
        .shift(48)
    )

    validation["lag_24_hours"] = (
        validation["Datetime"]
        - validation["lag_24_datetime"]
    ).dt.total_seconds() / 3600

    validation["lag_48_hours"] = (
        validation["Datetime"]
        - validation["lag_48_datetime"]
    ).dt.total_seconds() / 3600

    valid_24 = validation["lag_24_hours"].dropna()
    valid_48 = validation["lag_48_hours"].dropna()

    lag_24_valid = (valid_24 == 24).all()
    lag_48_valid = (valid_48 == 48).all()

    return lag_24_valid, lag_48_valid


def validate_pipeline(
    df,
    model_df,
    train_df,
    test_df,
    split_date
):
    print("\n")
    print("=" * 60)
    print("FINAL PREPROCESSING VALIDATION")
    print("=" * 60)

    print("\n1. DATASET")
    print("Raw rows:", len(df))
    print("Raw columns:", len(df.columns))
    print("Cities:", df["City"].nunique())

    print("\n2. DATETIME")
    print("Datetime dtype:", df["Datetime"].dtype)
    print("First:", df["Datetime"].min())
    print("Last:", df["Datetime"].max())

    print("\n3. PM2.5")
    print(
        "Remaining PM2.5 missing:",
        df["PM2.5"].isna().sum()
    )

    print("\n4. SELECTED FEATURES")
    print(SELECTED_FEATURES)

    print("\nMissing values in selected features:")
    print(
        df[SELECTED_FEATURES]
        .isna()
        .sum()
    )

    print("\n5. TIME FEATURES")
    print(TIME_FEATURES)

    print("\n6. LAG VALIDATION")

    lag_24_valid, lag_48_valid = validate_lag_timestamps(df)

    print(
        "24-hour lag valid:",
        lag_24_valid
    )

    print(
        "48-hour lag valid:",
        lag_48_valid
    )

    print("\n7. MODEL DATASET")
    print("Rows:", len(model_df))
    print("Columns:", len(model_df.columns))

    print("\nModel features:")
    print(
        SELECTED_FEATURES
        + TIME_FEATURES
        + LAG_FEATURES
    )

    print("\nTarget:")
    print(TARGET)

    print("\n8. TRAIN / TEST SPLIT")
    print("Split date:", split_date)

    print("Training rows:", len(train_df))
    print("Testing rows:", len(test_df))

    print(
        "Training percentage:",
        round(
            len(train_df) / len(model_df) * 100,
            2
        ),
        "%"
    )

    print(
        "Testing percentage:",
        round(
            len(test_df) / len(model_df) * 100,
            2
        ),
        "%"
    )

    print("\nTraining period:")
    print(
        train_df["Datetime"].min(),
        "to",
        train_df["Datetime"].max()
    )

    print("\nTesting period:")
    print(
        test_df["Datetime"].min(),
        "to",
        test_df["Datetime"].max()
    )

    print("\n9. LEAKAGE CHECK")

    leakage_columns = [
        "AQI",
        "AQI_Bucket",
        "Year",
        TARGET
    ]

    model_features = (
        SELECTED_FEATURES
        + TIME_FEATURES
        + LAG_FEATURES
    )

    leakage_found = [
        column
        for column in leakage_columns
        if column in model_features
    ]

    if leakage_found:
        print(
            "WARNING - Leakage columns found:",
            leakage_found
        )
    else:
        print(
            "No AQI / AQI_Bucket / Year / target leakage in features"
        )

    print("\n10. FINAL CHECK")

    if (
        lag_24_valid
        and lag_48_valid
        and len(train_df) > 0
        and len(test_df) > 0
        and len(model_df) > 0
    ):
        print("PREPROCESSING PIPELINE: PASS")
    else:
        print("PREPROCESSING PIPELINE: CHECK REQUIRED")

    print("=" * 60)


if __name__ == "__main__":

    print("Loading dataset...")

    df = load_data()

    print("Raw dataset shape:", df.shape)

    print("\nBefore PM2.5 preprocessing:")
    print(
        "PM2.5 missing:",
        df["PM2.5"].isna().sum()
    )

    df = handle_pm25_missing(df)

    print("\nAfter PM2.5 preprocessing:")
    print(
        "PM2.5 missing:",
        df["PM2.5"].isna().sum()
    )

    df = create_time_features(df)

    df = create_lag_and_target_features(df)

    df = impute_selected_features(df)

    model_df = create_model_dataset(df)

    train_df, test_df, split_date = time_based_split(
        model_df
    )

    validate_pipeline(
        df,
        model_df,
        train_df,
        test_df,
        split_date
    )