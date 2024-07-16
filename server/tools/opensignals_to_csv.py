import argparse, json
import pandas as pd

def read_opensignals(filename):
    # Open the file and read line by line
    with open(filename, 'r') as f:
        lines = f.readlines()
        if not lines[0].startswith("# OpenSignals Text File "):
            raise ValueError("Invalid file format. The file should start with '# OpenSignals Text File ...'")
        
        metadata = None
        metadata_num_rows = 1
        for line in lines[1:]:
            if line.startswith("#"):
                metadata_num_rows += 1
                if metadata is not None:
                    continue
                metadata_string = line[1:].replace("# ", "")
                metadata = json.loads(metadata_string)
            else:
                break

        if metadata is None:
            raise ValueError("Invalid file format. Metadata not found.")
        
        print("\nMetadata parsed successfully. Please consider the below information:\n\n", metadata, "\n")

        # Read the data row by row into the dataframe 
        devices = list(metadata.keys())
        if len(devices) != 1:
            raise ValueError(f"This tool currently only supports parsing data collected from exactly 1 device, but found {len(devices)} device(s) in the metadata.")
        
        rows = []
        columns = metadata[devices[0]]["column"]
        for line in lines[metadata_num_rows:]:
            row = line.strip().split("\t")
            rows.append(row)
        df = pd.DataFrame(rows, columns=columns)

        print("Data parsed successfully. The first few rows of the data are presented below:\n\n", df.head(), "\n")
        return df
    

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

    df = read_opensignals(args.source)
    export_to_csv(df, args.destination)

if __name__ == "__main__":
    main()