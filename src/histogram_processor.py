import numpy as np


class HistogramProcessor:
    def __init__(self, df):
        self.df = df

    def remove_outliers(self, numerical_fields):
        for field in numerical_fields:
            Q1 = self.df[field].quantile(0.25)
            Q3 = self.df[field].quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[~((self.df[field] < (Q1 - 1.5 * IQR)) | (self.df[field] > (Q3 + 1.5 * IQR)))]

    def aggregate_data(self, numerical_fields, aggregation_method):
        numerical_fields.append('symbol')
        if aggregation_method == 'median':
            return self.df[numerical_fields].groupby('symbol').median()
        else:
            return self.df[numerical_fields].groupby('symbol').mean()

    @staticmethod
    def calculate_histograms(aggregated_df, numerical_fields, num_bins):
        histograms = {}
        for column in numerical_fields:
            hist, bin_edges = np.histogram(aggregated_df[column].dropna(), bins=num_bins)
            histograms[column] = {"hist": hist.tolist(), "bin_edges": bin_edges.tolist()}
        return histograms
