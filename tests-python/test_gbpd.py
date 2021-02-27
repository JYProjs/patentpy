import pandas

from python.acquire import get_bulk_patent_data

df = get_bulk_patent_data(1991, 1)

df.head()