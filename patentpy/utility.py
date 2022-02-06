import sys, traceback, datetime
import urllib.request, shutil, zipfile, re
from os import remove


def get_date_tues(year, week):
    """Calculates Tuesday's date for week ``week`` of year ``year``.
    
    Helper function the USPTO patent grant date (Tuesdays) for a given `week` and `year` to aid in 
    obtaining file name and url containing zip folder to download.
    
    Args: 
        year (int): integer corresponding to the ``week`` th week in year ``year``.
        week (int): integer corresponding to year ``year``.
    
    Returns:
        date: returns a ``datetime.date`` corresponding to the Tuesday of week ``week`` of year ``year``.

    Raises:
        TypeError: 
            If 'year' or 'week' are not both integers. Will exit.
        ValueError: 
            When calculated date is not in valid range (1976 - present), i.e date is in the future. 
    """
    if not (isinstance(year, int) and isinstance(week, int)):
        raise TypeError("`year` and `week` arguments must be integers")
        
    curr_day = datetime.datetime.now().date()
        
    # get first day of the year
    first_day = datetime.date(year, 1, 1)
    while first_day.weekday() != 1:
        first_day += datetime.timedelta(days=1)
    
    # calcuate tuesday
    tues = first_day + datetime.timedelta(days=7*(week-1))
    
    # check if tuesday is in the future
    # check if tuesday exceeds year's range
    if tues > curr_day:
        raise ValueError("week {}'s Tuesday of year {} is in the future".format(week, year))
    if tues > datetime.date(year, 12, 31):
        raise ValueError("week {}'s Tuesday exceeded the date range of year {}".format(week, year))
    # Note: better usability to just have arg week = [i for i in range(0,54)], to capture entire year.
    # is_leap_yr = True if (year % 4 == 0 and year % 100 != 0) or (year % 400) else False
    # if first_day.day + 7 * (week-1) >= 365 + is_leap_yr:
    return tues

def get_file_name(year, week):
    """Formats the url string and file name expected based on uspto format using date information.
    
    Calls the helper function ``get_date_tues()`` to obtain date information from ``week`` and ``year``, 
    which is then utilized for file name and url formating.
    
    Args: 
        year (int): integer corresponding to the ``week`` th week in year ``year``.
        week (int): integer corresponding to year ``year``.
    
    Returns:
        string: returns expected file name as a string
 
    """
    try:
        file_date = get_date_tues(year, week)
    except ValueError as ve:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, ve.__traceback__, limit=1)
        return

    month, day = file_date.month, file_date.day
    if file_date.year < 2002:
        file_name = "pftaps{}{:02d}{:02d}_wk{:02d}".format(year, month, day, week) + ".txt"
    elif file_date.year < 2005:
        file_name = "pg{:02d}{:02d}{:02d}".format(year-2000, month, day)  + ".xml"
    else:
        file_name = "ipg{:02d}{:02d}{:02d}".format(year-2000, month, day) + ".xml"
    return file_name

def download_zip(url, zip_name):
    with urllib.request.urlopen(url) as res, open(zip_name, 'w+b') as output_file:
        shutil.copyfileobj(res, output_file)
    return

def uncompress_zip(file_name, zip_name):
    """Helper function used to uncompress zip file downloaded in from uspto url link. 
        
    Args: 
        zip_file (str): name of zip file from which file containing uspto bulk patent data will be extracted
        file_name (str): expected file name of in XML or TXT document containing uspto bulk patent data.
    
    Returns:
        string: returns filename of output file if completed successfully else False

    Raises:
        FileNotFoundError: 
            If expected filename could not be found in zip folder.
    """
    regex_to_match = re.compile("(./)?(?i:{})".format(file_name))
    with zipfile.ZipFile(zip_name, 'r') as zip_uspto:
        files = " ".join([file.filename for file in zip_uspto.infolist()])
        poss_match = regex_to_match.search(files)
        if poss_match:
            # file found
            output_file = poss_match[0]
            zip_uspto.extract(output_file)
    remove(zip_name)            # delete zip
    if not poss_match:
        raise FileNotFoundError("Unable to extract file {} from downloaded zip file".format(file_name)) 
    return output_file