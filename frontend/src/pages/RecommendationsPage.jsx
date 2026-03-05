import React, { useState, useEffect, useCallback } from 'react';
import { movieService } from '../services/movieService';
import { useAuth } from '../hooks/useAuth';
import { toast } from 'react-toastify';
import RecommendationList from '../components/Recommendations/RecommendationList';
import { FaRedo, FaInfoCircle, FaFilter } from 'react-icons/fa';
import './RecommendationsPage.css';

const RecommendationsPage = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(10);
  const [userGenres, setUserGenres] = useState([]);

  const fetchRecommendations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await movieService.getRecommendations(limit, userGenres);
      setRecommendations(response.recommendations || []);

      if (response.recommendations && response.recommendations.length > 0) {
        const genreText = userGenres.length > 0 ? ` based on your favorite genres (${userGenres.join(', ')})` : '';
        toast.success(`Generated ${response.recommendations.length} recommendations${genreText}!`);
      }
    } catch (error) {
      if (error.response?.status === 400) {
        toast.error('Please rate at least 5 movies to get recommendations');
      } else {
        toast.error('Failed to load recommendations');
      }
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [limit, userGenres]);

  useEffect(() => {
    // Set user genres from profile
    if (user?.preferences?.favoriteGenres) {
      setUserGenres(user.preferences.favoriteGenres);
    } else {
      setUserGenres([]);
    }
  }, [user]);

  useEffect(() => {
    if (userGenres.length >= 0) { // Allow empty array
      fetchRecommendations();
    }
  }, [fetchRecommendations]);

  const handleRefresh = () => {
    fetchRecommendations();
  };

  const handleLimitChange = (e) => {
    setLimit(parseInt(e.target.value));
  };

  return (
    <div className="recommendations-page">
      <div className="container">
        <div className="page-header">
          <h1>Your Recommendations</h1>
          <p className="page-subtitle">
            Personalized movie suggestions based on your ratings
          </p>
        </div>

        <div className="recommendations-controls">
          <div className="info-box">
            <FaInfoCircle />
            <span>
              Our ML algorithm analyzes your ratings to find movies you'll love
            </span>
          </div>

          {userGenres.length > 0 && (
            <div className="genre-filter-info">
              <FaFilter />
              <span>
                Filtering recommendations for your favorite genres:
                <div className="active-genres">
                  {userGenres.map(genre => (
                    <span key={genre} className="genre-tag">{genre}</span>
                  ))}
                </div>
              </span>
            </div>
          )}

          <div className="control-actions">
            <div className="limit-selector">
              <label htmlFor="limit">Show:</label>
              <select
                id="limit"
                value={limit}
                onChange={handleLimitChange}
              >
                <option value="5">5 movies</option>
                <option value="10">10 movies</option>
                <option value="15">15 movies</option>
                <option value="20">20 movies</option>
              </select>
            </div>

            <button
              onClick={handleRefresh}
              className="btn btn-primary"
              disabled={loading}
            >
              <FaRedo /> Refresh
            </button>
          </div>
        </div>

        <RecommendationList
          recommendations={recommendations}
          loading={loading}
        />
      </div>
    </div>
  );
};

export default RecommendationsPage;
