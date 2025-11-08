from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
import pandas as pd
from typing import Union
import joblib
import json

processing_configs = json.load(open("src/processing_config.json"))


class ScaleData:
    """
    This class is responsible for scaling numeric data columns.
    """

    def __init__(self, num_cols: list, method: str):
        """
        Args:
            num_cols: list of column names that need to be scaled
            method: Choose string from ('standard', 'minmax')
        """
        self.num_cols = num_cols
        if method == "standard":
            self.scaler = StandardScaler()
        elif method == "minmax":
            self.scaler = MinMaxScaler()
        else:
            raise ValueError("Choose method from ('standard', 'minmax')")

    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> None:
        """
        Fits the scaler on numeric columns.
        """
        self.scaler.fit(X[self.num_cols])
        return self


    def transform(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> pd.DataFrame:
        """
        Transforms numeric columns and returns formatted DataFrame.
        """
        X_copy = X.copy()
        scaled_values = self.scaler.transform(X_copy[self.num_cols])
        joblib.dump(self.scaler, processing_configs['scaler_file_path'])
        X_copy[self.num_cols] = pd.DataFrame(
            scaled_values, columns=self.num_cols, index=X_copy.index
        )
        return X_copy



class EncodelData:
    """
    This class is responsible for labeling categorical columns.
    """



    def __init__(self, cat_cols: list, method: str):
        """
        Args:
            cat_cols: list of column names that need to be labelled
            method: Choose string from ('onehot', 'label')
        """
        self.cat_cols = cat_cols
        self.method = method

        if method == "onehot":
            self.encoder = OneHotEncoder(sparse_output=False, drop=None, handle_unknown="ignore")
        elif method == "label":
            self.encoder = {col: LabelEncoder() for col in cat_cols}
        else:
            raise ValueError("Choose method from ('onehot', 'label')")



    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> None:
        """
        Fitting data before transformation.
        """
        if self.method == "onehot":
            self.encoder.fit(X[self.cat_cols])
        else:  # label encoding
            for col in self.cat_cols:
                self.encoder[col].fit(X[col])
        return self



    def transform(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> pd.DataFrame:
        """
        Transforms categorical columns and returns formatted DataFrame.
        """
        X_copy = X.copy()

        if self.method == "onehot":
            encoded_array = self.encoder.transform(X_copy[self.cat_cols])
            joblib.dump(self.encoder, processing_configs['one_hot_encoder_file_path'])
            encoded_df = pd.DataFrame(
                encoded_array,
                columns=self.encoder.get_feature_names_out(self.cat_cols),
                index=X_copy.index
            )
            X_copy = pd.concat([X_copy.drop(columns=self.cat_cols), encoded_df], axis=1)

        elif self.method == "label":
            for col in self.cat_cols:
                X_copy[col] = self.encoder[col].transform(X_copy[col])
                joblib.dump(self.encoder, os.path.join(processing_configs['label_encoder_folder_path'], col + '.pkl'))

        return X_copy



class Imputer:
    """
    This class is responsible for imputing missing values.
    """


    def __init__(self, cat_cols:list, num_cols:list, num_method:str, cat_method:str='most_frequent'):
        """
        Args:
            cat_cols: list of column names that need to be imputed
            num_cols: list of column names that need to be imputed
            cat_method: Choose string from ('most_frequent')
            num_method: Choose string from ('mean', 'median', 'mode')
        """
        self.cat_cols = cat_cols
        self.num_cols = num_cols
        self.cat_method = cat_method
        self.num_method = num_method



    def __findReplacements(self, X: pd.DataFrame) -> tuple:
        """
        Args:
            X: pd.DataFrame
        Description:
            Finds the values which needs to be imputed for categorical and numerical columns.
        Returns:
            pd.DataFrame
        """

        cat_rep = {}
        num_rep = {}

        if self.cat_method == "most_frequent":
            for col in self.cat_cols:
                cat_rep[col] = X[col].mode()[0]
        else:
            raise ValueError("Choose method from ('most_frequent')")


        if self.num_method == "mean":
            for col in self.num_cols:
                num_rep[col] = X[col].mean()
        elif self.num_method == "median":
            for col in self.num_cols:
                num_rep[col] = X[col].median()
        elif self.num_method == "mode":
            for col in self.num_cols:
                num_rep[col] = X[col].mode()[0]
        else:
            raise ValueError("Choose method from ('mean', 'median', 'mode')")

        return cat_rep, num_rep



    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> None:
        """
        Finding value to be replaced with missing values for categorical and numeric columns.
        """
        self.cat_rep, self.num_rep = self.__findReplacements(X=X)
        return self



    def transform(self, X: pd.DataFrame, y: Union[pd.Series, None] = None) -> pd.DataFrame:
        """
        Fills missing values with imputed values for categorical and numeric columns.
        """
        X_copy = X.copy()
        for col in self.cat_cols:
            X_copy[col] = X_copy[col].fillna(self.cat_rep[col])

        for col in self.num_cols:
            X_copy[col] = X_copy[col].fillna(self.num_rep[col])
        return X_copy
