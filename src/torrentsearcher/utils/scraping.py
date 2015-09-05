from bs4 import BeautifulSoup, SoupStrainer


class BeautifulSoupTableParser(object):
    def __init__(self, html, attrs=None):
        self._html = html
        self._attrs = attrs
        self._stainer = SoupStrainer('table')

    def _get_all_tables_in_page(self):
        tables = SoupStrainer('table')
        soup = BeautifulSoup(self._html, parse_only=tables)

        result = []
        unique_tables = set()

        for table in soup:
            if table not in unique_tables:
                result.append(table)

            unique_tables.add(table)

        return result
