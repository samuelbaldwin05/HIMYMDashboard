import panel as pn
from plotly.graph_objs.indicator.gauge import Threshold

from himym_api import HIMYMAPI
import sankey as sk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
pn.extension('plotly')

# Loads javascript dependencies and configures Panel (required)
pn.extension()

# Initialize API object
api = HIMYMAPI()
api.load_data()

pn.config.theme = "dark"

# Map display names to column names in dataframe using dictionary
options = {
    "US Viewers (Tens of Millions)": "us_viewers",
    "IMDB Rating": "imdb_rating",
    "Episode Number": "episode_num_overall",
    "Director": "directed_by",
    "Writer": "written_by",
    "Season": "season",
    "Main Character": "main character",
    "Barney Phrases Per Episode": "barney phrase #", # Barney phrases are phrases that the character Barney is
    # iconic for saying in the show. We counted how many of these occurred in each episode. Phrases included
    # 'legendary', 'awesome', and 'suit up'.
    "Sentiment Score": "sentiment",
    "Nothing": "nothing"
}

# WIDGET DECLARATIONS
# Select data that is applicable to each graph and organize it into respective widgets
bar_options = {key: options[key] for key in ["Writer", "Director", "Main Character", "Season"]}

bar_x_value = pn.widgets.Select(
    name="Bar Label",
    options=list(bar_options.keys()),
    value="Writer"
)

line_x_options = {key : options[key] for key in ["Episode Number", "Season"]}

line_x_value = pn.widgets.Select(
    name = "X Axis",
    options = list(line_x_options.keys()),
    value = "Episode Number"
)

hist_options = {key: options[key] for key in ["IMDB Rating", "US Viewers (Tens of Millions)",
                                              "Sentiment Score", "Barney Phrases Per Episode"]}
hist_x_value = pn.widgets.Select(
    name = "X Axis",
    options = list(hist_options.keys()),
    value = "IMDB Rating"
)

line_y_options = {key: options[key] for key in ["IMDB Rating", "US Viewers (Tens of Millions)",
                                              "Sentiment Score", "Barney Phrases Per Episode"]}
line_y_value = pn.widgets.Select(
    name = "Y Axis",
    options = list(line_y_options.keys()),
    value = "IMDB Rating"
)
scatter_x_options = {key: options[key] for key in ["IMDB Rating", "US Viewers (Tens of Millions)",
                                              "Sentiment Score", "Barney Phrases Per Episode"]}
scatter_x_value = pn.widgets.Select(
    name = "X Axis",
    options = list(scatter_x_options.keys()),
    value = "IMDB Rating"
)
scatter_y_options = {key: options[key] for key in ["IMDB Rating", "US Viewers (Tens of Millions)",
                                              "Sentiment Score", "Barney Phrases Per Episode"]}
scatter_y_value = pn.widgets.Select(
    name = "Y Axis",
    options = list(scatter_y_options.keys()),
    value = "Sentiment Score"
)

box_x_options = {key: options[key] for key in ["Season", "Director", "Writer", "Main Character"]}
box_x_value = pn.widgets.Select(
    name = "X Axis",
    options = list(box_x_options.keys()),
    value = "Season"
)

box_y_options = {key: options[key] for key in ["IMDB Rating", "US Viewers (Tens of Millions)",
                                               "Sentiment Score", "Barney Phrases Per Episode"]}
box_y_value = pn.widgets.Select(
    name = "Y Axis",
    options = list(box_y_options.keys()),
    value = "IMDB Rating"
)


# Sankey variable inputs

var1_options = {key: options[key] for key in ["US Viewers (Tens of Millions)", "IMDB Rating", "Episode Number",
                                              "Director", "Season", "Barney Phrases Per Episode",
                                               "Writer", "Main Character"]}
sankey_var_1 = pn.widgets.Select(
    name = "Data Comparison 1",
    options = list(var1_options.keys()),
    value = "Season"
)

var23_options = {key: options[key] for key in ["US Viewers (Tens of Millions)", "IMDB Rating", "Director",
                                               "Writer", "Main Character", "Nothing"]}
sankey_var_2 = pn.widgets.Select(
    name = "Data Comparison 2",
    options = list(var23_options.keys()),
    value = "Nothing"
)

sankey_var_3 = pn.widgets.Select(
    name = "Data Comparison 3",
    options = list(var23_options.keys()),
    value = "Nothing"
)

# Create widget to select a regression line
regression_line = pn.widgets.Checkbox(name="Add Regression Line", value=False)

# Color selector widget for graph colors
color_choice = pn.widgets.ColorPicker(name='Graph Color', value='#4169E1')

# Create sliders for histogram, bar chart, and boxplot to select number of items on x axis
# Also create slider for season selection in line chart
bins_amt = pn.widgets.IntSlider(
    name = "Amount of Bins in Histogram",
    start = 1,
    end = 20,
    step = 1,
    value = 5
)

