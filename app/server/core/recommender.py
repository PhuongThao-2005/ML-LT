from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor
from .base import BaseRecommender

class LinearRecommender(BaseRecommender):
    def __init__(self):
        super().__init__(model_name="LinearRegression")

    def train(self, df):
        df = self.feature_engineering(df)
        df = self.fit_encoders(df)

        X = df[self.features]
        y = df["label"]

        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X)

        self.model = LinearRegression()
        self.model.fit(X, y)

        print(f"[{self.model_name}] Training finished.")


class RandomForestRecommender(BaseRecommender):
    def __init__(self):
        super().__init__(model_name="RandomForest")
    
    def train(self, df):
        df = self.feature_engineering(df)
        df = self.fit_encoders(df)

        X = df[self.features]
        y = df["label"]

        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            max_features=0.7,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X, y)
        print(f"[{self.model_name}] Training finished.")


class CatBoostRecommender(BaseRecommender):
    def __init__(self):
        super().__init__(model_name="CatBoost")

    def train(self, train_df, val_df=None):
        train_df = self.feature_engineering(train_df)

        for col in self.cat_features:
            train_df[col] = train_df[col].astype(str).fillna("unknown")

        X_train = train_df[self.features]
        y_train = train_df["label"]

        eval_set = None

        if val_df is not None:
            val_df = self.feature_engineering(val_df)
            for col in self.cat_features:
                val_df[col] = val_df[col].astype(str).fillna("unknown")

            X_val = val_df[self.features]
            y_val = val_df["label"]
            eval_set = (X_val, y_val)

        self.model = CatBoostRegressor(
            iterations=500,
            depth=6,
            learning_rate=0.05,
            loss_function="RMSE",
            eval_metric="MAE",
            verbose=False,
            allow_writing_files=False,
            early_stopping_rounds=50 if val_df is not None else None
        )

        self.model.fit(
            X_train,
            y_train,
            cat_features=self.cat_features,
            eval_set=eval_set,
            use_best_model=val_df is not None
        )

        print(f"[{self.model_name}] Training finished.")