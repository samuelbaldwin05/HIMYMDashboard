"""
File: sankey.py
Author: Michael Maaseide and Jack Carroll

Description: A wrapper library for plotly sankey visualizations

"""
import pandas as pd
import plotly.graph_objects as go


def _code_mapping(df, src, targ):
    """ Map labels in src and targ colums to integers """

    # Get the distinct labels
    labels = list(set(list(df[src]) + list(df[targ])))
    labels_nums = [element for element in labels if type(element) == int or type(element) == float]
    labels_str = [element for element in labels if type(element) == str]
    labels_nums = sorted(labels_nums)
    labels_str = sorted(labels_str)
    labels = labels_str + labels_nums

    # Create a label->code mapping
    codes = range(len(labels))
    lc_map = dict(zip(labels, codes))

    # Substitute codes for labels in the dataframe
    df = df.replace({src: lc_map, targ: lc_map})

    return df, labels

def agg_filter(df, arg1, arg2, vals, filter=0):
    '''Aggregates the data, counting number of artists grouped by provided columns,
     and filters incorrect decade values'''
    agg = df.groupby([arg1, arg2])[vals].sum().reset_index()
    df_ready = agg[agg[vals] > filter]
    return df_ready

def df_stack(df, stack_col, df1_col, df2_col):
    """
    Takes two dataframes with two columns and common pararmeters and stacks them
    """
    df1 = df[[stack_col, df1_col]]
    df2 = df[[stack_col, df2_col]]
    df1.columns = ["src", "targ"]
    df2.columns = ["targ", "src"]
    return pd.concat([df1, df2], axis=0)

def make_sankey(df, src, targ, *cols, vals=None, **kwargs):
    """
    Create a sankey figure
    df - Dataframe
    src - Source node column
    targ - Target node column
    vals - Link values (thickness)
    """
    # Check if there are more than two columns given
    if cols:
        # If so stack the dataframe
        first = True
        for col in cols:
            if first:
                final_df = df_stack(df, col, src, targ)
                final_df[vals] = df[vals]
                first = False
            else:
                temp = df_stack(df, col, src, targ)
                pd.concat([temp, final_df], axis = 0)
    else:
        # If not isolate
        final_df = df
        unneeded_cols = [col for col in df.columns if (col != src) and (col != targ) and (col != vals)]
        final_df = final_df.drop(unneeded_cols, axis = 1)
        final_df.columns = ["src", "targ", "Count"]


    # Get filter keyword and aggregate with that filter based on given value keyword
    filter = kwargs.get("filter", 1)
    final_df = agg_filter(final_df, "src", "targ", vals, filter)
    # Check if values param is given and assign values accordingly
    if vals:
        values = final_df[vals]
    else:
        values = [1] * len(final_df)

    # Code map and create plot
    final_df, labels = _code_mapping(final_df, "src", "targ")
    link = {'source': final_df["src"], 'target': final_df["targ"], 'value': values}

    thickness = kwargs.get("thickness", 50) # 50 is the presumed default value
    pad = kwargs.get("pad", 50)

    node = {'label': labels, 'thickness': thickness, 'pad': pad}

    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.show()