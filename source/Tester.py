import pandas as pd
import panel as pn
from himym_api import HIMYMAPI
import sankey as sk
import matplotlib.pyplot as plt
import numpy as np

# Loads javascript dependencies and configures Panel (required)
pn.extension()

api = HIMYMAPI()
api.load_data()

# Map display names to column names in dataframe using dictionary
options = {
    "US Viewers (Tens of Millions)": "us_viewers",
    "IMDB Rating": "imdb_rating",
    "Episode Number": "episode_num_overall",
    "Director": "directed_by",
    "Writer": "written_by",
    "Season": "season",
    "Main Character": "main character",
    "Barney Phrases": "barney phrase #",
    "Sentiment Score": "sentiment"
}


def sankey(x, y, z, threshold):
    # Getting variable list

    cols = [x,y,z]

    if x == y or x == z:
        cols.remove(x)
    if y == z or y == z:
        cols.remove(y)

    for col in cols:
        if col == "Nothing":
            cols.remove(col)

    if len(cols) <= 1:
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.text(0.5, 0.5, "You did nothing", ha='center', va='center', fontsize=20)
        return fig

    # Getting df
    df = pd.DataFrame()
    df_cols = []
    for col in cols:
        df_cols.append(col)
        df_col = pd.DataFrame(api.get_series(options[col]).astype(str))
        df[col] = df_col[options[col]]

    # Creating figure
    fig = sk.make_sankey(df, df_cols, threshold=threshold)
    for x_coordinate, column_name in enumerate(cols):
        fig.add_annotation(
            x=x_coordinate,
            y=1.1,
            xref="x",
            yref="paper",
            text=column_name,
            showarrow=False,
            font=dict(
                family="Courier New, monospace",
                 size=16,
                color="Purple"
            ),
            align="center",
        )
    fig.update_layout(
        title_text=f"Sankey Diagram of:",
        xaxis={
            'showgrid': False,  # getting rid of grid
            'zeroline': False,  # getting rid of line
            'visible': False,  # getting rid of numbers
        },
        yaxis={
            'showgrid': False,  # getting rid of grid
            'zeroline': False,  # getting rid of line
            'visible': False,  # getting rid of numbers
        }, plot_bgcolor='rgba(0,0,0,0)', font_size=10)
    return fig

def main():
    x = "Barney Phrases"
    y = "Writer"
    z = "Writer"
    threshold = 1

    fig = sankey(x, y, z, threshold=threshold)
    fig.show()

main()