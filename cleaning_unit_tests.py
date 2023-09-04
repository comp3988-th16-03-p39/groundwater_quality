import unittest
import pandas as pd
import numpy as np
import math
from cleaning_utils import pivot_dataset, transform_chemical_data
import data_cleaning as dc

class TestUtilMethods (unittest.TestCase):
    def test_pivot1(self):
        # data is complete
        data = list()

        data.append([1, 12, "A", 1, "mg/L"])
        data.append([1, 12, "B", '<2', "g/L"])
        data.append([2, 8, "A", '12', "mg/L"])
        data.append([2, 8, "B", '<0.01', "g/L"])

        df = pd.DataFrame(data, columns=["ID", "X", "Name", "Y", "Z"])

        df = pivot_dataset (
            df,
            sample_id_columns=["ID"],
            per_sample_data=["X"],
            chemical_name_column="Name",
            values_per_chemical=["Y","Z"],
            desired_chemical_names=["A","B"],
        )

        #check dimensions
        self.assertTrue ((df.columns.levels[0] == ['A','B','X','ID']).any())
        self.assertTrue ((df.columns.levels[1] == ['Y','Z','']).any())
        self.assertEqual (list(df.index),list(range(0,2)))
        
        #check contents
        self.assertEqual (list(df["ID"]),[1,2])
        self.assertEqual (list(df["X"]),[12,8])
        self.assertEqual (list(df["A","Y"])[0],[1])
        self.assertEqual (list(df["A","Y"])[1],['12'])
    
    def test_pivot2(self):
        # data is incomplete
        data = list()

        data.append([1, 12, "A", 1, "mg/L"])
        data.append([1, 12, "B", '<2', "g/L"])
        data.append([2, 8, "A", '12', "mg/L"])

        df = pd.DataFrame(data, columns=["ID", "X", "Name", "Y", "Z"])

        df = pivot_dataset (
            df,
            sample_id_columns=["ID"],
            per_sample_data=["X"],
            chemical_name_column="Name",
            values_per_chemical=["Y","Z"],
            desired_chemical_names=["A","B"],
        )

        #check dimensions
        self.assertTrue ((df.columns.levels[0] == ['A','B','X','ID']).any())
        self.assertTrue ((df.columns.levels[1] == ['Y','Z','']).any())
        self.assertEqual (list(df.index),list(range(0,2)))
        
        #check contents
        self.assertEqual (list(df["B","Y"])[0],['<2'])
        self.assertTrue (math.isnan(list(df["B","Y"])[1]))
    
    def test_pivot3(self):
        # data is excessive
        data = list()

        data.append([1, 12, "A", 1, "mg/L"])
        data.append([1, 12, "B", '<2', "g/L"])
        data.append([2, 8, "A", '12', "mg/L"])
        data.append([2, 8, "B", '<0.01', "g/L"])
        data.append([2, 8, "B", '<0.02', "g/L"])

        df = pd.DataFrame(data, columns=["ID", "X", "Name", "Y", "Z"])

        df = pivot_dataset (
            df,
            sample_id_columns=["ID"],
            per_sample_data=["X"],
            chemical_name_column="Name",
            values_per_chemical=["Y","Z"],
            desired_chemical_names=["A","B"],
        )

        #check dimensions
        self.assertTrue ((df.columns.levels[0] == ['A','B','X','ID']).any())
        self.assertTrue ((df.columns.levels[1] == ['Y','Z','']).any())
        self.assertEqual (list(df.index),list(range(0,2)))
        
        #check contents
        self.assertEqual (list(df["ID"]),[1,2])
        self.assertEqual (list(df["X"]),[12,8])
        self.assertEqual (list(df["B","Y"])[0],['<2'])
        self.assertEqual (list(df["B","Y"])[1],['<0.01','<0.02'])
        self.assertEqual (list(df["B","Z"])[1],['g/L','g/L'])
    
    def test_transform_1 (self):
        # transform listwise
        data = list()

        data.append([1, "", [1,2], [2,3], [3,4], [4,5]])
        data.append([2, "", [2,3], [3,4], [4,5], [5,6]])
        data.append([3, "", [4,5], [5,6], [6,7], [7,8]])

        cols = [("ID",""), ("X",""), ("A","Y"), ("A","Z"), ("B","Y"), ("B","Z")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        transform_chemical_data(
            df = df,
            chem_name = "A",
            transform = lambda y,z : (y-z,z,y+z),
            input_row_names = ["Y","Z"],
            output_row_names = ["Y","Z","W"],
            split_lists = True
        )

        #check correct dimensions
        self.assertTrue ((set(df.columns.levels[0]) == set(['A','B','X','ID'])))
        self.assertTrue ((set(df.columns.levels[1]) == set(['Y','Z','W',''])))
        self.assertEqual (list(df.index),list(range(0,3)))

        # check contents of changed chemical
        self.assertEqual (df['A','Y'][0],[-1,-1])
        self.assertEqual (df['A','Z'][0],[2,3])
        self.assertEqual (df['A','W'][0],[3,5])
        self.assertEqual (df['A','Y'][1],[-1,-1])
        self.assertEqual (df['A','Z'][1],[3,4])
        self.assertEqual (df['A','W'][1],[5,7])

        # check other chemical is unchanged
        self.assertEqual (df['B','Y'][0],[3,4])
        self.assertEqual (df['B','Z'][0],[4,5])
        self.assertEqual (df['B','Y'][1],[4,5])
        self.assertEqual (df['B','Z'][1],[5,6])
    
    def test_transform_2 (self):
        # transform listwise
        data = list()

        data.append([1, "", [1,2], [2,3], [3,4], [4,5]])
        data.append([2, "", [2,3], [3,4], [4,5], [5,6]])
        data.append([3, "", [4,5], [5,6], [6,7], [7,8]])

        cols = [("ID",""), ("X",""), ("A","Y"), ("A","Z"), ("B","Y"), ("B","Z")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        transform_chemical_data(
            df = df,
            chem_name = "A",
            transform = lambda y,z : (sum(y)-sum(z),sum(z),sum(y)+sum(z)),
            input_row_names = ["Y","Z"],
            output_row_names = ["Y","Z","W"]
        )

        #check correct dimensions
        self.assertTrue ((set(df.columns.levels[0]) == set(['A','B','X','ID'])))
        self.assertTrue ((set(df.columns.levels[1]) == set(['Y','Z','W',''])))
        self.assertEqual (list(df.index),list(range(0,3)))

        # check contents of changed chemical
        self.assertEqual (list(df['A','Y']),[-2,-2,-2])
        self.assertEqual (list(df['A','Z']),[5,7,11])
        self.assertEqual (list(df['A','W']),[8,12,20])

        # check other chemical is unchanged
        self.assertEqual (df['B','Y'][0],[3,4])
        self.assertEqual (df['B','Z'][0],[4,5])
        self.assertEqual (df['B','Y'][1],[4,5])
        self.assertEqual (df['B','Z'][1],[5,6])
    
    def test_clean_units (self):
        # test removing whitespace and uppercase
        units = [" mg/ L", "° C", "u   G/ L", "   us/cm   "]
        cleaned_units = dc.clean_units(units)
        self.assertEqual (cleaned_units, ["mg/l","°c","ug/l","us/cm"])
    
    def test_clean_units_single (self):
        # test if str instead of list
        units = "  mg / L "
        cleaned_units = dc.clean_units(units)
        self.assertEqual (cleaned_units, "mg/l")
    
    def test_clean_units_invalid (self):
        # test invalid type
        units = set()
        cleaned_units = dc.clean_units(units)
        self.assertTrue (math.isnan(cleaned_units))

    def test_format_amount_number (self):
        # test formatting float amount
        amount = 4.5
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertEqual (formatted_amount, ('=',4.5,"mg/L"))
    
    def test_format_amount_string (self):
        # test formatting string amount
        amount = "4.5"
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertEqual (formatted_amount, ('=',4.5,"mg/L"))

        amount = "<4.5"
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertEqual (formatted_amount, ('<',4.5,"mg/L"))

    def test_format_amount_special (self):
        # test formatting keyword amounts
        amount = "BDL"
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertEqual (formatted_amount, ('<',3,"mg/L"))

        amount = "ND"
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertEqual (formatted_amount, ('<',3,"mg/L"))
    
    def test_format_amount_invalid (self):
        # test formatting invalid string or type inputs
        amount = "brufbje"
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertTrue (math.isnan(formatted_amount[0]))
        self.assertTrue (math.isnan(formatted_amount[1]))
        self.assertTrue (math.isnan(formatted_amount[2]))

        amount = set()
        min_detection_limit = 3
        uom = "mg/L"
        formatted_amount = dc.format_amount(True)(amount, min_detection_limit, uom)
        self.assertTrue (math.isnan(formatted_amount[0]))
        self.assertTrue (math.isnan(formatted_amount[1]))
        self.assertTrue (math.isnan(formatted_amount[2]))
    
    def test_standardise_units (self):
        # test converting amount by units
        convert_to_standard = dict()

        convert_to_standard['°c'] = lambda x: x
        convert_to_standard['°f'] = lambda x: 5*(x-32)/9

        convert_to_standard['us/cm'] = lambda x: x
        convert_to_standard['µs/cm'] = lambda x: x

        st_vals = dc.standardise_units(convert_to_standard)(32, 41, "<", "°f")
        # it does not change units, as units are meant to be dropped shortly after
        self.assertEqual(st_vals,(0,5,"<","°f"))

        st_vals = dc.standardise_units(convert_to_standard)(10, 3, "<", "°c")
        self.assertEqual(st_vals,(10,3,"<","°c"))
    
    def test_standardise_units_invalid (self):
        # test converting amount by NaN units
        convert_to_standard = dict()

        convert_to_standard['°c'] = lambda x: x
        convert_to_standard['°f'] = lambda x: 5*(x-32)/9

        convert_to_standard['us/cm'] = lambda x: x
        convert_to_standard['µs/cm'] = lambda x: x

        st_vals = dc.standardise_units(convert_to_standard)(32, 41, "<", np.nan)

        self.assertTrue(math.isnan(st_vals[0]))
        self.assertTrue(math.isnan(st_vals[1]))
        self.assertTrue(math.isnan(st_vals[2]))
        self.assertTrue(math.isnan(st_vals[3]))

    def test_sort_columns (self):
        # test sorting of chemical names and ordering of sample parameters first.
        data = list()

        data.append([1, 1.01, "<", "", 2.01, '='])
        data.append([2, 0.01, "=", "", 6.76, "<"])
        data.append([3, 0.03, "=", "", 5.44, "<"])

        cols = [("ID",""), ("B","Amount"), ("B","Prefix"), ("X",""), ("A","Amount"), ("A","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        desired_chemical_names = ["A","B"]
        df2 = dc.sort_columns (df, desired_chemical_names)
        
        # check indicies are correctly sorted
        self.assertTrue((df2.columns.levels[0]==['ID','X','A','B']).any())
        self.assertTrue((df2.columns.levels[1]==['','Amount','Prefix']).any())

        # check data is unaffected
        self.assertEqual(list(df["A","Amount"]),[2.01,6.76,5.44])
        self.assertEqual(list(df["A","Prefix"]),['=','<','<'])
        self.assertEqual(list(df["B","Amount"]),[1.01,0.01,0.03])
        self.assertEqual(list(df["B","Prefix"]),['<','=','='])
        self.assertEqual(list(df["X"]),["","",""])
        self.assertEqual(list(df["ID"]),[1,2,3])

    def test_aggregate_measurement (self):
        # test aggregating measurements

        # Case 1 : All equal
        amount = [1,3]
        prefix = ['=', '=']
        (agg_amount,agg_prefix) = dc.agg_measurement(amount, prefix) 
        self.assertEqual (agg_amount,2)
        self.assertEqual (agg_prefix,'=')

        # Case 2 : Mixed equal and less than
        amount = [1,3]
        prefix = ['<', '=']
        (agg_amount,agg_prefix) = dc.agg_measurement(amount, prefix) 
        self.assertEqual (agg_amount,2)
        self.assertEqual (agg_prefix,'=')

        # Case 3 : All less than
        amount = [1,3]
        prefix = ['<', '<']
        (agg_amount,agg_prefix) = dc.agg_measurement(amount, prefix) 
        self.assertEqual (agg_amount,1)
        self.assertEqual (agg_prefix,'<')

        # Case 4 : Amount is not a number
        amount = np.nan
        prefix = ['<', '<']
        (agg_amount,agg_prefix) = dc.agg_measurement(amount, prefix) 
        self.assertTrue (math.isnan(agg_amount))
        self.assertTrue (math.isnan(agg_prefix))

    def test_count_nas (self):
        # check nas in series correctly counted

        row = pd.Series([np.nan, np.nan, np.nan])
        self.assertEqual(dc.count_nas(row),3)

        row = pd.Series([np.nan, np.nan, 3])
        self.assertEqual(dc.count_nas(row),2)

        row = pd.Series([math.nan, math.nan, 3])
        self.assertEqual(dc.count_nas(row),2)

        row = pd.Series([1, 2, 3])
        self.assertEqual(dc.count_nas(row),0)

        row = pd.Series([])
        self.assertEqual(dc.count_nas(row),0)
    
    def test_filter_rows_by_nas_1 (self):
        # test whether rows are correctly removed by # of chemical nans
        # make sure nans outside of chemical amounts are ignored
        # All but one removed

        data = list()

        data.append([1, np.nan, 1.01, "<", np.nan, '='])
        data.append([2, "", 0.01, "=", np.nan, np.nan])
        data.append([3, "", 0.01, "=", 5.44, "<"])

        cols = [("ID",""), ("X",""), ("A","Amount"), ("A","Prefix"), ("B","Amount"), ("B","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        df = dc.filter_rows_by_nas (df,["A","B"], 0)

        self.assertEqual(list(df.index),[0])
        self.assertEqual(set(df.loc[0]),set([0.01,'=',5.44,'<',3,""]))
    
    
    def test_filter_rows_by_nas_2 (self):
        # test whether rows are correctly removed by # of chemical nans
        # make sure nans outside of chemical amounts are ignored
        # None removed

        data = list()

        data.append([1, np.nan, 1.01, "<", np.nan, '='])
        data.append([2, "", 0.01, "=", np.nan, np.nan])
        data.append([3, "", 0.01, "=", 5.44, "<"])

        cols = [("ID",""), ("X",""), ("A","Amount"), ("A","Prefix"), ("B","Amount"), ("B","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        df = dc.filter_rows_by_nas (df,["A","B"], 1)

        self.assertEqual(list(df.index),[0,1,2])

    def test_get_chemical_averages (self):
        # test getting averages for chemical amounts and missing columns
        data = list()

        data.append([1, np.nan, 1.00, "<", np.nan, '='])
        data.append([2, "", 0.01, "=", np.nan, np.nan])
        data.append([3, "", 0.01, "=", 5.44, "<"])

        cols = [("ID",""), ("X",""), ("A","Amount"), ("A","Prefix"), ("B","Amount"), ("B","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        (amount_avgs, missing_chemicals) = dc.get_chemical_averages (df, ["A", "B"])
        self.assertEqual(amount_avgs["A"],0.34)
        self.assertEqual(amount_avgs["B"],5.44)
        self.assertEqual(missing_chemicals,[])

    def test_get_chemical_averages_missing (self):
        # test getting averages for chemical amounts and missing columns
        # there is now a missing column
        data = list()

        data.append([1, np.nan, 1.00, "<", np.nan, '='])
        data.append([2, "", 0.01, "=", np.nan, np.nan])
        data.append([3, "", 0.01, "=", np.nan, "<"])

        cols = [("ID",""), ("X",""), ("A","Amount"), ("A","Prefix"), ("B","Amount"), ("B","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        (amount_avgs, missing_chemicals) = dc.get_chemical_averages (df, ["A", "B"])
        self.assertEqual(amount_avgs["A"],0.34)
        self.assertEqual(missing_chemicals,["B"])
    
    def test_fill_dataset_nans (self):
        # test filling dataset with nans according to average

        data = list()

        data.append([1, np.nan, 1.00, "<", np.nan, '='])
        data.append([2, "", 0.01, "=", np.nan, np.nan])
        data.append([3, "", 0.01, "=", 5.44, "<"])

        cols = [("ID",""), ("X",""), ("A","Amount"), ("A","Prefix"), ("B","Amount"), ("B","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        amount_avgs = {"A" : 1, "B": 2}
        missing_chemicals = []

        dc.fill_dataset_nans (df, ["A","B"], amount_avgs, missing_chemicals)

        self.assertEqual(set(df.loc[0]),set([1, np.nan, 1.00, '<', 2.00, '=']))
        self.assertEqual(set(df.loc[1]),set([2, "", 0.01, '=', 2.00, '=']))
        self.assertEqual(set(df.loc[2]),set([3, "", 0.01, '=', 5.44, '<']))

    def test_fill_dataset_nans_missing (self):

        # test filling dataset with nans according to average
        # there is a row with all NaNs to be removed

        data = list()

        data.append([1, np.nan, 1.00, "<", np.nan, '='])
        data.append([2, "", 0.01, "=", np.nan, np.nan])
        data.append([3, "", 0.01, "=", np.nan, "<"])

        cols = [("ID",""), ("X",""), ("A","Amount"), ("A","Prefix"), ("B","Amount"), ("B","Prefix")]
        cols = pd.MultiIndex.from_tuples(cols)
        df = pd.DataFrame(data, columns=cols)

        amount_avgs = {"A" : 1, "B": np.nan}
        missing_chemicals = ["B"]

        dc.fill_dataset_nans (df, ["A","B"], amount_avgs, missing_chemicals)

        self.assertEqual(set(df.loc[0]),set([1, np.nan, 1.00, '<']))
        self.assertEqual(set(df.loc[1]),set([2, "", 0.01, '=']))
        self.assertEqual(set(df.loc[2]),set([3, "", 0.01, '=']))
 

if __name__ == '__main__':
    unittest.main()