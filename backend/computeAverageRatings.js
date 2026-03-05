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

const computeAverageRatings = async () => {
  await connectDB();

  const ratingsMap = {};

  // Read ratings.csv and accumulate ratings
  fs.createReadStream('../data-processing/datasets/ratings.csv')
    .pipe(csv())
    .on('data', (row) => {
      const movieId = row.movieId;
      const rating = parseFloat(row.rating);

      if (!ratingsMap[movieId]) {
        ratingsMap[movieId] = { sum: 0, count: 0 };
      }
      ratingsMap[movieId].sum += rating;
      ratingsMap[movieId].count += 1;
    })
    .on('end', async () => {
      console.log('Finished reading ratings.csv');

      const updates = [];
      for (const [movieId, data] of Object.entries(ratingsMap)) {
        const averageRating = data.sum / data.count;
        updates.push({
          updateOne: {
            filter: { externalId: movieId },
            update: { averageRating: averageRating, totalRatings: data.count }
          }
        });
      }

      try {
        const result = await Movie.bulkWrite(updates);
        console.log(`Updated ${result.modifiedCount} movies with average ratings`);
        process.exit(0);
      } catch (error) {
        console.error('Error updating movies:', error);
        process.exit(1);
      }
    });
};

computeAverageRatings();