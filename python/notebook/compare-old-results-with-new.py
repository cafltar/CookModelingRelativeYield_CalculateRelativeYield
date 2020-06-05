# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

# %% Load data
RYAvg_current = pd.read_csv("output/relativeYieldAverage_1999-2015_20200605_P3A1.csv")[["ID2", "MeanRelativeYield_1999_2009"]]
RYAvg_kedar = pd.read_excel("input/StripbyStripAvg2_AllNormalization1.xlsx", "YearAddedAvg")[["UID", "11Years Avg_Strip"]].rename(columns={"UID": "ID2"})
RYAvg_jones = pd.read_excel("input/SOC_2009Manuscript.xlsx", "CAFTer10m")[["ID2", "CAFRelYd"]]


# %% Merge data
df = RYAvg_current.merge(RYAvg_kedar, on = "ID2", how = "left").merge(RYAvg_jones, on = "ID2", how = "left")

# %%
sns.scatterplot(x = "MeanRelativeYield_1999_2009", y = "11Years Avg_Strip", data = df)

# %%
sns.scatterplot(x = "MeanRelativeYield_1999_2009", y = "CAFRelYd", data = df)
