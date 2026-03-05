import api from './api';

export const movieService = {
  // Get all movies with pagination
  getMovies: async (page = 1, limit = 20, genre = '') => {
    const params = { page, limit };
    if (genre) params.genre = genre;

    const response = await api.get('/movies', { params });
    return response.data;
  },

  // Get single movie by ID
  getMovieById: async (id) => {
    const response = await api.get(`/movies/${id}`);
    return response.data;
  },

  // Rate a movie
  rateMovie: async (movieId, rating) => {
    const response = await api.post('/recommendations/rate', {
      movieId,
      rating
    });
    return response.data;
  },

  // Get recommendations
  getRecommendations: async (limit = 10, genres = []) => {
    const params = { limit };
    if (genres && genres.length > 0) {
      params.genres = genres.join(',');
    }

    const response = await api.get('/recommendations/recommend', { params });
    return response.data;
  },

  // Get user's rating history
  getUserRatings: async () => {
    const response = await api.get('/recommendations/history');
    return response.data;
  }
};
