import pandas as pd 
import csv 
from datetime import datetime 
import os 
from argparse import ArgumentParser 

class ReviewVarieties:
    def __init__(self):
        self.naming = datetime.now().strftime("%y_%m_%d")
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.source = self.enter_location()

        self.csvpath = os.path.join(self.base, self.source)
        self.prefix = self.source.split("/")[-1]
        self.outputs = os.path.join(self.base, "reviewed", self.prefix)

    def enter_location(self):
        parser = ArgumentParser(description="Inputs folder to be created")
        parser.add_argument("file", metavar="file", type=str)
        args = parser.parse_args()
        return args.file 
    
    @property
    def read_data(self):
        """_summary_: Read the csv file using pandas. Transpose the result and export to file.

        Inputs:
            CSV file 

        Outputs:
            Sales amount, stem quantities per day per variety
        """
        df = pd.read_csv(self.csvpath)
        grouped_data = df.groupby('Date').agg({
            'Quantity': 'sum',
            'Sales Amount': 'sum',
        }).reset_index() 

        # Extract week and year
        grouped_data[['Week', 'Year']] = grouped_data['Date'].str.extract(r'Week (\d+) (\d+)')

        # Convert 'Week' and 'Year' to integers
        grouped_data[['Week', 'Year']] = grouped_data[['Week', 'Year']].astype(int)

        # Calculate price per stem
        grouped_data['price'] =   round(grouped_data['Sales Amount'] / grouped_data['Quantity'] ,3)
        # sorted_data = grouped_data.sort_values(['Year', 'Week'])
        final_data = grouped_data[['Year', 'Week', 'price', 'Quantity']]
        sorted_data = final_data.sort_values(['Year', 'Week'])

        # Re-index?
        # Reindex with a range of weeks and fill missing values with zeros
        full_range = pd.MultiIndex.from_product([sorted_data['Year'].unique(), range(1, 53)], names=['Year', 'Week'])
        sorted_data = sorted_data.set_index(['Year', 'Week']).reindex(full_range, fill_value=0).reset_index()

        sorted_data.to_csv(self.outputs, index=False)

class ToDB:
    def __init__(self) -> None:
        self.naming = datetime.now().strftime("%y_%m_%d")
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.outputs = os.path.join(self.base, "backup", "output")

        if not os.path.exists(self.outputs):
            os.makedirs(self.outputs, exist_ok=True)

    def classify_by_date(self, year_selector: int, filepath: str):
        source_dir = os.path.join(self.base, filepath)
        dest_dir = os.path.join(self.outputs, "my_data.csv") 

        for  root, dirs, files in os.walk(source_dir):
            for file in sorted(files):
                prefix = file.split(".")[0]
                data = os.path.join(root, file)
                
                # Read pandas file
                df = pd.read_csv(data)
                
                df = df.rename(columns={'Quantity': prefix})
                mydata = df.loc[df['Year'] == year_selector]
                transposed = mydata[[prefix]].T 
                transposed.to_csv(dest_dir, mode='a', header=False)

if __name__ == "__main__":
    ToDB().classify_by_date(
        year_selector=2023,
        filepath="./final/"
        )
