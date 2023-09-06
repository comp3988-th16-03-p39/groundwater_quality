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

        df = pivot_dataset(
            df,
            sample_id_columns=["ID"],
            per_sample_data=["X"],
            chemical_name_column="Name",
            values_per_chemical=["Y", "Z"],
            desired_chemical_names=["A", "B"],
        )

        # check dimensions
        self.assertTrue((df.columns.levels[0] == ['A', 'B', 'X', 'ID']).any())
        self.assertTrue((df.columns.levels[1] == ['Y', 'Z', '']).any())
        self.assertEqual(list(df.index), list(range(0, 2)))

        # check contents
        self.assertEqual(list(df["ID"]), [1, 2])
        self.assertEqual(list(df["X"]), [12, 8])
        self.assertEqual(list(df["A", "Y"])[0], [1])
        self.assertEqual(list(df["A", "Y"])[1], ['12'])

    def test_pivot2(self):
        # data is incomplete
        data = list()

        data.append([1, 12, "A", 1, "mg/L"])
        data.append([1, 12, "B", '<2', "g/L"])
        data.append([2, 8, "A", '12', "mg/L"])

        df = pd.DataFrame(data, columns=["ID", "X", "Name", "Y", "Z"])

        df = pivot_dataset(
            df,
            sample_id_columns=["ID"],
            per_sample_data=["X"],
            chemical_name_column="Name",
            values_per_chemical=["Y", "Z"],
            desired_chemical_names=["A", "B"],
        )

        # check dimensions
        self.assertTrue((df.columns.levels[0] == ['A', 'B', 'X', 'ID']).any())
        self.assertTrue((df.columns.levels[1] == ['Y', 'Z', '']).any())
        self.assertEqual(list(df.index), list(range(0, 2)))

        # check contents
        self.assertEqual(list(df["B", "Y"])[0], ['<2'])
        self.assertTrue(math.isnan(list(df["B", "Y"])[1]))

    def test_pivot3(self):
        # data is excessive
        data = list()

        data.append([1, 12, "A", 1, "mg/L"])
        data.append([1, 12, "B", '<2', "g/L"])
        data.append([2, 8, "A", '12', "mg/L"])
        data.append([2, 8, "B", '<0.01', "g/L"])
        data.append([2, 8, "B", '<0.02', "g/L"])

        df = pd.DataFrame(data, columns=["ID", "X", "Name", "Y", "Z"])

        df = pivot_dataset(
            df,
            sample_id_columns=["ID"],
            per_sample_data=["X"],
            chemical_name_column="Name",
            values_per_chemical=["Y", "Z"],
            desired_chemical_names=["A", "B"],
        )

        # check dimensions
        self.assertTrue((df.columns.levels[0] == ['A', 'B', 'X', 'ID']).any())
        self.assertTrue((df.columns.levels[1] == ['Y', 'Z', '']).any())
        self.assertEqual(list(df.index), list(range(0, 2)))

        # check contents
        self.assertEqual(list(df["ID"]), [1, 2])
        self.assertEqual(list(df["X"]), [12, 8])
        self.assertEqual(list(df["B", "Y"])[0], ['<2'])
        self.assertEqual(list(df["B", "Y"])[1], ['<0.01', '<0.02'])
        self.assertEqual(list(df["B", "Z"])[1], ['g/L', 'g/L'])

    def test_transform(self):
        pass

    def test_clean_units(self):
        # Test single value version, not dataset version
        pass

    def test_format_amount(self):
        pass


if __name__ == '__main__':
    unittest.main()
