import pandas

from python.acquire import get_bulk_patent_data


def test_get_bulk_patent_data():
    assert get_bulk_patent_data(1991, 1, "test.csv") == True