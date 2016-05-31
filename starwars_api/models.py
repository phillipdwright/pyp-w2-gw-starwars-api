from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        self.__dict__.update(json_data)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        json_data = models[cls.RESOURCE_NAME]['retrieval_method'](resource_id)
        return cls(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return models[cls.RESOURCE_NAME]['qs']()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        # Thanks to group 4 for the encoding fix in this method!
        self.name = self.name.encode('utf8', 'ignore')
        return 'Person: {0}'.format(self.name)
    
    def get_appearances(self):
        """
        Returns a FilmsQuerySet object representing the films in which this
        character appears.
        """
        appearances = self.films
        return FilmsQuerySet(appearances)


class Films(BaseModel):
    RESOURCE_NAME = 'films'
    
    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self, subset):
        self.objects = []
        self.total = 0
        retrieve = models[self.RESOURCE_NAME]['retrieval_method']
        page = 1
        data = retrieve(page=page)
        results = data['results']
        while results:
            next_obj = models[self.RESOURCE_NAME]['model'](results.pop(0))
            if subset:
                if next_obj.url in subset:
                    self.objects.append(next_obj)
            else:
                self.objects.append(next_obj)
            self.total += 1
            # If we run out of results and there is a next page
            if not results and data['next']:
                page += 1
                data = retrieve(page=page)
                results = data['results']

    def __iter__(self):
        return iter(self.objects)

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        return next(iter(self))

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.total


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self, subset=[]):
        super(PeopleQuerySet, self).__init__(subset)

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self, subset=[]):
        super(FilmsQuerySet, self).__init__(subset)

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))


models = {
    'people': {
        'retrieval_method': api_client.get_people,
        'qs': PeopleQuerySet,
        'model': People 
    },
    'films': {
        'retrieval_method': api_client.get_films,
        'qs': FilmsQuerySet,
        'model': Films 
    }
}


luke = People.get(1)
luke_films = luke.get_appearances()
for film in luke_films:
    print(film)