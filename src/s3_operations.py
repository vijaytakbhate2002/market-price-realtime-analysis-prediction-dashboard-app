import boto3
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='a',
                    filename='logs.log')

class S3BucketHandler:
    """
    This class handles read, append or write/replace function for s3 bucket.
    """

    s3 = boto3.client('s3')

    def __init__(self, bucket_name:str):
        self.bucket_name = bucket_name



    def readS3Data(self, file_key:str, nrows:int) -> pd.DataFrame:
        """
        Args:
            file_key: path of the file to read.
            nrows: number of rows to read | pass -1 to access full data.

        Returns:
            return first {nrows} rows of data read from S3 bucket.
        """

        logging.info(f"Reading data from S3 bucket with {nrows}, {file_key}, {self.bucket_name} ...")
        response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
        if nrows == -1:
            df_head = pd.read_csv(response['Body'])
        elif nrows > 0:
            df_head = pd.read_csv(response['Body'], nrows=nrows)
        else:
            logging.error(f"Invalid value passed to nrows {nrows}")
        logging.info("Data read successfully! ")
        return df_head



    def appendToS3StreamCSV(self, file_key, new_data_df):
        """
        Appends data to a large CSV in S3 efficiently without loading the full file into memory.
        """

        csv_buffer = StringIO()

        new_data_df.to_csv(csv_buffer, index=False, header=False)
        new_csv_data = csv_buffer.getvalue()

        try:
            logging.info(f"Trying to append data into {file_key}...")
            self.s3.head_object(Bucket=self.bucket_name, Key=file_key)

            s3_object = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            existing_data = s3_object['Body'].read().decode('utf-8')

            # Append new data to the end without reloading into a DataFrame
            combined_data = existing_data + '\n' + new_csv_data
        except self.s3.exceptions.ClientError:
            csv_buffer = StringIO()
            new_data_df.to_csv(csv_buffer, index=False)
            combined_data = csv_buffer.getvalue()

        self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=combined_data)
        logging.info(f"✅ Stream-appended data to {file_key} in {self.bucket_name}")



    def uploadToS3(self, file_key, data_df):
        """
        Uploads a DataFrame to an S3 bucket (creates or overwrites the file).

        Parameters:
            file_key (str): S3 file path (e.g., 'folder/data.csv').
            data_df (pd.DataFrame): DataFrame to upload.
        """
        csv_buffer = StringIO()
        data_df.to_csv(csv_buffer, index=False)

        logging.info(f"Uploading {file_key} to {self.bucket_name} ...")
        self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=csv_buffer.getvalue())
        logging.info(f"✅ File '{file_key}' uploaded successfully to bucket '{self.bucket_name}'")



    def removeFromS3(self, file_key: str, last_rows_num: int):
        """
        Removes the last N rows from a CSV file in the S3 bucket,
        or deletes the entire file if last_rows_num == -1.

        Parameters:
            file_key (str): S3 file path (e.g., 'folder/data.csv').
            last_rows_num (int): Number of rows to remove from the end.
                                 Use -1 to delete the entire file.
        """
        try:
            if last_rows_num == -1:
                logging.info(f"🗑️ Deleting entire file '{file_key}' from S3...")
                self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)
                logging.info(f"✅ File '{file_key}' deleted successfully from bucket '{self.bucket_name}'")
                return

            # Otherwise, remove last N rows
            logging.info(f"Removing last {last_rows_num} rows from {file_key}...")

            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            df = pd.read_csv(response['Body'])

            # Trim last N rows
            if last_rows_num < len(df):
                df = df.iloc[:-last_rows_num]
            else:
                logging.warning("⚠️ last_rows_num >= total rows, clearing the file.")
                df = pd.DataFrame(columns=df.columns)

            # Upload updated file back to S3
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=csv_buffer.getvalue())

            logging.info(f"✅ Removed last {last_rows_num} rows and updated '{file_key}' successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to update '{file_key}' in S3: {e}")



    def readCsvRange(path, ranges):
        dfs = []
        for start, end in ranges:
            df_part = pd.read_csv(path, skiprows=range(1, start + 1), nrows=end - start)
            dfs.append(df_part)
        return pd.concat(dfs, ignore_index=True)



    def readS3DataStreaming(self, file_key:str, nrows:int, totalrows:int):
        """
        Args:
            file_key: path of the file to read.
            nrows: number of rows to read | pass -1 to access full data.

        Returns:
            Straming batchwise data where batchsize=nrows.
        """

        if totalrows < nrows:
            logging.warning(f"Entered {nrows} nrows are more than {totalrows} totalrows of the data")
            return Warning(f"Entered {nrows} nrows are more than {totalrows} totalrows of the data")

        batch_size = totalrows // nrows if totalrows % nrows == 0 else totalrows // nrows + 1

        for batch in range(batch_size):
            logging.info(f"Reading data from S3 bucket with {nrows}, {file_key}, {self.bucket_name} ...")
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            logging.info(f"Reading range(1, batch * nrows + 1) {range(1, batch * nrows + 1),}, batch number {batch}, batch_size {batch_size}, with nrows {nrows} and totalrows {totalrows} ...")
            data = pd.read_csv(response["Body"], skiprows=range(1, batch * nrows + 1), nrows=nrows)
            yield data




if __name__ == "__main__":
    bucket_handler = S3BucketHandler(
        bucket_name="market-price-data-vijay-takbhate"
    )
    file_key = "test_row_data.csv"
    head = bucket_handler.readS3Data(file_key=file_key, nrows=5)

    print("******************************************** head **************************************")
    print(head)
    print(head.shape)

    print("******************************************** full df info **************************************")
    full_df = bucket_handler.readS3Data(file_key=file_key, nrows=-1)
    print(full_df.head())
    print(full_df.tail())
    print(full_df.shape)
    bucket_handler.appendToS3StreamCSV(file_key=file_key, new_data_df=head)

    print("******************************************** full df info after appending head **************************************")
    full_df = bucket_handler.readS3Data(file_key=file_key, nrows=-1)
    print(full_df.head())
    print(full_df.tail())
    print(full_df.shape)

    print("******************************************** full df info after deleting head **************************************")
    bucket_handler.removeFromS3(file_key=file_key, last_rows_num=5)
    full_df = bucket_handler.readS3Data(file_key=file_key, nrows=-1)
    print(full_df.head())
    print(full_df.tail())
    print(full_df.shape)


