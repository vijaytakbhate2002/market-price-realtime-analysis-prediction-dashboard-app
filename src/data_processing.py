from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
import pandas as pd
from typing import Union
import joblib
import os
import json
processing_configs = json.load(open("src/processing_config.json"))
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='a', filename='logs.log')



class ScaleData:
    """
    This class is responsible for scaling numeric data columns.
    """

    scaler_passed = False

    def __init__(self, num_cols: list, method: str, scaler=None):
        logging.info("Initializing ScaleData with method: %s and columns: %s", method, num_cols)
        self.num_cols = num_cols
        if scaler is not None:
            self.scaler = scaler
            self.scaler_passed = True
            logging.info("Scaler instance passed directly to ScaleData.")
        else:
            if method == "standard":
                self.scaler = StandardScaler()
                logging.info("Using StandardScaler for scaling.")
            elif method == "minmax":
                self.scaler = MinMaxScaler()
                logging.info("Using MinMaxScaler for scaling.")
            else:
                logging.error("Invalid scaling method provided: %s", method)
                raise ValueError("Choose method from ('standard', 'minmax')")


    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> None:
        logging.info("Fitting scaler on numeric columns: %s", self.num_cols)
        if self.scaler_passed:
            logging.info("Scaler already provided, skipping fit.")
            return self
        self.scaler.fit(X[self.num_cols])
        logging.info("Scaler fitted successfully.")
        return self


    def transform(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> pd.DataFrame:
        logging.info("Transforming numeric columns using fitted scaler.")
        X_copy = X.copy()
        scaled_values = self.scaler.transform(X_copy[self.num_cols])
        joblib.dump(self.scaler, processing_configs['scaler_file_path'])
        logging.info("Scaler object saved to %s", processing_configs['scaler_file_path'])
        X_copy[self.num_cols] = pd.DataFrame(
            scaled_values, columns=self.num_cols, index=X_copy.index
        )
        logging.info("Scaling transformation completed.")
        return X_copy




class EncodelData:
    """
    This class is responsible for labeling categorical columns.
    """

    encoder_passed = False

    def __init__(self, cat_cols: list, method: str, encoder=None):
        logging.info("Initializing EncodelData with method: %s and columns: %s", method, cat_cols)
        self.cat_cols = cat_cols
        self.method = method

        if encoder is not None:
            self.encoder = encoder
            self.encoder_passed = True
            logging.info("Encoder instance passed directly to EncodelData.")
        else:
            if method == "onehot":
                self.encoder = OneHotEncoder(sparse_output=False, drop=None, handle_unknown="ignore")
                logging.info("Using OneHotEncoder for encoding.")
            elif method == "label":
                self.encoder = {col: LabelEncoder() for col in cat_cols}
                logging.info("Using LabelEncoder for each categorical column.")
            else:
                logging.error("Invalid encoding method provided: %s", method)
                raise ValueError("Choose method from ('onehot', 'label')")



    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> None:
        logging.info("Fitting encoder on categorical columns: %s", self.cat_cols)
        if self.encoder_passed:
            logging.info("Encoder already provided, skipping fit.")
            return self
        if self.method == "onehot":
            self.encoder.fit(X[self.cat_cols])
            logging.info("OneHotEncoder fitted successfully.")
        else:
            for col in self.cat_cols:
                self.encoder[col].fit(X[col])
                logging.info("LabelEncoder fitted successfully for column: %s", col)
        return self



    def transform(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> pd.DataFrame:
        logging.info("Transforming categorical columns using %s encoding.", self.method)
        X_copy = X.copy()

        if self.method == "onehot":
            encoded_array = self.encoder.transform(X_copy[self.cat_cols])
            joblib.dump(self.encoder, processing_configs['one_hot_encoder_file_path'])
            logging.info("OneHotEncoder object saved to %s", processing_configs['one_hot_encoder_file_path'])
            encoded_df = pd.DataFrame(
                encoded_array,
                columns=self.encoder.get_feature_names_out(self.cat_cols),
                index=X_copy.index
            )
            X_copy = pd.concat([X_copy.drop(columns=self.cat_cols), encoded_df], axis=1)
            logging.info("One-hot encoding transformation completed.")

        elif self.method == "label":
            for col in self.cat_cols:
                X_copy[col] = self.encoder[col].transform(X_copy[col])
                joblib.dump(self.encoder[col], os.path.join(processing_configs['label_encoder_folder_path'], col + '.pkl'))
                logging.info("LabelEncoder for column '%s' saved successfully.", col)

        logging.info("Categorical encoding transformation completed.")
        return X_copy



class Imputer:
    """
    This class is responsible for imputing missing values.
    """


    def __init__(self, cat_cols:list, num_cols:list, num_method:str, cat_method:str='most_frequent'):
        logging.info("Initializing Imputer with cat_method: %s, num_method: %s", cat_method, num_method)
        self.cat_cols = cat_cols
        self.num_cols = num_cols
        self.cat_method = cat_method
        self.num_method = num_method



    def __findReplacements(self, X: pd.DataFrame) -> tuple:
        logging.info("Finding replacement values for missing data.")
        cat_rep = {}
        num_rep = {}

        if self.cat_method == "most_frequent":
            for col in self.cat_cols:
                cat_rep[col] = X[col].mode()[0]
                logging.info("Most frequent value for column '%s' is '%s'", col, cat_rep[col])
        else:
            logging.error("Invalid categorical imputation method: %s", self.cat_method)
            raise ValueError("Choose method from ('most_frequent')")


        if self.num_method == "mean":
            for col in self.num_cols:
                num_rep[col] = X[col].mean()
                logging.info("Mean value for column '%s' is '%s'", col, num_rep[col])
        elif self.num_method == "median":
            for col in self.num_cols:
                num_rep[col] = X[col].median()
                logging.info("Median value for column '%s' is '%s'", col, num_rep[col])
        elif self.num_method == "mode":
            for col in self.num_cols:
                num_rep[col] = X[col].mode()[0]
                logging.info("Mode value for column '%s' is '%s'", col, num_rep[col])
        else:
            logging.error("Invalid numeric imputation method: %s", self.num_method)
            raise ValueError("Choose method from ('mean', 'median', 'mode')")

        logging.info("Replacement values determined successfully.")
        return cat_rep, num_rep



    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> None:
        logging.info("Fitting Imputer to find replacement values.")
        self.cat_rep, self.num_rep = self.__findReplacements(X=X)
        logging.info("Imputer fitted successfully.")
        return self



    def transform(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> pd.DataFrame:
        logging.info("Transforming dataset by imputing missing values.")
        X_copy = X.copy()
        for col in self.cat_cols:
            X_copy[col] = X_copy[col].fillna(self.cat_rep[col])
            logging.info("Filled missing categorical values for column: %s", col)

        for col in self.num_cols:
            X_copy[col] = X_copy[col].fillna(self.num_rep[col])
            logging.info("Filled missing numeric values for column: %s", col)

        logging.info("Imputation transformation completed successfully.")
        return X_copy
