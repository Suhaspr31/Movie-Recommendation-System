import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';
import { movieService } from '../services/movieService';
import { authService } from '../services/authService';
import { toast } from 'react-toastify';
import { FaUser, FaStar, FaFilm, FaSave, FaEdit } from 'react-icons/fa';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user, login } = useAuth();
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingGenres, setEditingGenres] = useState(false);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [stats, setStats] = useState({
    totalRatings: 0,
    averageRating: 0,
    favoriteGenre: 'N/A'
  });

  const availableGenres = [
    'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical',
    'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
  ];

   const calculateStats = useCallback((ratingsData) => {
     if (ratingsData.length === 0) {
       return;
     }

     const totalRatings = ratingsData.length;
     const sumRatings = ratingsData.reduce((sum, r) => sum + r.rating, 0);
     const averageRating = (sumRatings / totalRatings).toFixed(1);

     // Calculate favorite genre (most common genre in rated movies)
     const genreCounts = {};
     ratingsData.forEach(rating => {
       if (rating.movie?.genres) {
         rating.movie.genres.forEach(genre => {
           genreCounts[genre] = (genreCounts[genre] || 0) + 1;
         });
       }
     });

     const favoriteGenre = Object.keys(genreCounts).length > 0
       ? Object.keys(genreCounts).reduce((a, b) =>
           genreCounts[a] > genreCounts[b] ? a : b
         )
       : 'N/A';

     setStats({
       totalRatings,
       averageRating,
       favoriteGenre
     });
   }, []);


  const fetchUserRatings = useCallback(async () => {
    try {
      setLoading(true);
      const response = await movieService.getUserRatings();
      setRatings(response.ratings || []);
      calculateStats(response.ratings || []);
    } catch (error) {
      toast.error('Failed to load rating history');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [calculateStats]);

  const handleGenreToggle = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre)
        ? prev.filter(g => g !== genre)
        : [...prev, genre]
    );
  };

  const handleSaveGenres = async () => {
    try {
      const response = await authService.updatePreferences({ favoriteGenres: selectedGenres });
      if (response.success) {
        toast.success('Genre preferences updated!');
        setEditingGenres(false);
        // Update the user context
        login(user.email, 'dummy'); // This will refresh user data
      } else {
        toast.error('Failed to update preferences');
      }
    } catch (error) {
      toast.error('Failed to save preferences');
      console.error(error);
    }
  };

  useEffect(() => {
    fetchUserRatings();
    // Initialize selected genres from user preferences
    if (user?.preferences?.favoriteGenres) {
      setSelectedGenres(user.preferences.favoriteGenres);
    }
  }, [fetchUserRatings, user]);


  return (
    <div className="profile-page">
      <div className="container">
        <div className="profile-header">
          <div className="profile-avatar">
            <FaUser />
          </div>
          <div className="profile-info">
            <h1>{user?.username || 'User'}</h1>
            <p>{user?.email}</p>
          </div>
        </div>

        <div className="profile-stats">
          <div className="stat-card">
            <FaFilm className="stat-icon" />
            <div className="stat-info">
              <h3>{stats.totalRatings}</h3>
              <p>Movies Rated</p>
            </div>
          </div>

          <div className="stat-card">
            <FaStar className="stat-icon" />
            <div className="stat-info">
              <h3>{stats.averageRating}</h3>
              <p>Average Rating</p>
            </div>
          </div>

          <div className="stat-card">
            <FaFilm className="stat-icon" />
            <div className="stat-info">
              <h3>{stats.favoriteGenre}</h3>
              <p>Favorite Genre</p>
            </div>
          </div>
        </div>

        <div className="genre-preferences">
          <div className="preferences-header">
            <h2>Favorite Genres</h2>
            {!editingGenres ? (
              <button
                onClick={() => setEditingGenres(true)}
                className="btn btn-secondary btn-sm"
              >
                <FaEdit /> Edit
              </button>
            ) : (
              <div className="edit-actions">
                <button
                  onClick={() => {
                    setEditingGenres(false);
                    setSelectedGenres(user?.preferences?.favoriteGenres || []);
                  }}
                  className="btn btn-secondary btn-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveGenres}
                  className="btn btn-primary btn-sm"
                >
                  <FaSave /> Save
                </button>
              </div>
            )}
          </div>

          {!editingGenres ? (
            <div className="genres-display">
              {selectedGenres.length > 0 ? (
                <div className="selected-genres">
                  {selectedGenres.map(genre => (
                    <span key={genre} className="genre-tag">{genre}</span>
                  ))}
                </div>
              ) : (
                <p className="no-genres">No favorite genres set. Click edit to add your preferences!</p>
              )}
            </div>
          ) : (
            <div className="genres-editor">
              <p>Select your favorite genres to get better recommendations:</p>
              <div className="genres-grid">
                {availableGenres.map(genre => (
                  <label key={genre} className="genre-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedGenres.includes(genre)}
                      onChange={() => handleGenreToggle(genre)}
                    />
                    <span className="genre-label">{genre}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="rating-history">
          <h2>Rating History</h2>
          
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
            </div>
          ) : ratings.length === 0 ? (
            <div className="empty-state">
              <p>No ratings yet. Start rating movies to see your history!</p>
            </div>
          ) : (
            <div className="ratings-list">
              {ratings.slice(0, 20).map((rating) => (
                <div key={rating._id} className="rating-item">
                  <div className="rating-movie-info">
                    <h4>{rating.movie?.title || 'Unknown Movie'}</h4>
                    <p className="rating-date">
                      {new Date(rating.ratedAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="rating-score">
                    <FaStar className="star-icon" />
                    <span>{rating.rating.toFixed(1)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
