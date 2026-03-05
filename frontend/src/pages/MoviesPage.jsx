import React, { useState, useEffect, useCallback } from 'react';
import { movieService } from '../services/movieService';
import { toast } from 'react-toastify';
import MovieGrid from '../components/Movies/MovieGrid';
import { FaSearch, FaFilter } from 'react-icons/fa';
import './MoviesPage.css';

const MoviesPage = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');

  const genres = [
    'All', 'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Family', 'Fantasy', 'Horror',
    'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
  ];

  const fetchMovies = useCallback(async () => {
    try {
      setLoading(true);
      const genre = selectedGenre === 'All' ? '' : selectedGenre;
      const response = await movieService.getMovies(page, 20, genre);
      setMovies(response.movies);
      setTotalPages(response.totalPages);
    } catch (error) {
      toast.error('Failed to load movies');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [selectedGenre, page]);

  useEffect(() => {
    fetchMovies();
  }, [page, selectedGenre, fetchMovies]);

  const handleRating = async (movieId, rating) => {
    try {
      await movieService.rateMovie(movieId, rating);
      toast.success(`Movie rated ${rating} stars!`);
    } catch (error) {
      toast.error('Failed to submit rating');
      console.error(error);
    }
  };

  const handleGenreChange = (genre) => {
    setSelectedGenre(genre);
    setPage(1);
  };

  const filteredMovies = movies.filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="movies-page">
      <div className="container">
        <div className="page-header">
          <h1>Browse Movies</h1>
          <p className="page-subtitle">
            Explore our collection of {movies.length}+ movies
          </p>
        </div>

        <div className="movies-controls">
          <div className="search-box">
            <FaSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search movies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="genre-filter">
            <FaFilter className="filter-icon" />
            <select
              value={selectedGenre}
              onChange={(e) => handleGenreChange(e.target.value)}
            >
              {genres.map((genre) => (
                <option key={genre} value={genre}>
                  {genre}
                </option>
              ))}
            </select>
          </div>
        </div>

        <MovieGrid
          movies={filteredMovies}
          onRatingSubmit={handleRating}
          loading={loading}
        />

        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn btn-secondary"
            >
              Previous
            </button>
            <span className="page-info">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="btn btn-secondary"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MoviesPage;
