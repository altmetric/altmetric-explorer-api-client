import requests


class Page:
    '''Encapsulates a page returned from the api and provides accessor methods
    '''

    def __init__(self, raw_response):
        '''Initialize a page

        Args:
            raw_response (requests.Response): the raw response returned by `requests`
        '''
        self.__raw_response = raw_response
        self.__json = raw_response.json()

    def next_page(self):
        '''Get the next page if there is one

        The next page is found by looking for the links.next key in an API response.
        If the key is found then it will contain the URL of the next page and this
        method will retrieve it and use the response to create and return a new Page.

        If the key is not found then this method will return None.

        Returns:
            Page: the next page, or None if this is the last page
        '''
        url = self.__json.get('links', {}).get('next', None)
        if url:
            return Page(requests.get(url))

    def __repr__(self):
        return f'Page({self.__raw_response})'

    @property
    def status_code(self):
        '''Get the status code of the request to get the page of data

        Returns:
            int: HTTP status code
        '''
        return self.__raw_response.status_code

    @property
    def data(self):
        '''Get the data from the page as a list of Python dictionaries

        Returns:
            list: a list of dictionaries or an empty list if the 'data' key is not found
        '''
        return self.__json.get('data', [])

    @property
    def included(self):
        '''Get the included objects from the page as a list of Python dictionaries

        Returns:
            list: a list of dictionaries or an empty list if the 'data' key is not found
        '''
        return self.__json.get('included', [])

    @property
    def meta(self):
        '''Get the meta tag from the page

        Returns:
            dict: contents of the meta tag or and empty dictionary if the meta tag is not present
        '''
        return self.__json.get('meta', {})


class Response:
    '''Encapsulates the response from an api query'''

    def __init__(self, raw_response):
        '''Initialize a Response

        Args:
            raw_response (requests.response): a response from a call to the api using the `requests` HTTP library
        '''
        self.raw_response = raw_response
        self.text = raw_response.text
        self.first_page = None
        if raw_response.status_code < 300:
            try:
                self.first_page = Page(raw_response)
            except ValueError:
                # a 2xx response with a non-JSON body (e.g. a proxy
                # interstitial) leaves first_page None so the accessors degrade
                # to None/empty instead of raising here
                pass

    @property
    def status_code(self):
        '''Get the status code of the request

        Returns:
            int: HTTP status code
        '''
        return self.raw_response.status_code

    @property
    def ok(self):
        '''Check if the request succeeded

        Returns:
            bool: True if the result as in the 200 range was an error
                  else False
        '''
        return self.status_code in range(200, 300)

    @property
    def failed(self):
        '''Check if the request failed

        Returns:
            bool: True if there was an error else False
        '''
        return not self.ok

    @property
    def data(self):
        '''Returns a lazy sequence of rows from the data returned from the API

        Yields:
            dict: a row of data until all rows of all pages have been exhausted
        '''
        if self.failed:
            return

        page = self.first_page
        while page:
            rows = page.data
            if isinstance(rows, list):
                yield from rows
            else:
                # a single-object payload (e.g. identifier_lists) — yield it
                # whole rather than iterating a dict as its keys
                yield rows
            page = page.next_page()

    @property
    def included(self):
        '''Returns a lazy sequence of rows from the included field returned from the API

        Yields:
            dict: a row of data until all rows of all pages have been exhausted
        '''
        page = self.first_page
        while page:
            yield from page.included
            page = page.next_page()

    @property
    def meta(self):
        '''Returns the meta['response'] data from an API call

        Returns:
            dict: meta data
        '''
        if self.first_page is None:
            return

        return self.first_page.meta.get('response', {})

    @property
    def resource(self):
        '''Returns the single data object from a non-paginated response.

        Some endpoints (e.g. identifier_lists) return a single object under
        `data` rather than a list of rows. Use this instead of `data`, which is
        a generator that assumes `data` is a list.

        Returns:
            dict: the data object, or None if the request failed or the
                response has no single data object
        '''
        if self.first_page is None:
            return None

        data = self.first_page.data
        return data if isinstance(data, dict) else None

    @property
    def errors(self):
        '''Returns the errors from an error response envelope.

        Returns:
            list: the `errors` array, or an empty list if there were none or
                the body was not a JSON object
        '''
        if self.ok:
            return []

        try:
            body = self.raw_response.json()
        except ValueError:
            return []

        errors = body.get('errors') if isinstance(body, dict) else None
        # guarantee a list even if the body has a null/object/absent `errors`
        return errors if isinstance(errors, list) else []

    def __repr__(self):
        return f'Response({self.raw_response})'
