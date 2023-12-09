import numpy as np
import pandas as pd

class HistogramProcessor:
    def __init__(self, df):
        self.df = df

    def remove_outliers(self, numerical_fields):
        for field in numerical_fields:
            Q1 = self.df[field].quantile(0.25)
            Q3 = self.df[field].quantile(0.75)
            IQR = Q3 - Q1
            outlier_condition = ~((self.df[field] < (Q1 - 1.5 * IQR)) | (self.df[field] > (Q3 + 1.5 * IQR)))
            self.df.loc[~outlier_condition, field] = np.nan

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
            # Calculate histogram and bin edges
            hist, bin_edges = np.histogram(aggregated_df[column].dropna(), bins=num_bins)

            # Create a DataFrame to map stocks to bins
            bin_mapping = pd.DataFrame({
                column: aggregated_df[column],
                'symbol': aggregated_df.index,
                'bin': pd.cut(aggregated_df[column], bins=bin_edges, labels=range(num_bins), include_lowest=True)
            })

            # Group by bin and list symbols
            binned_symbols = bin_mapping.groupby('bin')['symbol'].apply(list).to_dict()

            # Add the histogram and bin edges to the results
            histograms[column] = {
                "hist": hist.tolist(),
                "bin_edges": bin_edges.tolist(),
                "binned_symbols": binned_symbols
            }
        return histograms
