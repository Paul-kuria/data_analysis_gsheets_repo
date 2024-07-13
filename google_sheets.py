import os

import gspread  # makes it easy to interact with the sheet. high level api
import pandas as pd
from google.oauth2.service_account import Credentials
from gspread import exceptions as gexeptions

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)


class GoogleSheetEditor:
    def __init__(self) -> None:
        self.basepath = os.path.dirname(os.path.abspath(__file__))
        self.source = os.path.join(self.basepath, "input_data")
        self.destination = os.path.join(self.basepath, "outputs")
        self.number_pattern = r"([0-9,.]+)"
        self.number_pattern = r"(-?[0-9,.]+)"

        self.google_sheet_id = ""

    def check_dataframe_type_data(self, input_dataframe: pd.DataFrame):
        """Checks the type data in each cell of the dataframe, for troubleshooting purposes

        Args:
            input_dataframe (pd.DataFrame): Dataframe to be validated
        """
        for index, row in input_dataframe.iterrows():
            for col in input_dataframe.columns:
                cell_data = row[col]
                data_type = type(cell_data)
                print(
                    f"Row {index}, Column {col}: Data type: {data_type}, Value: {cell_data}"
                )

    def create_sheets_invoice(self):
        """Create google worksheets with the varieties name."""
        # Read varieties csv file
        document = client.open_by_key(self.google_sheet_id)

        variety_list = []
        analysed_variety_path = os.path.join(self.destination, "to_google_sheets_paul")
        for row, subdirs, files in os.walk(analysed_variety_path):
            for file in files:
                abs_path = os.path.join(row, file)
                variety_key = os.path.splitext(os.path.basename(abs_path))[0]
                variety_list.append(variety_key)
                
        # Create sheets with the variety names
        for name in variety_list: 
            try:
                worksheet = document.add_worksheet(title=name, rows=120, cols=70)
                print(f"Successfully created worksheet: {worksheet} for the variety: {name}")
            except Exception as e:
                print(f"Error:{e}. Skip creation of worksheet. File  {name} present in google sheet")

    def delete_sheets_invoice(self):
        """Create google worksheets with the varieties name."""
        # Read varieties csv file
        df_varieties_list = self.my_varieties
        document = client.open_by_key(self.google_sheet_id)

        # Delete sheets with the varietynames
        for name in df_varieties_list:
            try:
                delete_sheet = document.worksheet(name)
                document.del_worksheet(delete_sheet)
                print(f"Successfully deleted sheet: {delete_sheet} with sheetname {name}")
            except Exception as e:
                print(e)
        
    def upload_data_to_google_sheets(self):
        """Perform bulk upload of data into corresponding Google worksheets.
        Uses: gspread library / Google sheets API.
        Eg: "var data" input into var Sheet, B30:P91
        """
        source_data = os.path.join(self.destination, "to_google_sheets_paul")

        # Load google sheets document
        google_document = client.open_by_key(self.google_sheet_id)
        
        for root, subdirs, files in os.walk(source_data):
            for file in files:
                # Load the existing dataframe
                abs_path = os.path.join(root, file)
                variety_name = os.path.splitext(os.path.basename(abs_path))[0]
                variety_dataframe = pd.read_csv(
                    abs_path, index_col=0, skiprows=1,  engine="python"
                )
                variety_dataframe.fillna(0, inplace=True)

                # print(variety_dataframe)
                # exit()
                print("*" * 50)
                # Get the worksheet if exisits
                try:
                    if variety_name == 'var1':
                        continue
                    s_worksheet = google_document.worksheet(variety_name)

                    # Input data, provide cell range
                    cell_range = "B30:P81"

                    # Convert dataframe to 2D list and update with the data
                    data_values = variety_dataframe.values.tolist()
                    try:
                      
                        s_worksheet.update(values=data_values, range_name=cell_range)
                        print(f"Successfully updated worksheet {s_worksheet}")
                    except Exception as e:
                        print(
                            f"{e}: Error in uploading data to the worksheet for variety {variety_name}"
                        )
                except Exception as e:
                    print(e)

    def upload_formulas_to_google_sheets(self):
        """Perform bulk edit of data in 1 column of a google worksheet.
        Uses: gspread library / Google sheets API.
        Eg: "var data" input into var Sheet, B30:P91
        """
        source_data = os.path.join(self.destination, "inventory_2024.csv")

        # Load google sheets document
        google_document = client.open_by_key(self.google_sheet_id)
        variety_dataframe = pd.read_csv(source_data)

        try:
            # Input data, provide cell range
            cell_range = "E9:E39"
            
            # Name google worksheet to be edited
            s_worksheet = google_document.worksheet("")

            # Convert dataframe to 2D list and update with the data
            data_values = variety_dataframe.values.tolist()
            updated_values = [[f"='{variety[0]}'!K30"] for variety in data_values]
            try:
                
                s_worksheet.update(values=updated_values, range_name=cell_range)
                print(f"Successfully updated worksheet {s_worksheet}")
            except Exception as e:
                print(
                    f"{e}: Error in uploading data to the worksheet for variety"
                )
        except Exception as e:
            print("Grand exception")
            print(e)

    def populate_by_year(self, variety_key: str, year: int):
        """Fill out the csv file, with entries for Week 1 to 53.
        Non present weeks are set to zero, to setup input into google sheets format

        Args:
            variety_key (str): The variety name whose dataframe is to be edited
            year (int): The year directory to work on.
        """
        # Destination folder
        destination_dir = os.path.join(self.destination, "todb")
        # Load invoice data
        invoice_data = os.path.join(
            self.destination, "grouped_data", f"{year}_invoice", f"{variety_key}.csv"
        )
        df_invoice = pd.read_csv(invoice_data)

        # Create dataframe with all weeks from 1 to 52 (or 53 where applicable)
        all_weeks = pd.DataFrame({"Week no": range(1, 54)})
        # Merge with your existing dataframe
        merged_df = pd.merge(all_weeks, df_invoice, on="Week no", how="left")
        # Fill missing values with zeros
        merged_df.fillna(0, inplace=True)

        if year == 2020:
            merged_df = merged_df[["Week no", " Quantity", " Price after Discount"]]
            merged_df.rename(
                columns={
                    " Quantity": f"Production_{year}",
                    " Price after Discount": f"Auction_price_{year}",
                },
                inplace=True,
            )

            # Save to file
            destination_file = os.path.join(destination_dir, f"{variety_key}.csv")
            merged_df.to_csv(destination_file, index=False)

        else:
            merged_df = merged_df[[" Quantity", " Price after Discount"]]
            column_names = [f"Production_{year}", f"Auction_price_{year}"]
            merged_df.rename(
                columns={
                    " Quantity": f"Production_{year}",
                    " Price after Discount": f"Auction_price_{year}",
                },
                inplace=True,
            )

            # Load the existing dataframe for 2020
            existing_data_file = os.path.join(destination_dir, f"{variety_key}.csv")
            existing_df = pd.read_csv(existing_data_file)

            # Append new data to the existing dataframe
            existing_df[f"Production_{year}"] = merged_df[f"Production_{year}"]
            existing_df[f"Auction_price_{year}"] = merged_df[f"Auction_price_{year}"]
            # print(existing_df)

            destination_file = os.path.join(destination_dir, f"{variety_key}.csv")
            existing_df.to_csv(destination_file, index=False)




if __name__ == "__main__":
    selected_variety = ""
    selected_year = 2024
    run = GoogleSheetEditor()

    run.upload_formulas_to_google_sheets()
 
