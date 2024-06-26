import base64
import hashlib
import hmac

import requests

from .query import Query
from .response import Response


def digest(secret, message):
    '''Calculates a cryptographic digest based on the user's API secret key and
    the values of some of the parameters as described here:

    https://www.altmetric.com/explorer/documentation/api#authentication
    '''
    if message is None:
        message = ''
    hmac_sha1 = hmac.new(secret.encode('utf-8'),
                         message.encode('utf-8'), hashlib.sha1)
    signature = base64.b64encode(hmac_sha1.digest()).decode('utf-8')
    signature = hmac_sha1.hexdigest()
    return signature


class Client:
    """Top level abstraction over the Altmetric Explorer API.
    """

    def __init__(self, api_endpoint, api_key, api_secret):
        """Initialises a new Client object

        Args:
            api_endpoint (string): the url of the explorer api (usually https://www.altmetric.com/explorer/api)
            api_key (string): your explorer api key
            api_secret (string): your explorer api secret key

        Raises:
            ValueError: if the api key or the api secret is None

        Notes:
            You can find your api key and secret at https://www.altmetric.com/explorer/settings
        """
        if api_key == None or api_secret == None:
            raise ValueError('api_key and api_secret cannot be None')

        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.api_secret = api_secret

    def get(self, path, **args):
        """Generic get method that constructs a call to an API path and returns a Response. An authentication digest is calculated behind the scenes using the
        api keys instance variables and the filters provided and added to the request automatically.

        Args:
            path (string): the path to query
            args (keyword list, accepts the following):
                page_size (int, optional): size of each page to be returned. Defaults to 100.
                order (string, optional): the field on which the results should be sorted. Defaults to None.
                limit (int, optional): maximum number of items to return.  Set to None to return everything. Defaults to None.

                All other keyword arguments are treated as filters e.g. timeframe, mention_sources_countries

        Returns:
            response: A Response object for the API call.
        """
        query = Query(**args)
        query.add_auth(self.api_key,
                       digest(self.api_secret, query.filters.message()))
        url = self.api_endpoint + '/' + path + '?' + str(query)

        return Response(requests.get(url))

    def get_attention_summary(self, **args):
        '''Shorthand accessor for research_outputs/attention'''
        return self.get('research_outputs/attention', **args)

    def get_demographics(self, **args):
        '''Shorthand accessor for research_outputs/demographics'''
        return self.get('research_outputs/demographics', **args)

    def get_journals(self, **args):
        '''Shorthand accessor for research_outputs/journals'''
        return self.get('research_outputs/journals', **args)

    def get_mention_sources(self, **args):
        ''' Shorthand accessor for research_outputs/mention_sources '''
        return self.get('research_outputs/mention_sources', **args)

    def get_mentions(self, **args):
        ''' Shorthand accessor for research_outputs/mentions '''
        return self.get('research_outputs/mentions', **args)
