import pandas as pd
import itertools as itt
import numbers as nb
import numpy as np
import re
import math
import statistics as st
import copy

from cleaning_utils import pivot_dataset, transform_chemical_data

# These functions should be performed in the given order

# Clean units formatting
def clean_units(units):

    if isinstance(units, list):
        return ["".join(unit.strip().lower().split()) if isinstance(unit, str) else unit for unit in units]
    elif isinstance(units, str):
        return "".join(units.strip().lower().split())
    else:
        return np.nan

def clean_dataset_units (df, desired_chemical_names):

    units_index = list(itt.product(desired_chemical_names, ["UOM"]))
    df[units_index] = df[units_index].applymap(clean_units)


# This function should format a single amount value and output a float-prefix tuple.
def format_amount(erase_invalid: bool = False):

    def format_amount_func(amount, min_detection_limit, uom):

        # if amount is already number
        if isinstance(amount, nb.Number):
            return ('=', float(amount), uom)

        if isinstance(amount, str):
            # remove whitespace
            amount = ''.join(amount.split())
            amount_prefix = None

            # if amount matches prefix-numerical form
            if re.fullmatch(r'([<>=]?)[0-9]*(\.?)[0-9]+', amount):
                if re.match(r'[<>=]', amount):
                    amount_prefix = re.split(r'[<>=]', amount)
                    amount_prefix[1] = float(amount_prefix[1])
                    if "<" in amount:
                        amount_prefix = ("<", amount_prefix[1], uom)
                    else:
                        amount_prefix = ("=", amount_prefix[1], uom)
                else:
                    amount_prefix = ("=", float(amount), uom)
                return amount_prefix

            # if amount is below detection limit
            elif amount == "BDL" or amount == "ND":
                if min_detection_limit is not None:
                    return ("<", min_detection_limit, uom)
                else:
                    return ("=", 0, uom)

        # otherwise amount is invalid
        if erase_invalid:
            return (np.nan, np.nan, np.nan)
        else:
            raise ValueError("Invalid Formatting - " + str(amount))

    return format_amount_func

def format_dataset_amount (df, desired_chemical_names):

    # apply formatting to every chemical and sort columns
    for chemical_name in desired_chemical_names:
        transform_chemical_data(df, chemical_name, format_amount(True),
            ["Amount", "MinDetectLimit", "UOM"], ["Prefix", "Amount", "UOM"], split_lists=True)
    df = df.sort_index(axis=1)


# standardise units

def standardise_units(units_dict, erase_invalid = False):

    def standardise_units_func(amount, min_detection_limit, prefix, uom):

        if isinstance(uom, float):
            if math.isnan(uom):
                return (np.nan, np.nan, np.nan, np.nan)
        if not (uom in units_dict.keys()):
            if not erase_invalid:
                raise ValueError('Invalid units', uom)
            else:
                return (np.nan,np.nan,np.nan,np.nan)
        amount = units_dict[uom](amount)
        min_detection_limit = units_dict[uom](min_detection_limit)
        return (amount, min_detection_limit, prefix, uom)
    return standardise_units_func

def standardise_dataset_unit (df, desired_chemical_names, convert_to_standard, erase_invalid = False):

    for chemical_name in desired_chemical_names:
        transform_chemical_data(df, chemical_name, standardise_units(convert_to_standard, erase_invalid),
                                ["Amount", "MinDetectLimit", "Prefix", "UOM"], ["Amount", "MinDetectLimit", "Prefix", "UOM"], split_lists=True)
        df.sort_index(axis=1, inplace=True)

# drop units and MinDetectLimit columns

def drop_units_min_detect (df, desired_chemical_names):
    df.drop(["UOM", "MinDetectLimit"], level=1, axis=1, inplace=True)

# sort columns
def sort_columns (df, desired_chemical_names):
    other_params = set(df.columns.levels[0])
    desired_chemical_names.sort()
    other_params = list(other_params.difference(set(desired_chemical_names)))
    ordered_params = other_params
    ordered_params.extend(desired_chemical_names)
    new_cols = df.columns.reindex(ordered_params, level=0)
    return df.reindex(columns=new_cols[0])

# turn list of measurements into one aggregated measurement

def agg_measurement(amount, prefix):

    if not isinstance(amount, list):
        if math.isnan(amount):
            return (np.nan, np.nan)
        elif isinstance(amount, nb.Number):
            if isinstance(prefix, list):
                raise TypeError(prefix)
            return (amount, prefix)
        else:
            raise TypeError(amount)

    if set(prefix) == set(["<"]):
        return (min(amount), "<")
    else:
        return (st.mean(amount), "=")


def agg_dataset_measurement (df, desired_chemical_names):

    for chemical_name in desired_chemical_names:
        transform_chemical_data(df, chemical_name, agg_measurement,
            ["Amount", "Prefix"], ["Amount", "Prefix"])

# count NaNs in a row
def count_nas(row):
    return row.isna().sum()

# remove rows with more NaNs than a threshold
def filter_rows_by_nas (df, desired_chemical_names, na_threshold):

    df = df.reindex(sorted(df.columns), axis=1)
    amounts_index = list(itt.product(desired_chemical_names, ["Amount"]))
    mask = df[amounts_index].apply(count_nas, axis=1)
    mask = mask[mask <= na_threshold].index

    df = df.loc[mask]
    df.reset_index(inplace=True)
    df.drop(['index'], axis=1, inplace=True)
    return df


# calculate averages for each chemical
# also reports NaN averages

def get_chemical_averages (df, desired_chemical_names):

    amount_avgs = dict()
    missing_chemicals = []

    for chemical_name in desired_chemical_names:
        amount_avgs[chemical_name] = df[chemical_name,"Amount"].mean()
        if math.isnan(amount_avgs[chemical_name]):
            missing_chemicals.append(chemical_name)
    
    return (amount_avgs, missing_chemicals)


# fill NaNs with chemical averages. Remove chemicals with no values.

def fill_dataset_nans (df, desired_chemical_names, amount_avgs, missing_chemicals):

    # remove chemicals with all NaNs
    desired_chemical_names = list(
        set(desired_chemical_names).difference(set(missing_chemicals)))
    df.drop(missing_chemicals, axis=1, inplace=True)

    # fill NaN values with averages
    for chemical_name in desired_chemical_names:
        transform_chemical_data(df, chemical_name, lambda a, p: (amount_avgs[chemical_name], '=') if math.isnan(a) else (a, p),
                                ["Amount", "Prefix"], ["Amount", "Prefix"])


