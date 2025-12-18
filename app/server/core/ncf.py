import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import DataLoader, Dataset

class NCFModel(nn.Module):
    def __init__(self, n_users, n_items, emb_dim=32):
        super().__init__()

        self.user_emb = nn.Embedding(n_users, emb_dim)
        self.item_emb = nn.Embedding(n_items, emb_dim)

        self.mlp = nn.Sequential(
            nn.Linear(emb_dim * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, user_ids, item_ids):
        u = self.user_emb(user_ids)
        i = self.item_emb(item_ids)
        x = torch.cat([u, i], dim=1)
        return self.mlp(x).squeeze()



# ---------- DATASET ----------
class InteractionDataset(Dataset):
    def __init__(self, df):
        self.users = torch.LongTensor(df["user_idx"].values)
        self.items = torch.LongTensor(df["poi_idx"].values)
        self.labels = torch.FloatTensor(df["label"].values)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.labels[idx]


# ---------- RECOMMENDER ----------
class NCFRecommender:
    def __init__(self, emb_dim=32, device=None):
        self.model_name = "NCF"
        self.emb_dim = emb_dim
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = None
        self.user_encoder = LabelEncoder()
        self.poi_encoder = LabelEncoder()

    # ---------- USER ID BUILDER ----------
    def build_user_id(self, city, user_type, price_level):
        city = city.lower().strip()
        user_type = user_type.lower().strip()
        return f"{city}_{user_type}_{price_level}"

    # ---------- TRAIN ----------
    def train(self, df, epochs=100, batch_size=512, lr=1e-3):
        df = df.copy()

        df["user_idx"] = self.user_encoder.fit_transform(df["user_id"])
        df["poi_idx"] = self.poi_encoder.fit_transform(df["poi_id"])

        self.model = NCFModel(
            df["user_idx"].nunique(),
            df["poi_idx"].nunique(),
            self.emb_dim
        ).to(self.device)

        dataset = InteractionDataset(df)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        self.model.train()
        for e in range(epochs):
            losses = []
            for u, i, y in loader:
                u, i, y = u.to(self.device), i.to(self.device), y.to(self.device)

                optimizer.zero_grad()
                preds = self.model(u, i)
                loss = criterion(preds, y)
                loss.backward()
                optimizer.step()

                losses.append(loss.item())

            print(f"[NCF] Epoch {e+1}/{epochs} - Loss: {np.mean(losses):.4f}")

    # ---------- RECOMMEND ----------
    def recommend(self, df_raw, city, user_type, user_price, top_k=50):
        self.model.eval()

        city = city.lower().strip()
        user_type = user_type.lower().strip()
        price_level = user_price
        user_id = self.build_user_id(city, user_type, price_level)

        # --- Cold-start user ---
        if user_id not in self.user_encoder.classes_:
            print("⚠️ Cold-start user profile")
            return pd.DataFrame()

        # --- Filter city ---
        subset = df_raw[df_raw["city_norm"] == city].copy()
        if subset.empty:
            return pd.DataFrame()

        uid = self.user_encoder.transform([user_id])[0]

        # --- Encode POI ---
        subset["poi_idx"] = subset["poi_id"].apply(
            lambda x: self.poi_encoder.transform([x])[0]
            if x in self.poi_encoder.classes_ else -1
        )
        subset = subset[subset["poi_idx"] >= 0]

        if subset.empty:
            return pd.DataFrame()

        # --- Predict ---
        u = torch.LongTensor([uid] * len(subset)).to(self.device)
        i = torch.LongTensor(subset["poi_idx"].values).to(self.device)

        with torch.no_grad():
            subset["score"] = self.model(u, i).cpu().numpy()

        # --- OUTPUT SCHEMA CHUẨN ---
        return (
            subset[[
                "poi_id",
                "name",
                "score",
                "latitude",
                "longitude",
                "type",
                "price",
                "price_level"
            ]]
            .rename(columns={"type": "poi_type"})
            .sort_values("score", ascending=False)
            .head(top_k)
            .reset_index(drop=True)
        )

    # ---------- SAVE / LOAD ----------
    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "state_dict": self.model.state_dict(),
            "user_encoder": self.user_encoder,
            "poi_encoder": self.poi_encoder,
            "emb_dim": self.emb_dim
        }
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        print(f"✓ [NCF] Model saved to {path}")

    def load(self, path):
        with open(path, "rb") as f:
            payload = pickle.load(f)

        self.emb_dim = payload["emb_dim"]
        self.user_encoder = payload["user_encoder"]
        self.poi_encoder = payload["poi_encoder"]

        self.model = NCFModel(
            len(self.user_encoder.classes_),
            len(self.poi_encoder.classes_),
            self.emb_dim
        ).to(self.device)

        self.model.load_state_dict(payload["state_dict"])
        self.model.eval()
        print("✓ [NCF] Model loaded")

