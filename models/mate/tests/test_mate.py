import pandas
import pytest

from models.mate.mate import Mate


class TestMate:
    def test_convert_src_fails_on_empty_df(self, mate_load: Mate):
        with pytest.raises(KeyError, match='czy_st_bezp'):
            mate_load.convert_src(pandas.DataFrame())

    def test_convert_src_fails_on_wrong_df(self, mate_load: Mate):
        dataframe = pandas.read_csv('rfs_trans_src.txt', sep='|', header=None)
        with pytest.raises(KeyError, match='czy_st_bezp'):
            mate_load.convert_src(dataframe)

    def test_convert_src_fails_on_missing_columns(self, mate_load: Mate):
        dataframe = pandas.DataFrame({
            'czy_st_bezp': ['N', 'T']
        })
        with pytest.raises(KeyError):
            mate_load.convert_src(dataframe)

    def test_convert_src_correct_typ_conversion(self, mate_load: Mate):
        dataframe = pandas.DataFrame({
            'czy_st_bezp': ['N', 'T', 'X'],
            'strategia': [1, 3, 4],
            'rachunek': [123, 456, 789],
            'kod_klienta': ['A', 'B', 'C'],
            'data': ['2024-06-01', '2024-06-02', '2024-06-03']
        })
        result = mate_load.convert_src(dataframe)
        expected_typ = pandas.Series(['I', 'A', pandas.NA])
        pandas.testing.assert_series_equal(result['typ'], expected_typ, check_names=False)

    def test_convert_src_correct_portfolio_id_assignment(self, mate_load: Mate):
        dataframe = pandas.DataFrame({
            'czy_st_bezp': ['N', 'T', 'X', 'N', 'T', 'X'],
            'strategia': [1, 3, 4, 7, 2, 5],
            'rachunek': [123, 456, 789, 101, 112, 131],
            'kod_klienta': ['A', 'B', 'C', 'D', 'E', 'F'],
            'data': ['2024-06-01', '2024-06-02', '2024-06-03', '2024-06-04', '2024-06-05', '2024-06-06']
        })

        result = mate_load.convert_src(dataframe)

        expected_portfolio_id = pandas.Series([6, 9, 9, 8, ' ', ' '], dtype="object")
        pandas.testing.assert_series_equal(result['portfolio_id'], expected_portfolio_id, check_names=False)

    def test_convert_src_correct_columns(self):
        dataframe = pandas.DataFrame({
            'czy_st_bezp': ['N', 'T'],
            'strategia': [1, 3],
            'rachunek': [123, 456],
            'kod_klienta': ['A', 'B'],
            'data': ['2024-06-01', '2024-06-02'],
            'extra_column': ['extra1', 'extra2']
        })
        result = Mate.convert_src(dataframe)
        expected_columns = ['rachunek', 'kod_klienta', 'typ', 'data', 'portfolio_id']
        assert list(result.columns) == expected_columns

    def test_convert_src_handles_null_values(self):
        dataframe = pandas.DataFrame({
            'czy_st_bezp': ['N', None, 'T'],
            'strategia': [1, None, 3],
            'rachunek': [123, 456, 789],
            'kod_klienta': ['A', 'B', 'C'],
            'data': ['2024-06-01', '2024-06-02', '2024-06-03']
        })
        result = Mate.convert_src(dataframe)
        expected_typ = pandas.Series(['I', pandas.NA, 'A'])
        expected_portfolio_id = pandas.Series([6, ' ', 9], dtype="object")
        pandas.testing.assert_series_equal(result['typ'], expected_typ)
        pandas.testing.assert_series_equal(result['portfolio_id'], expected_portfolio_id)

    def test_convert_src_handles_null_values(self):
        dataframe = pandas.DataFrame({
            'czy_st_bezp': ['N', None, 'T'],
            'strategia': [1, None, 3],
            'rachunek': [123, 456, 789],
            'kod_klienta': ['A', 'B', 'C'],
            'data': ['2024-06-01', '2024-06-02', '2024-06-03']
        })

        result = Mate.convert_src(dataframe)

        expected_typ = pandas.Series(['I', pandas.NA, 'A'], name='typ')
        expected_portfolio_id = pandas.Series([6, ' ', 9], dtype="object", name='portfolio_id')

        pandas.testing.assert_series_equal(result['typ'], expected_typ, check_names=False)
        pandas.testing.assert_series_equal(result['portfolio_id'], expected_portfolio_id, check_names=False)
