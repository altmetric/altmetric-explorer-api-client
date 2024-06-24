class Filters:
    '''Holds a list of filters and provides accessors to the authentication message string as well
       as the query string itself.'''
    def __init__(self):
        self.items = []

    def add_filter(self, arg, value):
        self.items.append((arg, value))
        return self

    def __len__(self):
        return len(self.items)

    def message(self):
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
        result = []
        for arg, value in self.items:
            if type(value) == list or type(value) == tuple:
                for val in value:
                    result.append(f'filter[{arg}][]={val}')
            else:
                result.append(f'filter[{arg}]={value}')
        return '&'.join(result)


