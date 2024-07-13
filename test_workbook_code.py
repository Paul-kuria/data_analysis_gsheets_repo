import csv 
import os 
import re 
from datetime import datetime 
import pandas as pd 

class Excel:

    def __init__(self, year, header_row, variety_name):
        pass
        self.year = year
        self.header_row = header_row
        self.variety_name = variety_name
        self.naming = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.source = f"{self.basepath}/week3.xlsx" 
        self.destination = f"{self.basepath}/outputs"
        self.output_file = f"{self.destination}/{self.naming}.csv"


        if not os.path.exists(self.destination):
            os.makedirs(self.destination, exist_ok=True)
        
    def extract_one_workbook(self, document: str):
        specified_name = self.variety_name
        list_select_rows_by_sheet = [] 

        mysheet_names = pd.ExcelFile(document).sheet_names[:10]
        mysheet_names = sorted(mysheet_names)

        dataframes = pd.read_excel(
            document, 
            sheet_name=mysheet_names,
            header=self.header_row
            )

        for worksheet, df in dataframes.items():
            try:
                selected = df[df["Variety"].str.contains(pat= specified_name, case=False, na=False)]
                date_cell = df.iloc[0]["Date"]
                new_row = selected.values.tolist()[0]
                new_row[0] = date_cell 

                list_select_rows_by_sheet.append(new_row)
                print(new_row)
            except KeyError as err:
                print(err)
                pass 
        return list_select_rows_by_sheet
    
    def main(self):
        extract = self.extract_one_workbook(self.source)

if __name__ == "__main__":
    year = 2022
    h_row = 4
    variety = ""
    df = Excel(year, h_row, variety)
    df.main()