import pytest, pandas
from os import remove
from datetime import date
from patentpy.utility import get_date_tues
from patentpy.convert_txt import convert_txt_to_df
from patentpy.acquire import get_bulk_patent_data

### TEST_GET_BULK_PATENT_DATA ###
# test generic; should return true and create/append to csv file.
def test_get_bulk_patent_data():
    # run func  x2 and see if csv formatted version == df version
    df = get_bulk_patent_data(1991, 1)
    get_bulk_patent_data(1991, 1, "test.csv")
    df_from_csv = pandas.read_csv("test.csv")
    remove("test.csv")
    assert df_from_csv.equals(df)

# test TypeError -- `years` & `weeks` not ints
def test_gbpd_not_ints():
    with pytest.raises(TypeError, match= r"integers"):
        get_bulk_patent_data(1991.1, 2, "test.csv")

# test TypeError -- not list of integers `year` & `week`
def test_gbpd_not_all_ints():
    with pytest.raises(TypeError, match= r"integer\b"):
        get_bulk_patent_data([1991, 1992, 1993], [1, 2, 3.0])

# test ValueError -- len(`year`) != len(`week`)
def test_gbpd_not_equal():
    with pytest.raises(ValueError, match= r"equal lengths"):
        get_bulk_patent_data([1991, 1992, 1993], [1, 2])

# test ValueError -- missing values in lists
def test_gbpd_missing():
    with pytest.raises(ValueError, match= r"missing or null"):
        get_bulk_patent_data([1991, None, 1993], [1, 3, 2])


### TEST_GET_DATE_TUES ###
# test get_date_tues with valid input
def test_get_date_tues():
    assert get_date_tues(1991, 6) == date(1991, 2, 5)

# test TypeError -- `year` or `week` not integers
def test_gdt_not_int():
    with pytest.raises(TypeError, match= r"integers"):
        get_date_tues(1991, 5.5)

# test ValueError --  future date
def test_gdt_future():
    with pytest.raises(ValueError, match= r"future"):
        get_date_tues(2050, 2)

# test ValueError -- no 53rd week in year
def test_gdt_no_53rd_wk():
    with pytest.raises(ValueError, match= r"date range"):
        get_date_tues(2020, 53)


### TEST_CONVERT_TXT_TO_DF ###
# test convert_txt_to_df with valid input
def test_convert_txt_to_df():
    # create test_df of dates, run func x2 and see if csv formatted version == df version
    test_df = pandas.DataFrame(data=[[1991, 1]], columns=['year', 'week'])
    df = convert_txt_to_df(test_df)
    convert_txt_to_df(test_df, "test_cttd.csv")
    df_from_csv = pandas.read_csv("test_cttd.csv")
    remove("test_cttd.csv")
    assert df_from_csv.equals(df)

# test ValueError -- incorrect column names
def test_cttd_bad_df():
    test_df = pandas.DataFrame(data=[[1991,1]], columns=['yr', 'wk'])
    with pytest.raises(ValueError, match= r"current columns"):
        convert_txt_to_df(test_df)

# test ValueError -- not CSV output_file
def test_cttd_not_CSV():
    test_df = pandas.DataFrame(data=[[1991,1]], columns=['year', 'week'])
    with pytest.raises(ValueError, match= r".*.csv.*"):
        convert_txt_to_df(test_df, "test.txt")



# should make convert_txt_to_df more modular to test download zip, getting url, etc separately.
# and add try and exceptions as necessary in convert_txt.py
