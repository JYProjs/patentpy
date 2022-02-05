import sys, traceback, datetime
import pandas as pd
from os import remove
from tqdm import tqdm

from convert_funcs import txt_to_df
from patentpy.convert_xml1 import xml1_to_df
from patentpy.convert_xml2 import xml2_to_df
from patentpy.utility import get_file_name, download_zip, uncompress_zip

# User-facing function `get_bulk_patent_data()`
def get_bulk_patent_data(year, week, output_file = None):
    """Obtains USPTO data in csv or dataframe from user-inputted values, `year` and `week`.  
    
    User-friendly function that utilizes `convert_txt_to_df` helper function after error 
    checking user-inputted `year` and `week` values (May either both be integer values or 
    equal-length lists). Used to get data from multiple files, each corresponding to a 
    'year'-'week' pair, from USPTO website (which may be stored as TXT or XML file formats).
    
    Args: 
        year (int or list[int]): integer or list of integers for 'year' in 'year'-'week' 
            pair corresponding to patent grants issued the ``week`` th week of year ``year``.
        week (int or list[int]): integer or list of integers for 'week in 'year'-'week' 
            pair corresponding to patent grants issued that ``week`` th week of year ``year``.
        output_file (str, default None): path of '.csv' file to store data.  
    
    Returns:
        DataFrame or bool: returns ``pandas.DataFrame`` object if output_file is ``None`` 
        else returns boolean ``True``

    Raises:
        TypeError:
            * ``year`` or ``week`` are not both integers or lists of integers
        ValueError: 
            * ``year`` or ``week`` contain missing values or contain invalid values 
            (i.e. week > 53, year < 1776)
            * ``year`` or ``week`` are unequal length lists. 
            * `dates_df` does not contain columns 1) 'year' or 2) 'week' 
            * if `output_file` is not a '.csv' file.

            **Note**: An "error" will be raised if there is no patent data available for week 53  
            for a specific year or if dates are in the future for the current year, 
            however these entries will be skipped without halting execution.
    """
    # convert to list if int
    year = [year] if isinstance(year, int) else year
    week = [week] if isinstance(week, int) else week

    # not list, int, or float error
    if not ( isinstance(year, list) and isinstance(week, list) ):
        raise TypeError("`year` and `week` parameters must be list[int] or integers")
    # unequal length lists error
    if len(year) != len(week):
        raise ValueError("`year` and `week` parameters should be of equal lengths: \nyear = {}\nweek = {}"
                         .format(year, week))
    # missing/none values error
    if not ( all(x is not None for x in year) and 
            all(x is not None for x in week) ):
        raise ValueError("`year` and `week` parameters must not have missing or null values: \nyear = {}\nweek = {}"
                         .format(year, week))
    # values of wrong type error
    if not ( all(isinstance(x, int) for x in year) and 
            all(isinstance(x, int) for x in week) ):
        raise TypeError("`year` and `week` parameters should be integer values: \nyear = {}\nweek = {}"
                         .format(year, week))
    # get current day
    # add buffer for not yet uploaded current week of USPTO bulk patent data?
    curr_day = datetime.datetime.now()
    
    # check if year and week are valid
    if not all(x >= 1976 and x <= curr_day.year for x in year):
        raise ValueError("`year` value(s) must be between 1976 and current year, inclusive")
    if not all(x >= 1 and x <= 53 for x in week):
        raise ValueError("`week` value(s) must be between 1 and 53, inclusive")
        
    # create dataframe
    dates_df = pd.DataFrame(data = list(zip(year, week)), columns = ['year', 'week'])

    return convert_to_df(dates_df, output_file = output_file)


