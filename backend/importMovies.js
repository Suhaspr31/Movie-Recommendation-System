const mongoose = require('mongoose');
const fs = require('fs');
const csv = require('csv-parser');
require('dotenv').config();

const Movie = require('./models/Movie');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('MongoDB connected');
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};

const importMovies = async () => {
  await connectDB();

  const movies = [];

  fs.createReadStream('../data-processing/datasets/movies.csv')
    .pipe(csv())
    .on('data', (row) => {
      // Parse title to extract year
      const titleMatch = row.title.match(/(.+)\s+\((\d{4})\)$/);
      let title = row.title;
      let releaseYear = null;
      if (titleMatch) {
        title = titleMatch[1];
        releaseYear = parseInt(titleMatch[2]);
      }

      const genres = row.genres.split('|').filter(g => g !== '(no genres listed)');

      movies.push({
        title: title.trim(),
        genres,
        releaseYear,
        externalId: row.movieId
      });
    })
    .on('end', async () => {
      try {
        await Movie.insertMany(movies);
        console.log(`Imported ${movies.length} movies`);
        process.exit(0);
      } catch (error) {
        console.error('Error importing movies:', error);
        process.exit(1);
      }
    });
};

importMovies();