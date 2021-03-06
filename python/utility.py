import datetime

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