season_slider = pn.widgets.IntSlider(
    name = "Season Selection",
    start = 1,
    end = 9,
    step = 1,
    value = 1
)

bars_amt = pn.widgets.IntSlider(
    name = "Max Bars in Bar Chart",
    start = 1,
    end = 32,
    step = 1,
    value = 5,
)

boxes_amt = pn.widgets.IntSlider(
    name = "Max Boxes in Box and Whisker Plot",
    start = 1,
    end = 32,
    step = 1,
    value = 5
)

# Sankey threshold slider
threshold_amt = pn.widgets.IntSlider(
    name = "Count threshold",
    start = 1,
    end = 10,
    step = 1,
    value = 1
)

# CALLBACK FUNCTIONS
def line_plot(x, y, season_selection, color, add_line=False):
    """
    Given an x and y from the selector with the options for the line plot, create a line plot
    Takes in a season selection for the case that the user want to examine a single season
    Change the color with color
    If regression line is ticked true, add a regression line with slope and fit details
    """
    x_data = api.get_series(options[x])
    y_data = api.get_series(options[y])
    # CASE 1: Plotting over the episodes of the entire series
    if x == "Episode Number":
        x_values = x_data
        y_values = y_data
        x_label = "Data From All Episodes"
    # CASE 2: Selecting an individual season. In this case we must fetch the episode numbers per season and filter
    # our data to correspond to a single season
    else:
        episode_nums = api.get_series("episode_num_in_season")
        x_values = episode_nums[x_data == season_selection]
        y_values = y_data[x_data == season_selection]
        x_label = f"Data From Season {season_selection}"
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, color = color)
    plt.title(f'{x} vs {y}')
    plt.xlabel(x_label)
    plt.ylabel(y)

    # if regression specified calculate regression and add to graph
    if add_line:
        slope, intercept = np.polyfit(x_values, y_values, 1)
        reg_line = slope * np.array(x_values) + intercept
        # Calculate R squared
        ss_res = np.sum((y_values - reg_line) ** 2)
        ss_tot = np.sum((y_values - np.mean(y_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        ax.plot(x_values, reg_line, color="red",
                label=(f"Regression Line\nSlope: {slope:.2f}\nFit: {r_squared:.2f}"))
        ax.legend()
    return fig

def scatter_plot(x, y, color, add_line=False):
    """
    Given an x and y from the selector with the options for the scatter plot, create a scatter plot
    Change the color with color
    If regression line is ticked true, add a regression line with slope and fit details
    """
    x_data = api.get_series(options[x])
    y_data = api.get_series(options[y])
    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data, color = color)
    plt.title(f'{x} vs {y}')
    plt.xlabel(x)
    plt.ylabel(y)

    # if regression specified calculate regression and add to graph
    if add_line:
        slope, intercept = np.polyfit(x_data, y_data,1)
        reg_line = slope * np.array(x_data) + intercept
        ss_res = np.sum((y_data - reg_line) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        ax.plot(x_data, reg_line, color="red", label=(f"Regression Line\nSlope: {slope:.2f}\nFit: {r_squared:.2f}"))
        ax.legend()
    return fig

def bar_chart(x, bars, color):
    """
    Given an x from the selector with the options for the bar chart, create a bar chart with the value counts
    of the selected x
    From the slider, chose the number of bars shown. Filter to only have 9 bars if season is selected
    as there are 9 seasons
    Change font and rotation if the x is writer as there are 32 writers and not all xticks fit
    Change the color with color
    """
    x_data = api.get_series(options[x])
    if x == "Season":
        bars = 9
    value_counts = x_data.value_counts().nlargest(bars)
    fig, ax = plt.subplots()
    ax.bar(value_counts.index, value_counts.values, color = color, edgecolor = "black")
    plt.title(f'Frequency of Episodes By {x}')
    plt.xlabel(x)
    plt.ylabel("Frequency")
    if x == "Writer":
        plt.xticks(rotation=90, fontsize=6)
    else:
        plt.xticks(rotation=0, fontsize=8)
    plt.tight_layout()
    return fig

def histogram(x, bins, color):
    """
    Given an x from the selector with the options for the histogram, create a histogram with the value counts
    of the selected x
    From the slider, chose the number of bins
    Change the color with color
    """
    x_data = api.get_series(options[x])
    fig, ax = plt.subplots()
    ax.hist(x_data, bins = bins, color = color, edgecolor = "black")
    plt.title(f"Histogram of {x}")
    plt.xlabel(x)
    plt.ylabel("Frequency of Episodes")
    return fig

def boxplot(x, y, boxes, color):
    """
    Given an x and y from the selector with the options for the box plot, create a box plot
    From the slider, chose the number of boxes shown. Filter to only have 9 bars if season is selected
    as there are 9 seasons
    Change font and rotation if the x is writer as there are 32 writers and not all xticks fit
    Change the color with color
    """
    x_data = api.get_series(options[x])
    y_data = api.get_series(options[y])
    df = pd.concat([x_data, y_data], axis = 1)
    if x == "Season":
        boxes = 9
    x_value_counts = x_data.value_counts(sort = False).nlargest(boxes)
    df_filtered = df[df[options[x]].isin(x_value_counts.index)]
    x_values = df_filtered[options[x]]
    y_values = df_filtered[options[y]]
    fig = plt.figure(figsize = (7, 4))
    sns.boxplot(x = x_values, y = y_values, color = color)
    plt.xlabel(x)
    plt.ylabel(y)
    if x == "Writer":
        plt.xticks(rotation=90, fontsize=6)
    else:
        plt.xticks(rotation=0, fontsize=8)
    plt.title(f"Box and Whisker plot of {y} by {x}")
    plt.tight_layout()
    return fig

def sankey(x, y, z, threshold):
    """
    Given variables x, y, and z create a stacked (or unstacked depending on xyz values) sankey diagram.
    From the slider for threshold, the weight of each line will be limited to a certain minimum value from this input.
    If there is only one valid variable given for xyz a funny plot (says "You've done nothing") gets shown.
    If only two valid variables are given then a regular sankey diagram is shown.
    """
    # Getting variable list
    cols = [x,y,z]

    if x == y or x == z:
        cols.remove(x)
    if y == z or y == z:
        cols.remove(y)

    for col in cols:
        if col == "Nothing":
            cols.remove(col)

    # If cols has 1 or less items then return a blank figure
    if len(cols) <= 1:
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.text(0.5, 0.5, "Select Categories To Display", ha='center', va='center', fontsize=20)
        return fig

    # Getting df
    df = pd.DataFrame()
    df_cols = []
    for col in cols:
        if col == "IMDB Rating":
            df_cols.append(col)
            imdb_series = api.get_series(options[col])
            imdb_int = imdb_series.astype(int)
            imdb_range = imdb_int.astype(str) + ".0-" + imdb_int.astype(str) + ".9"
            df_col = pd.DataFrame(imdb_range)
        else:
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

# CALLBACK BINDINGS
line = pn.bind(line_plot, line_x_value, line_y_value, season_slider, color_choice, regression_line)

scatter = pn.bind(scatter_plot, scatter_x_value, scatter_y_value, color_choice, regression_line)

bar = pn.bind(bar_chart, bar_x_value, bars_amt, color_choice)

hist = pn.bind(histogram, hist_x_value, bins_amt, color_choice)

box = pn.bind(boxplot, box_x_value, box_y_value, boxes_amt, color_choice)

sankey = pn.bind(sankey, sankey_var_1, sankey_var_2, sankey_var_3, threshold_amt)


# DASHBOARD WIDGET CONTAINERS
card_width = 320

plot_card = pn.Card(
    pn.Column(
        regression_line,
        color_choice
    ),
    title="Plot", width=card_width, collapsed=False
)
line_chart_card = pn.Card(
    pn.Column(
        line_x_value,
        line_y_value,
        season_slider
    ),
    title="Line Plot", width=card_width, collapsed=False
)
scatter_card = pn.Card(
    pn.Column(
        scatter_x_value,
        scatter_y_value,
    ),
    title="Scatterplot", width=card_width, collapsed=True
)
bar_plot_card = pn.Card(
    pn.Column(
        bars_amt,
        bar_x_value
    ),
    title="Bar Chart", width=card_width, collapsed=True
)

histogram_card = pn.Card(
    pn.Column(
        bins_amt,
        hist_x_value
    ),
    title="Histogram", width=card_width, collapsed=True
)
box_card = pn.Card(
    pn.Column(
        box_x_value,
        box_y_value,
        boxes_amt
    ),
    title="Box and Whisker", width=card_width, collapsed=True
)

sankey_card = pn.Card(
    pn.Column(
        sankey_var_1,
        sankey_var_2,
        sankey_var_3,
        threshold_amt
    ),
    title="Sankey Diagram", width=card_width, collapsed=True
)

# LAYOUT
layout = pn.template.FastListTemplate(
    title="How I Met Your Mother Episode Dashboard",
    sidebar=[plot_card, line_chart_card, scatter_card, bar_plot_card, histogram_card, box_card, sankey_card],
    theme_toggle=False,
    theme="dark",
    main=[
        pn.Tabs(
            ("Line Plot", line),
            ("Scatterplot", scatter),
            ("Bar Chart", bar),
            ("Histogram", hist),
            ("Box and Whisker Plot", box),
            ("Sankey Diagram", sankey),
            active=0
        )
    ],
    header_background='#4169E1'
).servable()

layout.show()
