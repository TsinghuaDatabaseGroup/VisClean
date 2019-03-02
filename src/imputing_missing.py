"""Impute missing values with k nearest classifier."""
import pandas as pd
import datawig_imputation


if __name__ == "__main__":
    path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp/DBPublications-input_id.csv'
    df = pd.read_csv(path)
    print(df.head())



    df_train, df_test = datawig_imputation.utils.random_split(df)

    # Initialize a SimpleImputer model
    missing_imputer = datawig_imputation.SimpleImputer(
        input_columns=['Citations'],  # column(s) containing information about the column we want to impute
        output_column='Citations',  # the column we'd like to impute values for
        output_path='imputer_model'  # stores model data and metrics
    )

    # Fit an imputer model on the train data
    missing_imputer.fit(train_df=df_train, num_epochs=50)

    # Impute missing values and return original dataframe with predictions
    imputed_res = missing_imputer.predict(df_test)
    print(imputed_res.head())
    imputed_res.to_csv('/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp/imputing_res.csv', index= False)