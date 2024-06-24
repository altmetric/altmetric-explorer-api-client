class Filters:
    '''Holds a list of filters and provides methods that transform them
     into query parameters and message digests.'''

    def __init__(self):
        """Initializes a new Filters object"""
        self.items = []

    def add_filter(self, arg, value):
        """Add a new filter to the list of filters

        Args:
            arg (string): name of the filter
            value (string, list, tuple or set): filter value(s)

        Returns:
            Filters: self
        """
        self.items.append((arg, value))
        return self

    def __len__(self):
        """Count of filters

        Returns:
            integer: number of filters stored
        """
        return len(self.items)

    def message(self):
        """Convert the Filters to a message that can be used to construct a
        digest for authentication.

        See https://www.altmetric.com/explorer/documentation/api#authentication

        Returns:
            string: the digest
        """
        result = []
        for arg, value in sorted(self.items):
            result.append(arg)
            if type(value) in (list, tuple, set):
                for val in value:
                    result.append(val)
            else:
                result.append(value)
        return '|'.join(result)

    def __str__(self):
        """Create a string representation of the Filters in the form of query
        parameters for convenience.

        Returns:
            string: api query parameters
        """
        result = []
        for arg, value in self.items:
            if type(value) == list or type(value) == tuple:
                for val in value:
                    result.append(f'filter[{arg}][]={val}')
            else:
                result.append(f'filter[{arg}]={value}')
        return '&'.join(result)
