import pathlib
import pandas as pd
import datetime

def append_treatmentId(df: pd.DataFrame, treatment_df: pd.DataFrame):
    """Appends columns in treatment_df to df based on ID2 values. 
    
    :param df: Pandas DataFrame with column "ID2"
    :param treatment_df: Pandas DataFrame with columns "TreatmentId" and "ID2" only
    :return: Pandas DataFRame with columns "ID2", "TreatmentId", and possibly others depending on df
    """

    result_df = df.copy()

    result_df = result_df.merge(treatment_df, on = "ID2", how = "left")

    return result_df

def append_relative_yield(df: pd.DataFrame):
    """Calculates relative yield for a given "GrainYieldDryPerArea" by dividing it by the average "GrainYieldDryPerArea" values for a given "HarvestYear" and "TreatmentId"

    :param df: Pandas DataFrame with columns "HarvestYear", "ID2", "GrainYieldDryPerArea", "TreatmentId"
    :return: Pandas DataFrame with "HarvestYear", "ID2", "GrainYieldDryPerArea", "TreatmentId", "MeanGrainYield", "RelativeYield"
    """

    result_df = df.copy()

    result_df["MeanGrainYield"] = df.groupby(by = ["HarvestYear", "TreatmentId"])["GrainYieldDryPerArea"].transform("mean")
    result_df["RelativeYield"] = result_df["GrainYieldDryPerArea"] / result_df["MeanGrainYield"]

    return result_df

def calc_running_average_relative_yield(df: pd.DataFrame):
    """Calculates average relative yields for each ID2 that included progressively more years in the calculation

    :param df: Pandas DataFrame with columns "HarvestYear", "ID2", "RelativeYield"
    :return: Pandas DataFrame with columns "ID2" (with each unique ID2 value), "MeanRelativeYield_{min harvest year}-{max harvest year in avg calculation}"
    """

    year_min = df["HarvestYear"].min()
    year_max = df["HarvestYear"].max()

    year_curr = year_min

    result_df = pd.DataFrame()
    result_df["ID2"] = df["ID2"].unique()

    while(year_curr <= year_max):
        # Get df that includes range of years
        running_avg_df = df.loc[(df["HarvestYear"] >= year_min) & (df["HarvestYear"] <= year_curr)]
        
        # Determine name of column to append and calculate mean relative yield for a given ID2
        col_name = "MeanRelativeYield_"+str(year_min)+"_"+str(year_curr)
        running_avg_df[col_name] = running_avg_df.groupby("ID2")["RelativeYield"].transform("mean")

        # Keep only columns we're interested in for this interation
        running_avg_df = running_avg_df[["ID2", col_name]]
        
        # Drop duplicates and NAs to get rid of duplicated values for various years
        running_avg_df = running_avg_df.drop_duplicates(subset = [col_name])
        running_avg_df.dropna(subset = [col_name], inplace=True)

        # Merge new column to results by ID2
        result_df = result_df.merge(running_avg_df, on = "ID2", how = "left")

        year_curr += 1
    
    return result_df

def main(
    yieldInput: pathlib.Path,
    treatmentInput: pathlib.Path,
    outputPath: pathlib.Path):
    """Creates two csv files in the outputPath 1) with relative yields and 2) average relative yields

    :param yieldInput: pathlib.Path to input csv file containing yield values, expect columns "HarvestYear", "ID2", "Crop", "GrainYieldDryPerArea" with values for HarvestYear less than 2016
    :param treatmentInput: pathlib.Path to input csv file containing treatment IDs mapped to ID2 values, expects columns "ID2", "TreatmentId", "EndYear" with values for EndYear less than 2016
    :param outputPath: pathlib.Path to output directory - dir will be created if does not exist
    """

    # Read yield data and filter for years 1999-2015
    df_in = pd.read_csv(inputYieldPath)
    df = df_in[["HarvestYear", "ID2", "Crop", "GrainYieldDryPerArea"]].query("HarvestYear < 2016")

    # Read file to get ID2 values mapped to Treatment and filter for years 1999-2015
    treatment_df_in = pd.read_csv(treatmentInput)
    treatment_df = treatment_df_in.query("EndYear < 2016")[["ID2", "TreatmentId"]]

    # Map yield values to treatmentId, then calc relative  yield by grouping by treatment
    with_treatmentId_df = append_treatmentId(df, treatment_df)
    relative_yield_df = append_relative_yield(with_treatmentId_df)

    # Calculate average relative yields for each point with progressively more years included in the average
    running_avg_df = calc_running_average_relative_yield(relative_yield_df)
    #running_avg_df.drop_duplicates(keep=False,inplace=True)

    # Write files
    outputPath.mkdir(parents=True, exist_ok=True)

    date_today = datetime.datetime.now().strftime("%Y%m%d")
    
    relative_yield_df.to_csv(
        outputPath / "relativeYield_1999-2015_{}_P3A1.csv".format(date_today), 
        index = False)
    running_avg_df.to_csv(
        outputPath / "relativeYieldAverage_1999-2015_{}_P3A1.csv".format(date_today),
        index=False)

if __name__ == "__main__":
    # params
    inputYieldPath = pathlib.Path.cwd() / "input" / "HY1999-2016_20200130_P3A1.csv"
    inputTreatmentPath = pathlib.Path.cwd() / "input" / "georeferencepoint_treatments_cookeast_1999-2016_20200605.csv"
    outputPath = pathlib.Path.cwd() / "output"

    main(inputYieldPath, inputTreatmentPath, outputPath)
