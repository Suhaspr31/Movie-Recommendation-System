import React, { useState } from 'react';
import { FaStar, FaTimes } from 'react-icons/fa';
import './RatingModal.css';

const RatingModal = ({ movie, onClose, onSubmit }) => {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);

  const handleSubmit = () => {
    if (rating > 0) {
      onSubmit(rating);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <FaTimes />
        </button>

        <h3>Rate Movie</h3>
        <p className="modal-movie-title">{movie.title}</p>

        <div className="rating-stars">
          {[...Array(10)].map((_, index) => {
            const ratingValue = (index + 1) * 0.5;
            return (
              <FaStar
                key={index}
                className={`star ${ratingValue <= (hover || rating) ? 'active' : ''}`}
                onClick={() => setRating(ratingValue)}
                onMouseEnter={() => setHover(ratingValue)}
                onMouseLeave={() => setHover(0)}
              />
            );
          })}
        </div>

        <p className="rating-value">
          {rating > 0 ? `${rating.toFixed(1)} / 5.0` : 'Select a rating'}
        </p>

        <button
          className="btn btn-primary btn-block"
          onClick={handleSubmit}
          disabled={rating === 0}
        >
          Submit Rating
        </button>
      </div>
    </div>
  );
};

export default RatingModal;
