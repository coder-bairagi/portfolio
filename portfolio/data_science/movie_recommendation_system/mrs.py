import requests
import pickle
import os

# TMDB api key
api_key = "0615d21ff3792fb0a667b6846cadabc0"
# Current directory path
dir_path = os.path.dirname(os.path.abspath(__file__))

# Load pkl files
# movies.pkl here is new_df in the notebook
# similarity.pkl here is similarity in the notebook
file_path = os.path.join(dir_path, 'movies.pkl')
with open(file_path, 'rb') as file:
    movies_list = pickle.load(file)

file_path = os.path.join(dir_path, 'similarity.pkl')
with open(file_path, 'rb') as file:
    similarity = pickle.load(file)

def format_votes(vote_count):
    if vote_count >=1000000:
        return f'{vote_count / 1000000: 0.1f}M'
    elif vote_count >= 1000:
        return f'{vote_count / 1000: 0.1f}K'
    else:
        return str(vote_count)

def format_runtime(mins):
    hrs = mins // 60
    mins = mins % 60
    return f'{str(hrs)}h {str(mins)}m'

def get_tmdb_movie_id(movie):
    return movies_list[movies_list['title'] == movie]['movie_id'].iloc[0]

def fetch_details(base_url, movie_id, movie_name):
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US"
    video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=en-US"
    movie_response = requests.get(movie_url)
    credits_response = requests.get(credits_url)
    video_response = requests.get(video_url)
    movie_response = movie_response.json()
    credits_response = credits_response.json()
    video_response = video_response.json()
    genres = []
    for genre in movie_response['genres']:
        genres.append(genre['name'])
    production_companies = []
    for company in movie_response['production_companies']:
        production_companies.append(company['name'])
    casts = []
    for i, cast in enumerate(credits_response['cast']):
        profile_path = ''
        if i == 18:
            break
        else:
            if cast['profile_path'] != None:   
                profile_path = 'https://image.tmdb.org/t/p/w300' + cast['profile_path']
            else:
                profile_path = base_url + '/static/img/dummy-user.jpg'
            casts.append({
                'name': cast['name'],
                'profile_path': profile_path,
                'character': cast['character'],
            })
    video_key = video_response['results'][0]['key']
    directors = []
    writers = []
    for crew in credits_response['crew']:
        if crew['job'] == 'Director':
            directors.append(crew['name'])
        if crew['job'] == 'Screenplay':
            writers.append(crew['name'])

    recommendations = recommend(movie_name)

    details = {
        'movie': {
            'name': movie_response['original_title'],
            'poster_path': 'https://image.tmdb.org/t/p/w500' + movie_response['poster_path'],
            'genres': genres,
            'overview': movie_response['overview'],
            'production_companies': production_companies,
            'release_year': movie_response['release_date'][0:4],
            'runtime': format_runtime(movie_response['runtime']),
            'vote_average': round(movie_response['vote_average'], 1),
            'vote_count': format_votes(movie_response['vote_count']),
            'popularity': str(round(movie_response['popularity'], 2)) + '%',
            'video_path': "https://www.youtube.com/embed/" + video_key + "?autoplay=1&mute=1",
        },
        'casts': casts,
        'three_casts': casts[0:3],
        'directors': directors,
        'writers': writers,
        'recommendations': recommendations,
    }
    return details

def fetch_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    details = response.json()
    details['poster_path'] = 'https://image.tmdb.org/t/p/w500' + details['poster_path']
    return details

def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances = similarity[movie_index]
    recommendations = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:11]
    recommended_movies = []
    for movie in recommendations:
        id = movies_list.iloc[movie[0]]['movie_id']
        movie_details = fetch_movie(id)
        recommended_movies.append({
            'name': movies_list.iloc[movie[0]]['title'],
            'poster_path': movie_details['poster_path'],
            'release_year': movie_details['release_date'][0:4],
        })
    return recommended_movies