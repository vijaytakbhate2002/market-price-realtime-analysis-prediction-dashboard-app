import pandas as pd
from sklearn.pipeline import Pipeline
from src.data_processing import ScaleData, EncodelData, Imputer
import os
import json
configs = json.load(open("config.json"))



def processData(df:pd.DataFrame, num_impute_method:str='mean', scale_method:str='minmax', encoder_method:str='label') -> pd.DataFrame:
    """
    Args:
        df: unprocessed data
        num_impute_method: Choose impute method from ('mean', 'median', 'mode')
        scale_method: Choose scaling method from ('minmax', 'standard')
        encoder_method: Choose encoder method from ('label', 'onehot')

    Description: This function will apply encoding techniques for categorical data and scaling techniques for numerical data

    Returns:
        df: processed data
    """

    cat_cols = df.select_dtypes(include='object').columns
    num_cols = df.select_dtypes(exclude='object').columns

    pipeline_steps = [
        ("imputer", Imputer(cat_cols=cat_cols, num_cols=num_cols, num_method=num_impute_method)),
        ("scaler", ScaleData(num_cols=num_cols, method=scale_method)),
        ("encoder", EncodelData(cat_cols=cat_cols, method=encoder_method))
        ]

    processing_pipeline = Pipeline(
        pipeline_steps
    )

    df = processing_pipeline.fit_transform(df)
    return df



if __name__ == "__main__":
    # df = pd.read_csv(os.path.join(configs["row_write_folder_path"], "market_prices_20251108-152737.csv"))
    df = pd.read_csv(os.path.join(configs["row_write_folder_path"], "market_prices_20251109-103741.csv"))

    processed_data = processData(df)
    print(processed_data.head())
    processed_data.to_csv(os.path.join(configs["processed_data_path"], 'processed_data.csv'), index=False)