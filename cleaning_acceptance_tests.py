import data_cleaning as dc
from cleaning_utils import pivot_dataset, transform_chemical_data
import pandas as pd
import itertools as itt

convert_to_standard = dict()

# mass/volume concentration g/L
convert_to_standard['g/l'] = lambda x: x
convert_to_standard['mg/l'] = lambda x: x/1e3
convert_to_standard['ug/l'] = lambda x: x/1e6
convert_to_standard['µg/l'] = lambda x: x/1e6
convert_to_standard['ng/l'] = lambda x: x/1e9

# pH
convert_to_standard['ph'] = lambda x: x

# temperature °c
convert_to_standard['°c'] = lambda x: x
convert_to_standard['°f'] = lambda x: 5*(x-32)/9

# conductivity us/cm
convert_to_standard['us/cm'] = lambda x: x
convert_to_standard['µs/cm'] = lambda x: x

def test_dataset (
    test_path: str,
    sample_id_columns: list[str],
    desired_chemical_names: list[str],
    chemical_name_column: str, 
    per_sample_data: list[str],
    na_threshold: int, 
    convert_to_standard: dict
):

    df = pd.read_csv(test_path+"_in.csv")

    df = pivot_dataset (
        df,
        sample_id_columns=[sample_id_columns],
        per_sample_data=[per_sample_data],
        chemical_name_column=chemical_name_column,
        values_per_chemical=["Amount", "UOM", "MinDetectLimit"],
        desired_chemical_names=desired_chemical_names,
    )

    dc.clean_dataset_units (df, desired_chemical_names)
    dc.format_dataset_amount (df, desired_chemical_names)
    dc.standardise_dataset_unit (df, desired_chemical_names, convert_to_standard)
    dc.drop_units_min_detect(df, desired_chemical_names)
    dc.agg_dataset_measurement (df, desired_chemical_names)
    df = dc.filter_rows_by_nas (df, desired_chemical_names, na_threshold)
    (amount_avgs, missing_chemicals) = dc.get_chemical_averages (df, desired_chemical_names)
    dc.fill_dataset_nans (df, desired_chemical_names, amount_avgs, missing_chemicals)
    df = dc.sort_columns(df, desired_chemical_names)

    df.to_csv(test_path+"_gen.csv", index=False, encoding="utf-8")

def small_complete ():
    # Data is complete. No missing values. No inequalities.
    # Units are inconsistent.

    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_complete"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_incomplete_1 ():
    # Data is incomplete. No inequalities.
    # Units are inconsistent.
    # Threshold should remove no samples

    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_incomplete_1"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_incomplete_2 ():
    # Data is incomplete. No inequalities.
    # Units are inconsistent.
    # Threshold should remove some samples.
    # The rest of the missing values should be filled with averages.

    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_incomplete_2"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = 1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_incomplete_3 ():
    # Data is incomplete. No inequalities.
    # Units are inconsistent.
    # Threshold should remove all samples.
    # All missing values should be filled with averages.

    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_incomplete_3"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = 1000

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )
    
def small_inequalities ():
    # Data is complete. Inequalities in amounts.
    # Units are inconsistent.
    # Only one value per chemical+sample
    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_inequalities"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_non_numeric ():
    # Data is complete. BDL and ND values present.
    # Inequalities present.
    # Units are inconsistent.
    # Only one value per chemical+sample
    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_non_numeric"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_list ():
    # Data is complete. No inequalities.
    # Units are inconsistent.
    # Multiple values per chemical+sample
    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_list"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_list_inequalities ():
    # Data is complete. Inequalities.
    # Some samples are all <.
    # Some samples are mixture.
    # Multiple values per chemical+sample
    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_list_inequalities"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )

def small_complex ():
    # Data incomplete. Inequalities.
    # NaN values
    # BDL and ND values present.
    # Units are inconsistent.
    # Multiple values per chemical+sample.
    # Threshold will remove some samples.
    # Average will fill remaining NaNs.
    desired_chemical_names = ["Calcium", "Chloride", "Water Temperature"]
    test_path = "Tests/small_complex"
    sample_id_columns = "SampleID"
    chemical_name_column = "ChemicalName"
    per_sample_data = "DateCollected"
    na_threshold = -1

    test_dataset (
        test_path,
        sample_id_columns,
        desired_chemical_names,
        chemical_name_column, 
        per_sample_data,
        na_threshold, 
        convert_to_standard
    )


    

small_complete ()
small_incomplete_1 ()
small_incomplete_2 ()
small_incomplete_3 ()
small_inequalities ()
small_non_numeric ()
small_list ()
small_list_inequalities ()
small_complex ()