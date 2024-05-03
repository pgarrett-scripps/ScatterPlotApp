import pandas as pd
import streamlit as st
import plotly.express as px

file_separator = {
    'comma': ',',
    'tab': '\t'
}

MAX_DISCRETE_ELEMENTS = 10
FACET_LIMIT = 3

with st.sidebar:
    files = st.file_uploader("Upload Tabular files", accept_multiple_files=True)

    if not files:
        st.stop()

    c1, c2 = st.columns([7, 3])
    choose_file = c1.selectbox("Choose a file", files, format_func=lambda x: x.name)
    separator = c2.selectbox("Choose separator", list(file_separator.keys()), index=0)

    df = pd.read_csv(choose_file, sep=file_separator[separator])

    columns = list(df.columns[1:])

    if len(columns) == 0:
        st.warning("No Columns found in the file")
        st.warning("Please upload a valid file, or choose a different separator")
        st.stop()

    # Identify discrete columns (typically 'object' type in pandas corresponds to categorical data)
    # Here, 'bool' type columns are also considered discrete because they represent binary categories
    discrete_columns = [col for col in columns if df[col].dtype == 'object' or df[col].dtype == 'bool']
    valid_discrete_columns = [col for col in discrete_columns if df[col].nunique() <= MAX_DISCRETE_ELEMENTS]
    valid_facet_columns = [col for col in valid_discrete_columns if df[col].nunique() <= FACET_LIMIT]

    # Identify continuous columns (numeric types)
    # Filtering only numeric types such as 'int' and 'float'
    continuous_columns = [col for col in columns if df[col].dtype in ['int64', 'float64', 'int32', 'float32']]

    # either 2 or 3 dimensions
    dimensions = st.radio("Choose dimensions", [2, 3], horizontal=True)

    x_axis = st.selectbox("Choose x-axis", [None] + continuous_columns)
    y_axis = st.selectbox("Choose y-axis", [None] + continuous_columns)
    z_axis = None
    if dimensions == 3:
        z_axis = st.selectbox("Choose z-axis", [None] + continuous_columns)

    if x_axis is None or y_axis is None or (dimensions == 3 and z_axis is None):
        st.warning("Please select x, y, and z axis")
        st.stop()

    with st.expander('Color, Size, Symbol, Facet'):
        c1, c2 = st.columns([7, 3])
        color_axis = c1.selectbox("Choose color axis", [None] + valid_discrete_columns)
        default_color = c2.selectbox("Choose default color", ['blue', 'red', 'green'], disabled=color_axis is not None)

        c1, c2 = st.columns([7, 3])
        size_axis = c1.selectbox("Choose size-axis", [None] + continuous_columns)
        max_size = c2.number_input("Max Size", value=5)
        if size_axis is None:
            df['dummy_size_axis'] = max_size
            size_axis = 'dummy_size_axis'

        symbol_axis = st.selectbox("Choose symbol axis", [None] + valid_discrete_columns)

        facet_col_axis = None
        facet_row_axis = None
        if dimensions == 2:
            facet_col_axis = st.selectbox("Choose facet axis", [None] + valid_facet_columns)
            facet_row_axis = st.selectbox("Choose facet row", [None] + valid_facet_columns)

    with st.expander('Title and Axes'):
        title = st.text_input("Title", f"Scatter Plot for {choose_file.name}")

        c1, c2 = st.columns([7, 3])
        x_label = c1.text_input("X-axis Label", x_axis)
        x_log_scale = c2.checkbox("X-axis Log Scale", value=False)
        min_x = df[x_axis].min()
        max_x = df[x_axis].max()
        c1, c2 = st.columns(2)
        x_range_min = c1.number_input("X-axis Range Min", value=min_x, min_value=min_x, max_value=max_x)
        x_range_max = c2.number_input("X-axis Range Max", value=max_x, min_value=min_x, max_value=max_x)

        c1, c2 = st.columns([7, 3])
        y_label = c1.text_input("Y-axis Label", y_axis)
        y_log_scale = c2.checkbox("Y-axis Log Scale", value=False)
        min_y = df[y_axis].min()
        max_y = df[y_axis].max()
        c1, c2 = st.columns(2)
        y_range_min = c1.number_input("Y-axis Range Min", value=min_y, min_value=min_y, max_value=max_y)
        y_range_max = c2.number_input("Y-axis Range Max", value=max_y, min_value=min_y, max_value=max_y)

        if dimensions == 3:
            c1, c2 = st.columns([7, 3])
            z_label = c1.text_input("Z-axis Label", z_axis)
            z_log_scale = c2.checkbox("Z-axis Log Scale", value=False)
            min_z = df[z_axis].min()
            max_z = df[z_axis].max()
            c1, c2 = st.columns(2)
            z_range_min = c1.number_input("Z-axis Range Min", value=min_z, min_value=min_z, max_value=max_z)
            z_range_max = c2.number_input("Z-axis Range Max", value=max_z, min_value=min_z, max_value=max_z)

    with st.expander('Hover Data'):
        default_columns = []
        if color_axis is not None:
            default_columns.append(color_axis)
        if size_axis is not None and size_axis != 'dummy_size_axis':
            default_columns.append(size_axis)
        if x_axis is not None:
            default_columns.append(x_axis)
        if y_axis is not None:
            default_columns.append(y_axis)
        if z_axis is not None:
            default_columns.append(z_axis)
        if symbol_axis is not None:
            default_columns.append(symbol_axis)
        if facet_col_axis is not None:
            default_columns.append(facet_col_axis)
        if facet_row_axis is not None:
            default_columns.append(facet_row_axis)
        hover_data = st.multiselect("Hover Data", columns, default=default_columns)

# scatter plot
if dimensions == 3:

    if x_axis is None or y_axis is None or z_axis is None:
        st.warning("Please select x, y, and z axis")
        st.stop()

    fig = px.scatter_3d(df,
                        x=x_axis,
                        range_x=(x_range_min, x_range_max),
                        y=y_axis,
                        range_y=(y_range_min, y_range_max),
                        z=z_axis,
                        range_z=(z_range_min, z_range_max),
                        color=color_axis,
                        size=size_axis,
                        size_max=max_size,
                        symbol=symbol_axis,
                        log_x=x_log_scale,
                        log_y=y_log_scale,
                        log_z=z_log_scale,
                        labels={x_axis: x_label, y_axis: y_label, z_axis: z_label},
                        hover_data=hover_data)

    # update title and axis labels
    fig.update_layout(title=title)
else:

    if x_axis is None or y_axis is None:
        st.warning("Please select x and y axis")
        st.stop()

    fig = px.scatter(df,
                     x=x_axis,
                     range_x=(x_range_min, x_range_max),
                     y=y_axis,
                        range_y=(y_range_min, y_range_max),
                     color=color_axis,
                     symbol=symbol_axis,
                     size=size_axis,
                     size_max=max_size,
                     facet_col=facet_col_axis,
                     facet_row=facet_row_axis,
                     log_x=x_log_scale,
                     log_y=y_log_scale,
                        labels={x_axis: x_label, y_axis: y_label, title: title},
                     hover_data=hover_data)

    # update title and axis labels
    fig.update_layout(title=title)

trace_color = default_color if color_axis is None else None
# make fig larger
fig.update_layout(
    autosize=False,
    width=700,
    height=700,
).update_traces(marker=dict(line=dict(width=1, color=trace_color), color=trace_color))

st.plotly_chart(fig, use_container_width=True)
