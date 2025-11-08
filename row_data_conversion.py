import pandas as pd
import json
import os
import datetime
configs = json.load(open("config.json"))
import logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs.log', filemode='a'
)


class BuildTable:
    """
    Reads path from provided folder and return the dataframe
    """

    def __init__(self, read_folder:str, save_folder_path:str) -> None:
        self.read_folder = read_folder
        self.save_folder_path = save_folder_path



    def concatData(self, file_paths:list) -> pd.DataFrame:
        """
        Args:
            file_paths: list of file paths
        Returns:
            pd.DataFrame
        """

        df = pd.DataFrame()
        for file_path in file_paths:
            logging.info(f"Reading and merging file path: {file_path}...")
            if file_path.endswith(".csv"):
                df = pd.concat([df, pd.read_csv(file_path)], axis=1)
            elif file_path.endswith(".xlsx"):
                df = pd.concat([df, pd.read_excel(file_path)], axis=1)
            else:
                raise ValueError("Unsupported file type, {}".format(file_path))
        return df



    def saveData(self, df:pd.DataFrame, file_name:str) -> None:
        """
        Args: dataframe to store at the folder_path
        """

        full_path = os.path.join(self.save_folder_path, file_name)
        df.to_csv(full_path, index=False)



    def getData(self) -> pd.DataFrame:
        """
        Converts folder files into combined dataframe
        """

        logging.info("Collecting file paths...")
        file_names = os.listdir(self.read_folder)
        file_paths = [os.path.join(self.read_folder, name) for name in file_names]
        logging.info(f"Reading and merging files from the folder {self.read_folder}...")
        df = self.concatData(file_paths)
        logging.info(f"Writing the merged files to folder {self.save_folder_path}...")
        self.saveData(df, "market_prices_{}.csv".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
        logging.info(f"Written successfully!")



if __name__ == "__main__":
    row_read_folder_path = configs["row_read_folder_path"]
    row_write_folder_path = configs["row_write_folder_path"]

    data_builder = BuildTable(
        read_folder=row_read_folder_path,
        save_folder_path=row_write_folder_path
    )
    data_builder.getData()
