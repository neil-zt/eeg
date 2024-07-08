import argparse
import pyedflib
import pandas as pd

def read_edf(edf_file):
    """
    Reads an EDF file and returns a DataFrame with the data.
    
    Parameters:
    edf_file (str): Path to the EDF file.

    Returns:
    pd.DataFrame: DataFrame containing the EEG data.
    """
    edf_reader = pyedflib.EdfReader(edf_file)
    signal_labels = edf_reader.getSignalLabels()
    data = {label: edf_reader.readSignal(i) for i, label in enumerate(signal_labels)}
    edf_reader._close()
    return pd.DataFrame(data)

def export_to_csv(df, csv_file):
    """
    Exports a DataFrame to a CSV file.
    
    Parameters:
    df (pd.DataFrame): DataFrame to export.
    csv_file (str): Path to the destination CSV file.
    """
    df.to_csv(csv_file, index=False)

def main():
    """
    Main function to parse arguments and perform the conversion.
    """
    parser = argparse.ArgumentParser(description='Convert EDF EEG file to CSV.')
    parser.add_argument('source', type=str, help='Path to the source EDF file.')
    parser.add_argument('destination', type=str, help='Path to the destination CSV file.')
    args = parser.parse_args()

    df = read_edf(args.source)
    export_to_csv(df, args.destination)

if __name__ == "__main__":
    main()