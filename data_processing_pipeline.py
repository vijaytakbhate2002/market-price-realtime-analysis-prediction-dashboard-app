import pandas as pd
from sklearn.pipeline import Pipeline
from src.data_processing import ScaleData, EncodelData, Imputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler
import os
import json
from typing import Union
from src.s3_operations import S3BucketHandler
configs = json.load(open("config.json"))



def processData(df:pd.DataFrame, num_impute_method:str='mean', scale_method:str='minmax', encoder_method:str='label', scaler:Union[None, StandardScaler, MinMaxScaler]=None, encoder:Union[None, dict, OneHotEncoder]=None) -> pd.DataFrame:
    """
    Args:
        df: unprocessed data
        num_impute_method: Choose impute method from ('mean', 'median', 'mode')
        scale_method: Choose scaling method from ('minmax', 'standard')
        encoder_method: Choose encoder method from ('label', 'onehot')

        scaler: Pass None if you want to create new scaler while processing data else pass fitted StandardScaler or MinmaxScaler.
        encoder: Pass None if you want to create new encoder while processing data 
                for 'label' method pass dictionary of column as key and respective fitted label encoder,
                for 'onehot' method pass fitted OneHotEncoder

    Description: This function will apply encoding techniques for categorical data and scaling techniques for numerical data

    Returns:
        df: processed data
    """

    cat_cols = df.select_dtypes(include='object').columns
    num_cols = df.select_dtypes(exclude='object').columns

    pipeline_steps = [
        ("imputer", Imputer(cat_cols=cat_cols, num_cols=num_cols, num_method=num_impute_method)),
        ("scaler", ScaleData(num_cols=num_cols, method=scale_method, scaler=scaler)),
        ("encoder", EncodelData(cat_cols=cat_cols, method=encoder_method, encoder=encoder))
        ]

    processing_pipeline = Pipeline(
        pipeline_steps
    )

    df = processing_pipeline.fit_transform(df)
    return df



def runProcessingPipeline(num_impute_method:str='mean', scale_method:str='minmax', encoder_method:str='label', scaler=Union[None, StandardScaler, MinMaxScaler], encoder:Union[None, dict, OneHotEncoder]=None) -> None:
    """
    Args:
        df: unprocessed data
        num_impute_method: Choose impute method from ('mean', 'median', 'mode')
        scale_method: Choose scaling method from ('minmax', 'standard')
        encoder_method: Choose encoder method from ('label', 'onehot')

        scaler: Pass None if you want to create new scaler while processing data else pass fitted StandardScaler or MinmaxScaler.
        encoder: Pass None if you want to create new encoder while processing data 
                for 'label' method pass dictionary of column as key and respective fitted label encoder,
                for 'onehot' method pass fitted OneHotEncoder

    Description: This function will apply encoding techniques for categorical data and scaling techniques for numerical data

    Returns:
        df: processed data
    """

    s3_handler = S3BucketHandler(
        bucket_name=configs["bucket_name"]
    )

    # s3_handler.removeFromS3(file_key=configs["processed_file_key"], last_rows_num=-1)
    # data = s3_handler.readS3Data(file_key=configs['all_row_data_key'], nrows=-1)
    # processed_data = processData(df=data, num_impute_method="mean", scale_method="minmax", encoder_method="label")
    # s3_handler.appendToS3StreamCSV(file_key=configs["processed_file_key"], new_data_df=processed_data)

    for data in s3_handler.readS3DataStreaming(file_key=configs["all_row_data_key"], nrows=100, totalrows=10000):
        processed_data = processData(df=data, num_impute_method="mean", scale_method="minmax", encoder_method="label", scaler=scaler, encoder=encoder)
        s3_handler.appendToS3StreamCSV(file_key=configs["batch_processed_file_key"], new_data_df=processed_data)

    # df = s3_handler.readS3Data(file_key=configs["processed_file_key"], nrows=-1)
    # df.to_csv("processed_data_all_rows.csv", index=False)
    full_processed_df = s3_handler.readS3Data(file_key=configs["processed_file_key"], nrows=-1)
    batch_processed_df = s3_handler.readS3Data(file_key=configs["batch_processed_file_key"], nrows=-1)



if __name__ == "__main__":
    import joblib
    import os
    import json

    configs = json.load(open("config.json"))
    processing_configs = json.load(open("src/processing_config.json"))
    encoders = {}

    for col_name in os.listdir(processing_configs['label_encoder_folder_path']):
        encoders[col_name.replace('.pkl', '')] = joblib.load(os.path.join(processing_configs['label_encoder_folder_path'], col_name))

    runProcessingPipeline(
        num_impute_method='mean',
        scale_method='minmax',
        encoder_method='label',
        scaler = joblib.load(processing_configs['scaler_file_path']),
        encoder = encoders
    )

    # runProcessingPipeline(
    #     num_impute_method='mean',
    #     scale_method='minmax',
    #     encoder_method='label'
    # )


