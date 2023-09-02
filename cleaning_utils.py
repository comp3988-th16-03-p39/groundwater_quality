import pandas as pd
from typing import Callable, Any


def pivot_dataset(
        df: pd.DataFrame,
        sample_id_columns: list[str],
        per_sample_data: list[str],
        chemical_name_column: str,
        values_per_chemical: list[str],
        desired_chemical_names: list[str],
        *,
        drop_duplicates: bool = False
):

    df = df[df[chemical_name_column].isin(
        desired_chemical_names)]

    if drop_duplicates:
        df = df.drop_duplicates(
            subset=[*sample_id_columns, chemical_name_column])

        df_pivoted = df.pivot(
            index=[*sample_id_columns, *per_sample_data],
            columns=[chemical_name_column],
            values=values_per_chemical
        )

    else:
        df_pivoted = df.pivot_table(
            index=[*sample_id_columns, *per_sample_data],
            columns=[chemical_name_column],
            values=values_per_chemical,
            aggfunc=list
        )

    df_pivoted.columns = df_pivoted.columns.reorder_levels(order=[
        chemical_name_column, None])
    df_pivoted = df_pivoted.sort_index(axis=1, level=0)
    df_pivoted = df_pivoted.reset_index()  # ? May not be needed
    # Removes unnecessary data in the coulmns multiindex
    df_pivoted.columns.names = [None, None]
    return df_pivoted


def transform_chemical_data(
    df: pd.DataFrame,
    chem_name: str,
    transform: Callable[[tuple[Any]], tuple[Any]],
    input_row_names: list[str],
    output_row_names: list[str],
    *,
    split_lists: bool = False,
):
    input_row_multiindex = [(chem_name, i) for i in input_row_names]
    output_row_multiindex = [(chem_name, i) for i in output_row_names]

    if split_lists:
        assert len(input_row_names) > 0

        def wrapped_transform(row):
            if type(row[chem_name, input_row_names[0]]) == list:
                list_rows = [transform(*[row[i][n] for i in input_row_multiindex])
                             for n in range(len(row[chem_name, input_row_names[0]]))]
                list_cols = [list(row) for row in zip(*list_rows)]
                return list_cols
                # if (len(row[chem_name, input_row_names[0]]) > 0):
                # else:
                #     raise ValueError(
                #         "Number of elements in a cell must be larger than 0.")
            else:
                return transform(*[row[i] for i in input_row_multiindex])
        # if len(input_row_names) > 0:
        # else:
        #     raise ValueError(
        #         "There must be atleast one input column to use `split_lists` option.")

    else:
        def wrapped_transform(row):
            return transform(*[row[i] for i in input_row_multiindex])

    df[output_row_multiindex] = df[input_row_multiindex].apply(
        wrapped_transform, axis=1, result_type="expand"
    )


# : Old version of transform_chemical_data
# had redundant checks (as corresponding errors were never called)

# def transform_chemical_data(
#     df: pd.DataFrame,
#     chem_name: str,
#     transform: Callable[[tuple[Any]], tuple[Any]],
#     input_row_names: list[str],
#     output_row_names: list[str],
#     *,
#     split_lists: bool = False,
# ):
#     input_row_multiindex = [(chem_name, i) for i in input_row_names]
#     output_row_multiindex = [(chem_name, i) for i in output_row_names]

#     if split_lists:
#         def wrapped_transform(row):
#             if len(input_row_names) > 0:
#                 if type(row[chem_name, input_row_names[0]]) == list:
#                     if (len(row[chem_name, input_row_names[0]]) > 0):
#                         list_rows = [transform(*[row[i][n] for i in input_row_multiindex])
#                                      for n in range(len(row[chem_name, input_row_names[0]]))]
#                         list_cols = [list(row) for row in zip(*list_rows)]
#                         return list_cols
#                     else:
#                         raise ValueError(
#                             "Number of elements in a cell must be larger than 0.")
#                 else:
#                     return transform(*[row[i] for i in input_row_multiindex])
#             else:
#                 raise ValueError(
#                     "There must be atleast one input column to use `split_lists` option.")

#     else:
#         def wrapped_transform(row):
#             return transform(*[row[i] for i in input_row_multiindex])

#     df[output_row_multiindex] = df[input_row_multiindex].apply(
#         wrapped_transform, axis=1, result_type="expand"
#     )
