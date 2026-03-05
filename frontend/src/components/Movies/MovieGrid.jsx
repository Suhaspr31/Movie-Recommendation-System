import React from 'react';
import MovieCard from './MovieCard';
import './MovieGrid.css';

const MovieGrid = ({ movies, onRatingSubmit, loading }) => {
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!movies || movies.length === 0) {
    return (
      <div className="empty-state">
        <p>No movies found</p>
      </div>
    );
  }

  return (
    <div className="movie-grid">
      {movies.map((movie) => (
        <MovieCard
          key={movie._id}
          movie={movie}
          onRatingSubmit={onRatingSubmit}
        />
      ))}
    </div>
  );
};

export default MovieGrid;
