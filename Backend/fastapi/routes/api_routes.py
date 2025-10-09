from fastapi import Request, Query, HTTPException
from Backend import db

# --- API Routes for Media Management ---

async def list_media_api(
    media_type: str = Query("movie", regex="^(movie|tv)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    search: str = Query("", max_length=100)
):
    try:
        if search:
            result = await db.search_documents(search, page, page_size)
            filtered_results = [item for item in result['results'] if item.get('media_type') == media_type]
            total_filtered = len(filtered_results)
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paged_results = filtered_results[start_index:end_index]
            
            return {
                "total_count": total_filtered,
                "current_page": page,
                "total_pages": (total_filtered + page_size - 1) // page_size,
                "movies" if media_type == "movie" else "tv_shows": paged_results
            }
        else:
            if media_type == "movie":
                return await db.sort_movies([], page, page_size)
            else:
                return await db.sort_tv_shows([], page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_media_api(
    tmdb_id: int,
    db_index: int,
    media_type: str = Query(regex="^(movie|tv)$")
):
    try:
        media_type_formatted = "Movie" if media_type == "movie" else "Series"
        result = await db.delete_document(media_type_formatted, tmdb_id, db_index)
        if result:
            return {"message": "Media deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Media not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_media_api(
    request: Request,
    tmdb_id: int,
    db_index: int,
    media_type: str = Query(regex="^(movie|tv)$")
):
    try:
        update_data = await request.json()
        if 'rating' in update_data and update_data['rating']:
            try:
                update_data['rating'] = float(update_data['rating'])
            except (ValueError, TypeError):
                update_data['rating'] = 0.0
        
        if 'release_year' in update_data and update_data['release_year']:
            try:
                update_data['release_year'] = int(update_data['release_year'])
            except (ValueError, TypeError):
                pass
        if 'genres' in update_data:
            if isinstance(update_data['genres'], str):
                update_data['genres'] = [g.strip() for g in update_data['genres'].split(',') if g.strip()]
            elif not isinstance(update_data['genres'], list):
                update_data['genres'] = []
        
        if 'languages' in update_data:
            if isinstance(update_data['languages'], str):
                update_data['languages'] = [l.strip() for l in update_data['languages'].split(',') if l.strip()]
            elif not isinstance(update_data['languages'], list):
                update_data['languages'] = []
        if media_type == "movie":
            if 'runtime' in update_data and update_data['runtime']:
                try:
                    update_data['runtime'] = int(update_data['runtime'])
                except (ValueError, TypeError):
                    pass
        elif media_type == "tv":
            if 'total_seasons' in update_data and update_data['total_seasons']:
                try:
                    update_data['total_seasons'] = int(update_data['total_seasons'])
                except (ValueError, TypeError):
                    pass
            
            if 'total_episodes' in update_data and update_data['total_episodes']:
                try:
                    update_data['total_episodes'] = int(update_data['total_episodes'])
                except (ValueError, TypeError):
                    pass
        update_data = {k: v for k, v in update_data.items() if v != ""}
        result = await db.update_document(media_type, tmdb_id, db_index, update_data)
        if result:
            return {"message": "Media updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Media not found or no changes made")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_media_details_api(
    tmdb_id: int,
    db_index: int,
    media_type: str = Query(regex="^(movie|tv)$")
):
    try:
        result = await db.get_document(media_type, tmdb_id, db_index)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Media not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_movie_quality_api(tmdb_id: int, db_index: int, quality: str):
    try:
        result = await db.delete_movie_quality(tmdb_id, db_index, quality)
        if result:
            return {"message": "Quality deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Quality not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_tv_quality_api(
    tmdb_id: int, db_index: int, season: int, episode: int, quality: str
):
    try:
        result = await db.delete_tv_quality(tmdb_id, db_index, season, episode, quality)
        if result:
            return {"message": "Quality deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Quality not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_tv_episode_api(
    tmdb_id: int, db_index: int, season: int, episode: int
):
    try:
        result = await db.delete_tv_episode(tmdb_id, db_index, season, episode)
        if result:
            return {"message": "Episode deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Episode not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_tv_season_api(tmdb_id: int, db_index: int, season: int):
    try:
        result = await db.delete_tv_season(tmdb_id, db_index, season)
        if result:
            return {"message": "Season deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Season not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
