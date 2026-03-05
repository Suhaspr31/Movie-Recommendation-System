import React from 'react';
import { FaStar } from 'react-icons/fa';
import './RecommendationList.css';

const RecommendationList = ({ recommendations, loading }) => {
  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Generating personalized recommendations...</p>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="empty-state">
        <FaStar className="empty-icon" />
        <p>No recommendations yet</p>
        <p className="empty-subtitle">Rate some movies to get personalized recommendations!</p>
      </div>
    );
  }

  return (
    <div className="recommendation-list">
      <h2 className="recommendation-header">
        <FaStar className="header-icon" />
        Your Personalized Recommendations
      </h2>
      
      <div className="recommendation-grid">
        {recommendations.map((rec, index) => (
          <div key={rec.movieId || index} className="recommendation-card">
            <div className="recommendation-rank">#{index + 1}</div>
            
            <div className="recommendation-poster">
              {rec.posterUrl ? (
                <img src={rec.posterUrl} alt={rec.title} />
              ) : (
                <div className="recommendation-poster-placeholder">
                  <FaStar />
                </div>
              )}
            </div>

            <div className="recommendation-info">
              <h3>{rec.title}</h3>
              
              <div className="prediction-score">
                <span className="score-label">Predicted Rating:</span>
                <span className="score-value">
                  <FaStar /> {rec.predictedRating?.toFixed(1) || 'N/A'} / 5.0
                </span>
              </div>

              {rec.genres && rec.genres.length > 0 && (
                <div className="recommendation-genres">
                  {rec.genres.slice(0, 3).map((genre, idx) => (
                    <span key={idx} className="genre-tag">{genre}</span>
                  ))}
                </div>
              )}

              {rec.releaseYear && (
                <p className="recommendation-year">{rec.releaseYear}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationList;