def convert_to_df(dates_df, output_file = None):
    """Converts TXT and XML files to CSV format or a dataframe.
    
    Internal Function without error checking that ``get_bulk_patent_data()`` calls. Iterates through 
    each row in dates_df DataFrame formated with columns [`year`, `week`] and downloads respective 
    zip file from United States Patent Trademark Office (USPTO) url. Extracts each zip folder (containing a TXT 
    or XML file) and parses files (extracting fields and converting it to CSV file format). 
    If no output file is provided, a temporary csv file is created and read into pandas at the end of execution. 
    Temporary files (zip, xml, etc.) are cleaned up.
    
    Args: 
        date_df (DataFrame): dataframe with columns: 1) 'year' and 2) 'week'. Values must all be integers. 
        output_file (str, default None): path of '.csv' file to store data. 

        **Note**: This function omits error checking for values / types in dataframe argument as its intended use
        is to be called by the ``get_bulk_patent_data()`` function
    
    Returns:
        DataFrame or bool: returns (``pandas.DataFrame`` object if `output_file` is ``None``
        or boolean ``True`` if `output_file` is provided) AND at least one week of data is able to be parsed 
        and converted to CSV format

    Raises:
        ValueError: 
            * `dates_df` does not contain columns 1) 'year' or 2) 'week' 
            * `output_file` is not end with '.csv'.
    """
    # check format of df; internal function so should not occur
    if not ('year' == dates_df.columns[0] and 'week' == dates_df.columns[1]):
        raise ValueError("`dates_df` parameter must have `year` and `week` columns; current columns = {}"
                         .format(dates_df.columns))
    # check if output file is CSV
    if output_file is not None:
        if not isinstance(output_file, str):
            raise ValueError("`output_file` parameter must be a path in the form of a string")
        elif output_file[len(output_file)-4:len(output_file)] != ".csv":
            raise ValueError('`output_file` parameter must be a ".csv" file')
    
    # base vars
    uspto_url = "https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/"
    dest_file = "temp-output.zip"
    temp_output_file = "temp-patent-package-output.csv"
    total_patents = 0
    
    # check if file exists/add header if needed
    csv_file = output_file if output_file else temp_output_file
    try:
        f = open(csv_file)
    except FileNotFoundError:        # no file exists, create file and write header
        with open(csv_file, 'w+') as f:
            f.write("WKU,Title,App_Date,Issue_Date,Inventor,Assignee,ICL_Class,References,Claims\n")
    else:
        f.close()        # close file if exists
    
    # convert all rows in df to that year & week's tuesday date (if exists)
    for row, curr_year, curr_week in tqdm(dates_df.itertuples(), total = dates_df.shape[0]):
        # get file name and url
        curr_file = get_file_name(curr_year, curr_week)
        if curr_file is None:
            print("SKIPPING PATENT DATA FOR WEEK {} OF YEAR {}...".format(curr_week, curr_year))
            continue
        curr_url = uspto_url + "{}/".format(curr_year) + curr_file[:-4] + ".zip"
        
        try:
            # try to download data with complete file name
            download_zip(curr_url, dest_file)
            # try to find and uncompress file from zip, and delete zip
            curr_file = uncompress_zip(curr_file, dest_file)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, e.__traceback__)
            print("UNABLE TO GET DATA, SKIPPING PATENT DATA FOR WEEK {} OF YEAR {}...".format(curr_week, curr_year))
            continue

        # convert to TXT or XML data to CSV format
        try:
            if curr_year < 2002:
                pat_count = txt_to_df(curr_file, csv_file, True, False)
            elif curr_year < 2005:
                pat_count = xml1_to_df(curr_file, csv_file, True, False)   # always append, no header, checked in file
            else:
                pat_count = xml2_to_df(curr_file, csv_file, True, False)   # always append, no header, checked in file
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, e.__traceback__)
            print("UNABLE TO CONVERT DATA, SKIPPING PATENT DATA FOR WEEK {} OF YEAR {}...".format(curr_week, curr_year))
            continue
        finally:
            # remove xml before next iteration, skip this year's week's data if unable to read
            remove(curr_file)
            
        total_patents += pat_count

    if total_patents == 0:
        if not output_file:
            print("ERROR, NO PATENTS FOUND, PLEASE RAISE A GITHUB ISSUE @ https://github.com/JYProjs/patentpy/issues")
            remove(temp_output_file)
        return -1 
    # get temp file contents and read into pandas as df if no output file specified
    if output_file is None:
        try:
            curr_df = pd.read_csv(temp_output_file)
        except:
            raise Exception("PANDAS UNABLE TO PARSE FINAL CSV FILE, DATA IS STORED IN STILL STORED IN FILE: {}. DELETE AS NECESSARY!!!".format(temp_output_file))
        remove(temp_output_file)

    

    return True if output_file else curr_df