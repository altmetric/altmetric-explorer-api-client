import itertools
import requests


class Response:
    '''Encapsulates the response from an api query'''

    def __init__(self, raw_response):
        '''Initialize a Response

        Args:
            all_pages (iterator): an iterator over pages of data returned
            in response to an API query
        '''
        self.raw_response = raw_response
        self.response_json = raw_response.json()
        self.base_url = raw_response.url
        self.first_page = self.response_json.get('data')

    @property
    def status_code(self):
        return self.raw_response.status_code

    @property
    def data(self):
        '''Returns a lazy sequence of rows from the data returned from the API

        Yields:
            dict: a row of data
        '''
        for page in self.all_pages():
            yield from page

    def all_pages(self):
        first_page = self.response_json.get('data')
        yield first_page

        url = first_page.get('links', {}).get('next', None)
        while url:
            response = requests.get(url)
            page = response.json()
            url = page.get('links', {}).get('next', None)
            yield page.get('data')

    @property
    def meta(self):
        '''Returns the meta['response'] data from an API call

        Returns:
            dict: meta data
        '''
        return self.response_json["meta"]["response"]
