import pandas as pd 
import csv 
from datetime import datetime 
import os 
from argparse import ArgumentParser  

class ToDB:
    def __init__(self) -> None:
        self.naming = datetime.now().strftime("%y_%m_%d")
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.outputs = os.path.join(self.base, "final_clean") 
        
        if not os.path.exists(self.outputs):
            os.makedirs(self.outputs, exist_ok=True)

    def enter_location(self):
        parser = ArgumentParser(description="Inputs folder to be created")
        parser.add_argument("file", metavar="file", type=str)
        args = parser.parse_args()
        return args.file 
      
    def final_clean_price(self):
        csv_file = os.path.join(self.base, self.enter_location())
        df = pd.read_csv(csv_file)  
        my_row = df.iloc[1:2]
        print(my_row)

    # Organize based on variety, and year 
    def final_clean_production(self, year_selector: int):
        constants = os.path.join(self.base, "date_prod_21.csv")

        source_directory = os.path.join(self.base, self.enter_location())
        destination = os.path.join(self.outputs, "output_file.csv")

        for  root, dirs, files in os.walk(source_directory):
            for file in sorted(files):
                prefix = file.split(".")[0]
                data = os.path.join(root, file)
                
                # Read pandas file
                df = pd.read_csv(data) 
                df2 = pd.read_csv(constants)

                mydata = df.loc[df['Year'] == year_selector].copy()
                mydata['variety'] = prefix
                mydata['description'] = mydata['variety'].astype(str) + mydata['Year'].astype(str) + mydata['Week'].astype(str)
                mydata['datetime'] = df2["datetime"]
                mydata['af_cost_per_stem'] = df2["af_cost_per_stem"]

                mydata = mydata.rename(columns={
                    'Quantity': 'production_amount',
                    'price': 'auction_price',
                    'variety':'variety_name',
                    'Year':'year',
                    'Week':'week',
                    })
                mydata.to_csv(destination, mode='a', index=False, header=False)
        

if __name__ == "__main__":
    ToDB().final_clean_production(year_selector=2021)