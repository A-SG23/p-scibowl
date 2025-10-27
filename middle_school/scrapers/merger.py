import pandas as pd
import glob
import os

# Path to your folder with all CSV files
csv_folder = "middle_school/raw_data"

# Use glob to get all csv file paths
csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

# Read and concatenate all CSVs
df_list = [pd.read_csv(f) for f in csv_files]
big_df = pd.concat(df_list, ignore_index=True)

# Save combined dataframe to one large CSV file
output_file = "middle_school/cleaned_data/middle_school_all.csv"
big_df.to_csv(output_file, index=False)

print(f"All CSVs merged! Output at {output_file}")
