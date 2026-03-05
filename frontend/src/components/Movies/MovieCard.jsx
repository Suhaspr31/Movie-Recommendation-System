import React, { useState, useContext } from 'react';
import { FaStar } from 'react-icons/fa';
import RatingModal from '../Recommendations/RatingModal';
import { AuthContext } from '../../context/AuthContext.js';
import './MovieCard.css';

const MovieCard = ({ movie, onRatingSubmit }) => {
  const [showRatingModal, setShowRatingModal] = useState(false);
  const { user } = useContext(AuthContext);

  const handleRateClick = () => {
    setShowRatingModal(true);
  };

  const handleRatingSubmit = (rating) => {
    onRatingSubmit(movie._id, rating);
    setShowRatingModal(false);
  };

  return (
    <>
      <div className="movie-card">
        <div className="movie-poster">
          {movie.posterUrl ? (
            <img src={movie.posterUrl} alt={movie.title} />
          ) : (
            <div className="movie-poster-placeholder">
              <FaStar />
            </div>
          )}
          <div className="movie-overlay">
            {user && (
              <button onClick={handleRateClick} className="btn btn-primary">
                Rate Movie
              </button>
            )}
          </div>
        </div>
        
        <div className="movie-info">
          <h3 className="movie-title">{movie.title}</h3>
          <div className="movie-details">
            <span className="movie-year">{movie.releaseYear || 'N/A'}</span>
            <span className="movie-rating">
              <FaStar className="star-icon" />
              {movie.averageRating ? movie.averageRating.toFixed(1) : 'N/A'}
            </span>
          </div>
          <div className="movie-genres">
            {movie.genres && movie.genres.slice(0, 3).map((genre, index) => (
              <span key={index} className="genre-tag">{genre}</span>
            ))}
          </div>
        </div>
      </div>

      {showRatingModal && (
        <RatingModal
          movie={movie}
          onClose={() => setShowRatingModal(false)}
          onSubmit={handleRatingSubmit}
        />
      )}
    </>
  );
};

export default MovieCard;
