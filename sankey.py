import plotly.graph_objects as go


def _code_mapping(df, src, targ):
    """ Map labels in src and targ columns to integers"""

    # Extract distinct labels
    labels = sorted(list(set(list(df[src])))) + sorted(list(set(list(df[targ]))))

    # Define integer codes
    codes = list(range(len(labels)))

    # Pair labels with codes
    pairs = dict(zip(labels, codes))

    # in df, substitute codes for labels
    df = df.replace({src:pairs, targ:pairs})

    return df, labels


def make_sankey(df, src, targ, vals=None, **kwargs):
    """ Creates a sankey diagram from the dataframe using the src, targ and values columns"""

    # creating the df and labels to use in the sankey diagram
    df, labels = _code_mapping(df, src, targ)

    # using the values parameter (vals) if provided, otherwise defaulting to 1
    if vals:
        values = df[vals]
    else:
        values = [1] * len(df)

    # applying the provided sankey arguments if given from kwargs (pad, thickness, line_color, line_width)
    pad = kwargs.get('pad', 50)
    thickness = kwargs.get('thickness', 30)
    line_color = kwargs.get('line_color', 'black')
    line_width = kwargs.get('line_width', 1)

    # creating the (link, node) variables to use in the plotly sankey parameters
    link = {'source': df[src], 'target': df[targ], 'value': values}
    node = {'label': labels, 'pad': pad, 'thickness': thickness,
            'line': {'color': line_color, 'width': line_width}}

    # creating and showing the final sankey diagram
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.show()