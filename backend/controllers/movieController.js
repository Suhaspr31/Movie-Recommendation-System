const Movie = require('../models/Movie');

const getAllMovies = async (req, res) => {
  try {
    const { page = 1, limit = 20, genre } = req.query;

    let query = {};
    if (genre) {
      query.genres = { $in: [genre] };
    }

    const movies = await Movie.find(query)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .exec();

    const total = await Movie.countDocuments(query);

    res.json({
      movies,
      totalPages: Math.ceil(total / limit),
      currentPage: page
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

const getMovieById = async (req, res) => {
  try {
    const movie = await Movie.findById(req.params.id);
    if (!movie) return res.status(404).json({ message: 'Movie not found' });
    
    res.json(movie);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

module.exports = { getAllMovies, getMovieById };
