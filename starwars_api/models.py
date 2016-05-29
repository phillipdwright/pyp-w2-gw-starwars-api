from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

#from client import SWAPIClient, SWAPIClientError

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
        try:
            resource = cls.RESOURCE_NAME
        except:
            resource = ''
        
        if resource == 'people':
            json_data = api_client.get_people(resource_id)
            return People(json_data)
        elif resource == 'films':
            json_data = api_client.get_films(resource_id)
            return Films(json_data)
            
        raise ValueError('resource name not defined')

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        try:
            resource = cls.RESOURCE_NAME
        except:
            resource = ''
        
        if cls.RESOURCE_NAME == 'people':
            return PeopleQuerySet()
        elif cls.RESOURCE_NAME == 'films':
            return FilmsQuerySet()
        
        raise ValueError('resource name not defined')


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        try:
            return 'Person: {0}'.format(self.name)
        except UnicodeEncodeError:
            return 'Person: {0}'.format(self.url)


class Films(BaseModel):
    RESOURCE_NAME = 'films'
    
    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.objects = []
        self.total = 0

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

    def __init__(self):
        super(PeopleQuerySet, self).__init__()
        # Get results from the first page
        page = 1
        data = api_client.get_people(page=page)
        results = data['results']
        while results:
            self.objects.append(People(results.pop(0)))
            #print(self.objects[-1])
            self.total += 1
            # If we run out of results and there is a next page
            if not results and data['next']:
                page += 1
                data = api_client.get_people(page=page)
                results = data['results']

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()
        page = 1
        data = api_client.get_films(page=page)
        results = data['results']
        while results:
            self.objects.append(Films(results.pop(0)))
            #print(self.objects[-1])
            self.total += 1
            # If we run out of results and there is a next page
            if not results and data['next']:
                page += 1
                data = api_client.get_films(page=page)
                results = data['results']

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))


# people = PeopleQuerySet()
# for person in people:
#     print(person)

# films = Films.all()
# for film in films:
#     print(film)