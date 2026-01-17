"""API views for media details."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from media.services import TMDbService


@login_required
def media_details_api(request, media_type, tmdb_id):
    """
    Get detailed media information from TMDb API.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    media_type : str
        Type of media (movie or tv).
    tmdb_id : int
        TMDb ID of the media.

    Returns
    -------
    JsonResponse
        JSON response with detailed media information.
    """
    tmdb_service = TMDbService()

    try:
        if media_type == 'movie':
            # Get movie details
            details = tmdb_service.get_movie_details(tmdb_id)

            # Get credits
            credits = tmdb_service.get_movie_credits(tmdb_id)

            # Extract directors
            directors = [
                crew['name']
                for crew in credits.get('crew', [])
                if crew.get('job') == 'Director'
            ][:2]

            # Extract cast
            cast = [
                {
                    'name': person.get('name'),
                    'character': person.get('character'),
                    'profile_path': person.get('profile_path')
                }
                for person in credits.get('cast', [])
            ][:10]

            # Get TMDb external IDs
            external_ids = tmdb_service._make_request(f'/movie/{tmdb_id}/external_ids')
            imdb_id = external_ids.get('imdb_id')

            return JsonResponse({
                'id': details.get('id'),
                'title': details.get('title'),
                'overview': details.get('overview'),
                'backdrop_path': details.get('backdrop_path'),
                'poster_path': details.get('poster_path'),
                'vote_average': details.get('vote_average'),
                'release_date': details.get('release_date'),
                'runtime': details.get('runtime'),
                'genres': details.get('genres', []),
                'production_companies': details.get('production_companies', []),
                'budget': details.get('budget'),
                'revenue': details.get('revenue'),
                'directors': directors,
                'cast': cast,
                'imdb_id': imdb_id,
                'media_type': 'movie'
            })
        else:  # tv
            # Get TV details
            details = tmdb_service.get_tv_details(tmdb_id)

            # Get credits
            credits = tmdb_service.get_tv_credits(tmdb_id)

            # Extract creators/directors
            directors = [creator.get('name') for creator in details.get('created_by', [])][:2]

            # Extract cast
            cast = [
                {
                    'name': person.get('name'),
                    'character': person.get('character'),
                    'profile_path': person.get('profile_path')
                }
                for person in credits.get('cast', [])
            ][:10]

            # Get TMDb external IDs
            external_ids = tmdb_service._make_request(f'/tv/{tmdb_id}/external_ids')
            imdb_id = external_ids.get('imdb_id')

            return JsonResponse({
                'id': details.get('id'),
                'name': details.get('name'),
                'title': details.get('name'),  # Alias for consistency
                'overview': details.get('overview'),
                'backdrop_path': details.get('backdrop_path'),
                'poster_path': details.get('poster_path'),
                'vote_average': details.get('vote_average'),
                'first_air_date': details.get('first_air_date'),
                'genres': details.get('genres', []),
                'production_companies': details.get('production_companies', []),
                'number_of_seasons': details.get('number_of_seasons'),
                'number_of_episodes': details.get('number_of_episodes'),
                'directors': directors,
                'cast': cast,
                'imdb_id': imdb_id,
                'media_type': 'tv'
            })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
