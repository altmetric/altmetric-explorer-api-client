import itertools


class Response:
    """The response object that holds onto the meta data and data iterator
    """

    def __init__(self, all_pages):
        self.data_iterator, self.meta_iterator = itertools.tee(all_pages)
        self.first_page = next(self.meta_iterator)

    def data(self):
        for page in self.data_iterator:
            for row in page.get('data'):
                yield row

    def meta(self):
        return self.first_page["meta"]["response"]
