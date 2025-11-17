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

    # cat_cols = df.select_dtypes(include='object').columns
    # num_cols = df.select_dtypes(exclude='object').columns

    cat_cols = configs['cat_cols']
    num_cols = configs['num_cols']

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



def runProcessingPipeline(totalrows:int, batch_size:int, num_impute_method:str='mean', scale_method:str='minmax', encoder_method:str='label', scaler:Union[None, StandardScaler, MinMaxScaler]=None, encoder:Union[None, dict, OneHotEncoder]=None, number_of_rows:int=-1, input_data:Union[None, pd.DataFrame]=None) -> Union[None, pd.DataFrame]:
    """
    Args:
        num_impute_method: Choose impute method from ('mean', 'median', 'mode')
        scale_method: Choose scaling method from ('minmax', 'standard')
        encoder_method: Choose encoder method from ('label', 'onehot')

        scaler: Pass None if you want to create new scaler while processing data else pass fitted StandardScaler or MinmaxScaler.
        encoder: Pass None if you want to create new encoder while processing data 
                for 'label' method pass dictionary of column as key and respective fitted label encoder,
                for 'onehot' method pass fitted OneHotEncoder

        input_data: Your data to process (Function will return processed data instead of saving it into S3 bucket)

    Description: This function will apply encoding techniques for categorical data and scaling techniques for numerical data

    Returns:
        df: processed data
    """

    if input_data is not None:
        processed_data = processData(
                                     df=input_data, 
                                     num_impute_method=num_impute_method, 
                                     scale_method=scale_method,
                                     encoder_method=encoder_method
                                     )
        return processed_data

    s3_handler = S3BucketHandler(
        bucket_name=configs["bucket_name"]
    )

    # s3_handler.removeFromS3(file_key=configs["batch_processed_file_key"], last_rows_num=-1)
    for df_temp in s3_handler.readS3DataStreaming(file_key=configs["all_row_data_key"], nrows=batch_size, totalrows=totalrows):
        processed_data = processData(df=df_temp, num_impute_method=num_impute_method, scale_method=scale_method, encoder_method=encoder_method, scaler=scaler, encoder=encoder)
        s3_handler.appendToS3StreamCSV(file_key=configs["batch_processed_file_key"], new_data_df=processed_data)



if __name__ == "__main__":
    import joblib
    import os
    import json

    configs = json.load(open("config.json"))
    processing_configs = json.load(open("src/processing_config.json"))
    encoders = {}

    for col_name in os.listdir(processing_configs['label_encoder_folder_path']):
        encoders[col_name.replace('.pkl', '')] = joblib.load(os.path.join(processing_configs['label_encoder_folder_path'], col_name))

    input_df = pd.read_csv(os.path.join(configs['row_write_folder_path'], configs['all_row_data_key']))

    processed_data = runProcessingPipeline(
        # input_data = input_df,
        num_impute_method='mean',
        scale_method='minmax',
        encoder_method='label',
        scaler = joblib.load(processing_configs['scaler_file_path']),
        encoder = encoders,
        batch_size = 10000000,
        totalrows=configs['total_data_rows']
        )

    print(processed_data.head())


