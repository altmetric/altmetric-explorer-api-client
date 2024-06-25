import itertools
import requests


class Page:
    '''Encapsulates a page returned from the api and provides accessor methods
    '''

    def __init__(self, raw_response):
        '''Initialize a page

        Args:
            raw_response (requests.Response): the raw response returned by `requests`
        '''
        self.raw_response = raw_response
        self.json = raw_response.json()

    def next_page(self):
        '''Get the next page if there is one

        The next page is found by looking for the links.next key in an API response.
        If the key is found then it will contain the URL of the next page and this
        method will retrieve it and use the response to create and return a new Page.

        If the key is not found then this method will return None.

        Returns:
            Page: the next page, or None if this is the last page
        '''
        url = self.json.get('links', {}).get('next', None)
        if url:
            return Page(requests.get(url))

    @property
    def status_code(self):
        '''Get the status code of the request to get the page of data

        Returns:
            int: HTTP status code
        '''
        return self.raw_response.status_code

    @property
    def data(self):
        '''Get the data from the page as a list of Python dictionaries

        Returns:
            list: a list of dictionaries or an empty list if the 'data' key is not found
        '''
        return self.json.get('data', [])

    @property
    def meta(self):
        '''Get the meta tag from the page

        Returns:
            dict: contents of the meta tag or and empty dictionary if the meta tag is not present
        '''
        return self.json.get('meta', {})


class Response:
    '''Encapsulates the response from an api query'''

    def __init__(self, raw_response):
        '''Initialize a Response

        Args:
            raw_response (requests.response): a response from a call to the api using the `requests` HTTP library
        '''
        self.raw_response = raw_response
        self.first_page = Page(raw_response)

    @ property
    def status_code(self):
        '''Get the status code of the request

        Returns:
            int: HTTP status code
        '''
        return self.first_page.status_code

    @ property
    def data(self):
        '''Returns a lazy sequence of rows from the data returned from the API

        Yields:
            dict: a row of data until all rows of all pages have been exhausted
        '''
        page = self.first_page
        while page:
            yield from page.data
            page = page.next_page()

    @ property
    def meta(self):
        '''Returns the meta['response'] data from an API call

        Returns:
            dict: meta data
        '''
        return self.first_page.meta.get('response', {})
