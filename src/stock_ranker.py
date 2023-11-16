import pandas as pd


class StockRanker:
    def __init__(self, stocks_df, selected_features):
        self.stocks_df = stocks_df
        self.selected_features = selected_features
        self.selected_features_names = [item['feature'] for item in self.selected_features]

    def rank_stocks(self):
        self.stocks_df['score'] = self.calculate_scores()

        self.stocks_df = self.stocks_df.groupby('symbol')[['score'] + self.selected_features_names].mean()

        # Sort by score and add rank
        print(self.stocks_df)
        ranked_stocks_df = self.stocks_df.sort_values(by='score', ascending=False).reset_index()
        ranked_stocks_df['rank'] = ranked_stocks_df.index + 1

        print(self.selected_features_names)
        return ranked_stocks_df[['rank', 'symbol', 'score'] + self.selected_features_names]

    def calculate_scores(self):
        # Normalize each feature
        normalized_df = ((self.stocks_df[self.selected_features_names] -
                          self.stocks_df[self.selected_features_names].min()) /
                         (self.stocks_df[self.selected_features_names].max() -
                          self.stocks_df[self.selected_features_names].min()))

        score_series = pd.Series(0, index=self.stocks_df.index)
        for feature_info in self.selected_features:
            feature = feature_info['feature']
            weight = feature_info['weight']
            if feature in self.stocks_df.columns:
                score_series += normalized_df[feature].fillna(0) * weight
        return score_series
