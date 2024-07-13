import csv 
import os 
import re 
from datetime import datetime 
import pandas as pd 
from argparse import ArgumentParser 

class CommonFunctions:
    """Commonly reuseable functions in the repository.
    """
    def __init__(self):
        self.naming = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.outputs = os.path.join(self.base, "all_data") 
        
    def enter_location(self):
        parser = ArgumentParser(description="Inputs folder to be created")
        parser.add_argument("file", metavar="file", type=str)
        args = parser.parse_args()
        return args.file 
    
    def read_file(self):
        filepath = os.path.join(self.base, self.enter_location())

        # Read file
        df = pd.read_csv(filepath)

        # Select 1 column
        df_variety = df['Variety Name ?']

        # Sort in alphabetical order
        df_sort = df.sort_values(['Variety Name ?'], ascending=(True))

        # Save to csv
        outputs = r"C:\Users\paulm\Documents\dataset"
        destination = os.path.join(outputs, f"{self.naming}.csv")
        df_sort.to_csv(destination, index=False)

if __name__ == "__main__":
    run = CommonFunctions()
    run.read_file()