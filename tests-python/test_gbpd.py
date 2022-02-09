import pytest, pandas
from os import remove
from datetime import date
from patentpy.utility import get_date_tues
from patentpy.acquire import get_bulk_patent_data, convert_to_df

### TEST_GET_BULK_PATENT_DATA ###
# test generic; should return true and create/append to csv file.
def test_get_bulk_patent_data():
    # run func  x2 and see if csv formatted version == df version
    df = get_bulk_patent_data([i for i in range (2001, 2006, 2)], [1 for i in range(0, 3)])
    get_bulk_patent_data([i for i in range (2001, 2006, 2)], [1 for i in range(0, 3)], "test.csv")
    df_from_csv = pandas.read_csv("test.csv")
    remove("test.csv")
    assert (df_from_csv.equals(df), df.iloc[9521, 0], df.iloc[0, 0]) == (True, '06839901', 'D04357132')

# test Exception -- no uspto bulk data able to be converted
def test_gbpd_no_data_returned():
    with pytest.raises(Exception, match= r"NO PATENTS FOUND"):
        get_bulk_patent_data([i for i in range (2001, 2006, 2)], [53 for i in range(0, 3)])

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

def test_gbpd_zero_patents():
    with pytest.raises(Exception, match=r"NO PATENTS FOUND"):
        get_bulk_patent_data(2001,53)

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


### TEST_CONVERT_TO_DF ###
# TO DO: test download zip, getting url, etc separately
def test_ctd():
    # create test_df of dates, run func x2 and see if csv formatted version == df version
    test_df = pandas.DataFrame(data=[[1991, 1]], columns=['year', 'week'])
    df = convert_to_df(test_df)
    convert_to_df(test_df, "test_xtd1.csv")
    df_from_csv = pandas.read_csv("test_xtd1.csv")
    remove("test_xtd1.csv")
    assert df_from_csv.equals(df)

# test ValueError -- incorrect column names
def test_ctd_bad_df():
    test_df = pandas.DataFrame(data=[[1991,1]], columns=['yr', 'wk'])
    with pytest.raises(ValueError, match= r"current columns"):
        convert_to_df(test_df)

# test ValueError -- not CSV output_file
def test_ctd_not_CSV():
    test_df = pandas.DataFrame(data=[[1991,1]], columns=['year', 'week'])
    with pytest.raises(ValueError, match= r".*.csv.*"):
        convert_to_df(test_df, "test.txt")
