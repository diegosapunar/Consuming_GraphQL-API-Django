from django.http import HttpResponse
from django.views.generic import TemplateView
import requests
import json
from django.shortcuts import render

_URL_API = 'https://integracion-rick-morty-api.herokuapp.com/graphql'
# _URL_API = 'https://rickandmortyapi.com/graphql/'

# SOURCE: https://towardsdatascience.com/connecting-to-a-graphql-api-using-python-246dda927840

def index(request):
    page = 1
    query = """
        query {{
            episodes(page: {page}) {{
                info {{
                count
                next
                }}
                results {{
                id
                name
                air_date
                episode
                }}
            }}
        }}
    """
    output = []

    while True:
        r = requests.post(_URL_API, json={'query': query.format(page=str(page))})
        json_data = json.loads(r.text)
        next_ = json_data['data']['episodes']['info']['next']
        render_data = json_data['data']['episodes']['results']
        for epi in render_data:
            _dic_aux = {}
            _dic_aux['id'] = epi['id']
            _dic_aux['name'] = epi['name']
            _dic_aux['air_date'] = epi['air_date']
            _dic_aux['episode'] = epi['episode']
            output.append(_dic_aux)
        if next_:  # hay otra pagina
            page += 1
        else:
            break

    return render(request, 'index.html', {'episodes': output})


def episode(request, episode_id):
    query = """
        query {{
            episode (id: {episode_id}) {{
                name
                air_date
                episode
                characters {{
                    id
                    name
                }}
            }}
        }}
        """
    r = requests.post(_URL_API, json={'query': query.format(episode_id=str(episode_id))})
    json_data = json.loads(r.text)
    render_data = json_data['data']['episode']

    return render(request, 'episode.html', render_data)


def character(request, character_id):
    query = """
        query {{
            character (id: {character_id}) {{
                name
                status
                    species
                type
                gender
                origin {{
                    id
                    name
                }}
                location {{
                    id
                    name
                }}
                image
                episode {{
                    id
                    name
                }}
            }}
            }}
    """
    r = requests.post(
        _URL_API, json={'query': query.format(character_id=str(character_id))})
    json_data = json.loads(r.text)
    render_data = json_data['data']['character']

    return render(request, 'character.html', render_data)


def location(request, location_id):
    query = """
        query {{
            location (id: {location_id}) {{
                name
                type
                dimension
                residents {{
                    id
                    name
                }}
                }}
            }}
    """
    r = requests.post(
        _URL_API, json={'query': query.format(location_id=str(location_id))})
    json_data = json.loads(r.text)
    render_data = json_data['data']['location']

    if not render_data['residents'][0]["id"]:
        del render_data['residents']
    return render(request, 'location.html', render_data)


def search(request):
    '''
    SOURCE : https: // stackoverflow.com/questions/54678389/search-bar-in-django
    SOURCE : https: // stackoverflow.com/questions/17716624/django-csrf-cookie-not-set
    SOURCE : https://docs.djangoproject.com/en/3.0/ref/request-response/
    '''
    search_term = request.POST.get('search', '')
    
    # characters
    query_characters = """
    query {{
        characters(filter: {{name: "{search_term}" }}) {{
            results {{
                id
                name
            }}
        }}
    }}
    
    """
    try:
        r = requests.post(_URL_API, json={'query': query_characters.format(search_term=search_term)})
        json_data = json.loads(r.text)
        characters = json_data['data']['characters']['results']
    except: 
        characters = [{'id': "",
                       'name': ""}]

    # episodes
    query_episodes = """
    query {{
        episodes(filter: {{name: "{search_term}" }}) {{
            results {{
                id
                name
            }}
        }}
    }}
    """
    try:
        r = requests.post(_URL_API, json={'query': query_episodes.format(search_term=search_term)})
        json_data = json.loads(r.text)
        episodes = json_data['data']['episodes']['results']
    except:
        episodes = [{'id': "",
                       'name': ""}]

    # locations
    query_locations = """
        query {{
            locations(filter: {{name: "{search_term}" }}) {{
                results {{
                    id
                    name
                }}
            }}
        }}
    """
    try:
        r = requests.post(_URL_API, json={'query': query_locations.format(search_term=search_term)})
        json_data = json.loads(r.text)
        locations = json_data['data']['locations']['results']
    except:
        locations = [{'id': "",
                       'name': ""}]

    return render(request, 'search.html',
                    {'characters': characters,
                     'episodes': episodes, 
                     'locations': locations})
