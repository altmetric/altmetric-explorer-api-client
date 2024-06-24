import itertools


class Response:
    '''Encapsulates the response from an api query'''

    def __init__(self, all_pages):
        '''Initialize a Response

        Args:
            all_pages (iterator): an iterator over pages of data returned
            in response to an API query
        '''
        self.data_iterator, self.meta_iterator = itertools.tee(all_pages)
        self.first_page = next(self.meta_iterator)

    def data(self):
        '''Returns a lazy sequence of rows from the data returned from the API

        Yields:
            dict: a row of data
        '''
        for page in self.data_iterator:
            for row in page.get('data'):
                yield row

    def meta(self):
        '''Returns the meta['response'] data from an API call

        Returns:
            dict: meta data
        '''
        return self.first_page["meta"]["response"]
