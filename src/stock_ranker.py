import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class StockRanker:
    def __init__(self, stocks_df, selected_features, decay_rate, decay_function):
        self.stocks_df = stocks_df
        self.selected_features = selected_features
        self.selected_features_names = [item['feature'] for item in self.selected_features]
        self.decay_rate = decay_rate
        self.decay_function = decay_function

    def rank_stocks(self):
        self.stocks_df['score'] = self.calculate_scores()
        group_by_columns = self.selected_features_names.copy()
        group_by_columns.append('score')
        self.stocks_df = self.stocks_df.groupby(['symbol'])[group_by_columns].mean()

        # Sort by score and add rank
        ranked_stocks_df = self.stocks_df.sort_values(by='score', ascending=False).reset_index()
        ranked_stocks_df['rank'] = ranked_stocks_df.index + 1
        return ranked_stocks_df[['rank', 'symbol', 'score'] + self.selected_features_names]

    def calculate_scores(self):
        self.apply_decay()

        # Normalize each feature
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(self.stocks_df[self.selected_features_names])
        normalized_df = pd.DataFrame(normalized_data, columns=self.selected_features_names)

        score_series = pd.Series(0, index=self.stocks_df.index)
        for feature_info in self.selected_features:
            feature = feature_info['feature']
            weight = feature_info['weight']
            if feature in self.stocks_df.columns:
                decayed_feature_values = normalized_df[feature].fillna(0) * self.stocks_df['decay']
                score_series += decayed_feature_values * weight
        return score_series

    def apply_decay(self):
        self.stocks_df['days_from_recent'] = (self.stocks_df['date'].max() - self.stocks_df['date']).dt.days
        if self.decay_function == 'linear':
            self.stocks_df['decay'] = 1 - (self.decay_rate / 100) * self.stocks_df['days_from_recent']
        elif self.decay_function == 'exponential':
            self.stocks_df['decay'] = np.exp(-self.decay_rate * self.stocks_df['days_from_recent'])
        elif self.decay_function == 'logarithmic':
            # Avoid log(0) issue
            self.stocks_df['decay'] = 1 / np.log(self.stocks_df['days_from_recent'] + 1)
        else:
            # No decay
            self.stocks_df['decay'] = 1

        self.stocks_df['decay'] = self.stocks_df['decay'].clip(lower=0)
