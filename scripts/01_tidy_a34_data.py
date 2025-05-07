import pandas as pd
import argparse
import os

def process_and_save_data(file_path: str, output_path: str) -> None:
    """
    Processes an Excel file containing data about inadmissibility grounds by country 
    and year, and saves the tidy version of the data into a CSV file.

    Parameters
    ----------
    file_path : str
        The file path to the Excel file containing the data.
    output_path : str
        The file path where the processed data in CSV format will be saved.

    Returns
    -------
    None
        The function saves the tidy DataFrame into a CSV file at the specified location.
    
    Notes
    -----
    - The function processes the data by filling missing values with 0 and converts numeric columns to integers.
    - The data is split into sections based on rows containing digits and reorganized into a long format.
    - Additional columns for 'cor_status' and 'resident' are derived from the year column.
    """
    df = pd.read_excel(file_path, skiprows=5, skipfooter=8)

    df = df.fillna(0)
    df[df.select_dtypes(include='number').columns] = df.select_dtypes(include='number').astype(int)

    mask = df['Unnamed: 0'].str.contains(r'\d', regex=True)

    split_indices = df.index[mask].tolist()
    split_indices.append(df.index[-1] + 1)

    dfs = []
    start_idx = 0
    for end_idx in split_indices:
        # Skip rows containing digits
        if mask[start_idx]:
            start_idx += 1
        
        # Select sub_df from start_idx to end_idx, excluding the row containing the digit
        sub_df = df.iloc[start_idx:end_idx].copy()
        
        # Skip empty sub_df
        if sub_df.empty:
            start_idx = end_idx
            continue
        
        # Assign 'inadmissibility_grounds' column with the value from previous split row
        inadmissibility_value = df['Unnamed: 0'].iloc[start_idx - 1]
        sub_df['inadmissibility_grounds'] = inadmissibility_value

        sub_df.rename(columns={'Unnamed: 0': 'country'}, inplace=True)

        dfs.append(sub_df)
        start_idx = end_idx

    def remove_unwanted_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes columns containing 'Unnamed' or 'Total' in their names.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame to remove unwanted columns from.

        Returns
        -------
        pd.DataFrame
            The DataFrame after removing unwanted columns.
        """
        df = df.loc[:, ~df.columns.str.contains('Unnamed|Total')]
        return df

    dfs = [remove_unwanted_columns(df) for df in dfs]

    dfs_long = []
    for df in dfs:
        df_long = pd.melt(df, 
                          id_vars=['country', 'inadmissibility_grounds'], 
                          var_name='year', 
                          value_name='count')
        dfs_long.append(df_long)

    for df_long in dfs_long:
        df_long['cor_status'] = df_long['year'].apply(
            lambda x: 'COR Canada' if '.1' in str(x) or '.3' in str(x) else 'COR Not Canada'
        )
        df_long['resident'] = df_long['year'].apply(
            lambda x: 'Temporary Resident' if '.2' in str(x) or '.3' in str(x) else 'Permanent Resident'
        )
        df_long['year'] = df_long['year'].astype(float).astype(int)

    df = pd.concat(dfs_long, ignore_index=True)

    df = df[['inadmissibility_grounds', 'country', 'year', 'cor_status', 'resident', 'count']]

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    df.to_csv(output_path, index=False)

    print(f"Data has been processed and saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process and save data from an Excel file to CSV.')
    parser.add_argument('input_file', type=str, help='Path to the input Excel file')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file')

    args = parser.parse_args()

    process_and_save_data(args.input_file, args.output_file)