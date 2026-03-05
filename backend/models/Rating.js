const mongoose = require('mongoose');

const ratingSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  movieId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Movie',
    required: true
  },
  rating: {
    type: Number,
    required: true,
    min: 0.5,
    max: 5,
    validate: {
      validator: function(v) {
        return v % 0.5 === 0;
      }
    }
  },
  ratedAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Rating', ratingSchema);
