import json
import os
from src.inverse_data_processing import InverseDataProcessing
import pandas as pd
configs = json.load(open("config.json"))



def inverseProcessData(df: pd.DataFrame, scale_method:str='minmax', encoder_method:str='label') -> pd.DataFrame:
    """
    This function will apply inverse encoding and scaling techniques to get original data
    """

    cat_cols = configs['cat_cols']
    num_cols = configs['num_cols']

    print("cat_cols: ", cat_cols)
    print("num_cols: ", num_cols)

    inverse = InverseDataProcessing(
                                    cat_cols=cat_cols,
                                    num_cols=num_cols,
                                    scale_method=scale_method,
                                    encoder_method=encoder_method
                                    )

    inverse_encoded_data = inverse.inverseEncoder(df)
    inverse_data = inverse.inverseScale(inverse_encoded_data)
    return inverse_data


if __name__ == "__main__":
    processed_data = pd.read_csv(os.path.join(configs["processed_data_path"], "processed_data.csv"))
    original_data = inverseProcessData(processed_data)
    print(original_data.head())
    original_data.to_csv("test.csv", index=False)