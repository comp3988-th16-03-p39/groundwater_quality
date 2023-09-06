import math
from typing import Callable, Any
import itertools as itt


import pandas as pd
import numpy as np


# : `cleaning_utils.py` contains very general functions that can be applied to a wide range of datasets.


def pivot_dataset(
        df: pd.DataFrame,
        sample_id_columns: list[str],
        per_sample_data: list[str],
        chemical_name_column: str,
        values_per_chemical: list[str],
        desired_chemical_names: list[str],
        *,
        drop_duplicates: bool = False
) -> pd.DataFrame:
    """
    Takes a dataset where each row is a single chemical measurement 
    from a sample and returns dataset with each desired_chemical as its own column
    and each sample is stored (and completely contained) within its own row.

    Paramters
    ---------- 
    `df` : the dataframe containing the dataset

    `sample_id_columns` : The list of coloumns which
        can be used to uniquely identify the sample.
        eg ["SampleID"] or ["SampleTime","SampleLocation"]

    `per_sample_data` : The list of columns which contain
        data which is unique to each sample, not including the sample_id_columns. 
        eg ["Time", "Location"] but not ["SampleID"]

    `chemical_name_column` : The column which contains the name of the 
        chemical measured (in that row). 

    `values_per_chemical` : The list of coulumns which contain data 
        which is unique to each chemical measurement within a sample.
        eg ["Amount", "Unit Of Measurement"]

    `desired_chemical_names` : The list of chemical names 
        (in the chemical_name_column) which should be kept. Other names will be dropped.

    `drop_duplicates` : Deteremines what to do if the dataset has any rows with
        two or more measurments of the same chemical within the same sample.
        - False (default): The multiple values are aggregated into a list,
            however this has the side effect of wrapping all values in lists.
        - True : All duplicate rows are dropped.

    Returns 
    ---------
    Returns a dataset with the following sets of columns: `sample_id_columns` 
    and `per_sample_data` columns. Then for each desired chemical name there 
    will be a pandas multiindex column for each chemical containing the 
    `values_per_chemical` columns.
    """

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
    chem_names: list[str],
    transform: Callable[[Any], tuple[Any]],
    input_row_names: list[str],
    output_row_names: list[str],
    *,
    split_lists: bool = False,
) -> None:
    """
    Helper function which can be used to easily transform mutliple columns of the 
    dataset and create new columns for the given chemical name.

    Parameters 
    ----------
    `df` : The dataset as output by the `pivot_dataset` function with multiindex columns 
        for each chemical then subcolumns for `values_per_chemical`. 

    `chem_names` : The list of chemicals that the transformation of 
        their subcolumns should be performed on. (used as multiindex prefixes)

    `transform` : The function which takes in the arguments of the values of  
        `input_row_names` in the row, and outputs the tuple of arguments 
        meant to be stored in the `output_row_names` for the column.

    `input_row_names` : The names of the columns to be passed as arguments
        to the `transform` function

    `output_row_names` : The names of the columns that each value in the 
        tuple output by the `transform` function should be assigned to.

    `split_lists` : The `pivot_dataset` can return a dataframe with lists 
        as the values. In many cases the `transform` function should 
        be applied to each index of the lists in the row indepenedently. 
        - True: If the split_lists` option is set to true, then if there is a 
            row where the values are lists, it will pass each index of the lists
            to the transform function elementwise and store the output in new lists.
        - False (default): If a list is in a row it will be passed directly to the 
            transform function. Keep this option to false if `transform` is 
            meant ot aggregrate the multiple values in the lists.
    """
    for chem_name in chem_names:

        input_row_multiindex = [(chem_name, i) for i in input_row_names]
        output_row_multiindex = [(chem_name, i) for i in output_row_names]

        if split_lists:
            assert len(input_row_names) > 0

            def wrapped_transform(*args):

                if type(args[0]) == list:
                    if len(args[0]) == 1:
                        res = [transform(*[i[0] for i in args])]
                        res = tuple(list(row) for row in zip(*res))
                        return res
                    else:
                        list_rows = [transform(*[args[i][n] for i in range(len(args))])
                                     for n in range(len(args[0]))]
                        list_cols = tuple(list(row) for row in zip(*list_rows))
                        return list_cols
                else:
                    res = transform(*[i for i in args])
                    return res
        else:
            def wrapped_transform(*args):
                row = args
                # return transform(*[row[i] for i in input_row_multiindex])
                return transform(*args)

        res = np.vectorize(wrapped_transform, otypes=["object"])(
            *[df[i] for i in input_row_multiindex])
        res = list(zip(*[res[i] for i in range(len(res))]))
        for idx, output_row in enumerate(output_row_multiindex):
            df[output_row] = res[idx]


def create_standardise_units_func(units_dict: dict[str, Callable]
                                  ) -> Callable[[tuple[float, str]], tuple[float]]:
    """
    Takes a dictionary of unit names to functions and 
    returns a function.
    This function takes a value and a unit of measurement (string) 
    and returns a tuple containing the result of applying the 
    corresponding function in the `units_dict` to the value.
    (Compatible with `transform_chemical_data`)
    """
    def standardise_units_func(value, uom):
        if isinstance(uom, float):
            if math.isnan(uom):
                return (np.nan, np.nan, np.nan, np.nan)
        if not (uom in units_dict.keys()):
            raise ValueError('Invalid units', uom)
        value = units_dict[uom](value)
        return (value,)
    return standardise_units_func


def drop_chemical_columns(df: pd.DataFrame,
                          chemical_names: list[str],
                          drop_col_names: list[str]) -> None:
    """
    Will drop the `drop_col_names` from all chemicals in `chemical_names`.
    """
    drop_multiindicies = list(itt.product(
        chemical_names, drop_col_names))
    df.drop(drop_multiindicies, axis=1, inplace=True)


def order_cols(df: pd.DataFrame,
               chemical_names: list[str]
               ) -> None:
    """
    Will return a new dataframe with ordered columns
    """
    # move chemical columns to left
    other_params = set(df.columns.levels[0])
    chemical_names.sort()
    other_params = list(other_params.difference(set(chemical_names)))
    ordered_params = other_params
    ordered_params.extend(chemical_names)
    new_cols = df.columns.reindex(ordered_params, level=0)
    df = df.reindex(columns=new_cols[0])
    return df
