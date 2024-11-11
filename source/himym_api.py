import pandas as pd


class HIMYMAPI:

    data = None

    def load_data(self):
        # Load the data into a dataframe
        # Source gave two dataframes, so merge them and drop repeat columns
        episode_data = pd.read_csv("himym_episodes.csv")
        imdb_data = pd.read_csv("himym_imdb.csv")
        nlp_data = pd.read_csv("HIMYM_NLP.csv")
        merged = episode_data.join(imdb_data, lsuffix = "_l", rsuffix = "_r")
        merged = merged.drop(["season_l", "title_l", "original_air_date_l"], axis = 1)
        merged = merged.rename(columns = {"season_r": "season", "title_r": "title",
                                          "original_air_date_r": "original_air_date"})
        merged.DateAired = pd.to_datetime(merged.original_air_date, format="mixed")
        merged = merged.merge(nlp_data, left_on='episode_num_overall', right_on='Episode', how='inner')
        self.data = merged

    def get_series(self, series_name):
        # fetch a series from the data
        return self.data[series_name]

