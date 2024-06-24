from .filters import Filters


class Query:
    '''Builder class that builds up a list of parameters to be passed to an
    API endpoint and generates a URL query string'''

    def __init__(self, **kvargs):
        '''Initialise a Query with an initial set of params'''
        self.items = []
        self.filters = Filters()
        self.add_params(**kvargs)

    def add_params(self, **kvargs):
        """Add parameter(s) to the query

        Returns:
            Query: self
        """
        for arg, value in kvargs.items():
            match arg:
                case 'page_size':
                    self.items.append(f'page[size]={value}')
                case 'page_number':
                    self.items.append(f'page[number]={value}')
                case 'order':
                    self.items.append(f'filter[order]={value}')
                case ('key' | 'digest'):
                    self.items.append(f'{arg}={value}')
                case _:
                    self.filters.add_filter(arg, value)
        return self

    def add_auth(self, api_key, digest):
        """Add authorisation fields the query

        Args:
            api_key (string): public API key (NOT the secret)
            digest (string): digest calculated using the filters and the secret key

        Returns:
            Query: self
        """
        return self.add_params(key=api_key, digest=digest)

    def add_str(self, item):
        """Add an arbitrary item to the query in the form `param=value`

        Args:
            item (Object): any object that responds to __str__ and returns a valid query string

        Returns:
            Query: self
        """
        self.items.append(str(item))
        return self

    def __str__(self):
        """Compile a URL query string from the items provided to the builder methods.

        Returns:
            string: the URL query string

        Notes:
            The string created is not URL encoded
        """
        result = []

        if self.items:
            result.append("&".join(self.items))

        if self.filters:
            result.append(str(self.filters))

        return '&'.join(result)
