import plotly.graph_objects as go
import pandas as pd

def code_mapping(df, src, targ):
    """ Map labels in src and targ columns to integers """
    # Get the distinct labels using a set to remove duplicates
    labels = sorted(list(set(list(df[src]) + list(df[targ]))))
    codes = range(len(labels))
    lc_map = dict(zip(labels, codes))

    # Substitute codes for labels in the dataframe
    df = df.replace({src: lc_map, targ: lc_map})
    return df, labels

def aggregate(df, src, target, threshold):
    """
    Given a dataframe and a source and target, group the source and target and
    drop and source target groups with a count below the threshold to reduce the dataframe
    Return the dataframe
    df: Dataframe
    src: Source
    target: Target
    threshold: Threshold
    """
    # Groups together the source and target for sankey and gives the size for the width of nodes
    df = df.groupby([src, target]).size().reset_index(name='Count')

    # Filters the data and removes any rows where the count is below a threshold
    df = df.query(f'Count >= {threshold}')

    return df

def make_sankey(df, cols, threshold=0, **kwargs):
    """
    Given a dataframe, a list of columns in the dataframe, iterate through pairs of columns
    finding the aggregate count of pairs. The provided threshold will cut any source target
    combination from the dataframe with a count below the threshold. Stack the column pairs
    in a new dataframe until all columns have been iterated through. With the stacked
    dataframe create a sankey if there are more than 2 columns the sankey will be multi-layered.

    df: Dataframe
    cols: List of columns
    threshold: Threshold set at 0 if no threshold provided
    """
    # Create an empty dataframe so data can be appended in the loop
    stacked_df = pd.DataFrame()

    # Loop through source/target pairs of columns
    for i in range(len(cols) - 1):
        src = cols[i]
        targ = cols[i + 1]

        # Aggregate the data between source and target and rename the columns
        aggregated_df = aggregate(df, src, targ, threshold)
        aggregated_df = aggregated_df.rename(columns={src: 'src', targ: 'targ'})

        # Append new columns to the dataframe
        stacked_df = pd.concat([stacked_df, aggregated_df])

    # Create the sankey diagram
    stacked_df, labels = code_mapping(stacked_df, 'src', 'targ')

    link = {'source': stacked_df['src'], 'target': stacked_df['targ'], 'value': stacked_df['Count']}

    thickness = kwargs.get("thickness", 50)  # 50 is the presumed default value
    pad = kwargs.get("pad", 50)

    node = {'label': labels, 'thickness': thickness, 'pad': pad}

    fig = go.Figure(go.Sankey(link=link, node=node))
    return fig