import joblib
import os
import json
import pandas as pd
processing_configs = json.load(open("src/processing_config.json"))

class InverseDataProcessing:
    """
    This class is responsible for inversing the data processing techniques
    - Encoder Inversion (LabelEncoder or OneHot)
    - Scaler Inversion (Minmax or StandardScaler)
    """

    def __init__(self, cat_cols:list, num_cols:list, scale_method:str, encoder_method:str):
        self.cat_cols = cat_cols
        self.num_cols = num_cols
        self.encoder_method = encoder_method
        self.scale_method = scale_method


    def inverseEncoder(self, X:pd.DataFrame):
        X_copy = X.copy()
        if self.encoder_method == 'label':
            encoder_names = os.listdir(processing_configs['label_encoder_folder_path'])
            for name in encoder_names:
                encoder = joblib.load(os.path.join(processing_configs['label_encoder_folder_path'], name))
                X_copy[name.replace(".pkl", "")] = encoder.inverse_transform(X_copy[name.replace(".pkl", "")].astype(int))

            return X_copy

        elif self.encoder_method == 'onehot':
            encoder = joblib.load(processing_configs['one_hot_encoder_file_path'])
            X_copy = encoder.inverse_transform(X_copy[self.cat_cols])
            return X_copy

        else:
            raise ValueError("Choose either 'onehot' or 'label'")


    def inverseScale(self, X:pd.DataFrame):
        """
        Args:
            X: pd.DataFrame
        Description: Inverse the scaled data

        Returns:
            pd.DataFrame
        """
        X_copy = X.copy()
        scaler = joblib.load(processing_configs['scaler_file_path'])
        X_copy[self.num_cols] = scaler.inverse_transform(X_copy[self.num_cols])
        X_copy = pd.DataFrame(X_copy, columns=X.columns)
        return X_copy


