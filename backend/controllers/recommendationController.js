const axios = require('axios');
const Rating = require('../models/Rating');
const User = require('../models/User');


const getRecommendations = async (req, res) => {
  try {
    const userId = req.userId || null;
    const { limit = 10, genres } = req.query;

    const Movie = require('../models/Movie');
    const Rating = require('../models/Rating');

    let userGenres = [];
    if (genres) {
      userGenres = genres.split(',').map(g => g.trim()).filter(g => g);
    } else if (userId) {
      const user = await User.findById(userId);
      if (user && user.preferences) {
        userGenres = user.preferences.favoriteGenres || user.preferences.genres || [];
      }
    }

    let searchParams = {
      limit: parseInt(limit) * 4 // Get more for filtering
    };

    // PERSONALIZATION LOGIC:
    // If user is logged in, find their ratings and use them to find similar movies
    if (userId) {
      console.log(`[DEBUG] Fetching ratings for user ${userId}`);
      const userRatings = await Rating.find({ userId }).populate('movieId');
      console.log(`[DEBUG] Found ${userRatings.length} total ratings`);

      if (userRatings.length > 0) {
        // Find movies they liked (rating >= 3.5)
        const likedMovies = userRatings.filter(r => r.rating >= 3.5 && r.movieId);
        console.log(`[DEBUG] User has ${likedMovies.length} liked movies (>= 3.5 stars)`);

        if (likedMovies.length > 0) {
          // Send the externalIds of movies the user likes to the Python engine
          // The Python engine will use these to find a representative feature vector
          const likedMovieIds = likedMovies.map(r => r.movieId.externalId).filter(id => id);
          searchParams.likedMovieIds = likedMovieIds;

          console.log(`[DEBUG] Sending ${likedMovieIds.length} movie IDs for personalization:`, likedMovieIds.slice(0, 5));
        }
      }
    }

    // Default to modelUserId 1 if no history (fallback)
    if (!searchParams.likedMovieIds) {
      searchParams.userId = 1;
    }

    // Call Python API
    const response = await axios.post(
      `${process.env.PYSPARK_API_URL}/recommend`,
      searchParams
    );

    const { recommendations } = response.data;

    // Enrich recommendations
    const enrichedRecommendations = await Promise.all(
      recommendations.map(async (rec) => {
        const movie = await Movie.findOne({ externalId: rec.movieId.toString() });
        if (movie) {
          return {
            ...movie.toObject(),
            predictedRating: rec.predictedRating
          };
        }
        return null;
      })
    );

    let validRecommendations = enrichedRecommendations.filter(rec => rec !== null);

    // Filter by genre if requested
    if (userGenres.length > 0) {
      validRecommendations = validRecommendations.filter(rec =>
        rec.genres.some(genre => userGenres.includes(genre))
      );
    }

    // Limit and return
    res.json({
      recommendations: validRecommendations.slice(0, parseInt(limit)),
      userGenres: userGenres,
      message: validRecommendations.length > 0 ? 'Recommendations generated' : 'No recommendations available'
    });
  } catch (error) {
    console.error('--- RECOMMENDATION SYSTEM ERROR ---');
    console.error('Message:', error.message);
    if (error.response) {
      console.error('ML Engine Response Error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('No response received from ML Engine. Check PYSPARK_API_URL or service status.');
    }
    console.error('--- END ERROR ---');
    res.status(500).json({ message: 'Recommendation Engine is currently unavailable. Please try again in 1 minute.' });
  }
};

const addRating = async (req, res) => {
  try {
    const { movieId, rating } = req.body;

    let ratingDoc = await Rating.findOne({ userId: req.userId, movieId });

    if (ratingDoc) {
      ratingDoc.rating = rating;
      ratingDoc.ratedAt = new Date();
    } else {
      ratingDoc = new Rating({
        userId: req.userId,
        movieId,
        rating,
        ratedAt: new Date()
      });
    }

    await ratingDoc.save();
    res.json({ message: 'Rating saved', ratingDoc });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

const getUserRatings = async (req, res) => {
  try {
    const userId = req.userId;

    const ratings = await Rating.find({ userId })
      .populate('movieId', 'title genres releaseYear posterUrl')
      .sort({ ratedAt: -1 });

    // Transform to match frontend expectations
    const transformedRatings = ratings.map(rating => ({
      _id: rating._id,
      rating: rating.rating,
      ratedAt: rating.ratedAt,
      movie: rating.movieId
    }));

    res.json({ ratings: transformedRatings });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

module.exports = { getRecommendations, addRating, getUserRatings };
