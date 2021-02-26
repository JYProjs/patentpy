import datetime

def get_date_tues(year, week):
    # check `year` and `week` are integers; should not hit this error
    #if not ( isinstance(year, int) and isinstance(week, int) ):
    #    raise ValueError("`year` and `week` parameters must be integers")
        
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
    # is_leap_yr = True if (year % 4 == 0 and year % 100 != 0) or (year % 400) else False
    # if first_day.day + 7 * (week-1) >= 365 + is_leap_yr:
    return tues