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

    def __init__(self, read_folder:str, save_folder_path:str, compress_level:int=2) -> None:
        self.read_folder = read_folder
        self.save_folder_path = save_folder_path
        self.compress_level = compress_level



    def compressData(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Args:
            df: dataframe to compress
            compress_level: compression level (1, 2, 3, 4 etc)

        Description:
            - compression value decides the size of data if level is 2 then you will get every 2nd row from df,
            if 3 then every 3rd and soo on.
            - compress_level is inversely inversely proportional to size of df

        Returns:
            pd.DataFrame
        """
        df = df.iloc[::self.compress_level].reset_index(drop=True)
        return df



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
                temp = pd.read_csv(file_path)
                temp = self.compressData(temp)
                df = pd.concat([df, temp], axis='rows')
            elif file_path.endswith(".xlsx"):
                temp = pd.read_excel(file_path)
                temp = self.compressData(temp)
                df = pd.concat([df, temp], axis='rows')
            else:
                raise ValueError("Unsupported file type, {}".format(file_path))
        return df



    def saveData(self, df:pd.DataFrame, file_name:str) -> None:
        """
        Args: dataframe to store at the folder_path
        """

        full_path = os.path.join(self.save_folder_path, file_name)
        df.to_csv(full_path, index=False)



    def getData(self, latest_files:int=None) -> pd.DataFrame:
        """
        Args:
            latest_files: number of latest files to read for conversion

        Description:
            Converts folder files into combined dataframe

        Returns:
            None
        """

        logging.info("Collecting file paths...")
        file_names = os.listdir(self.read_folder)
        if latest_files is not None:
            file_names = file_names[-latest_files:]
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
        save_folder_path=row_write_folder_path,
        compress_level=2

    )

    data_builder.getData(latest_files=15)
