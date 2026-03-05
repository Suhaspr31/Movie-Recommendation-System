const express = require('express');
const auth = require('../middleware/auth');
const { getRecommendations, addRating, getUserRatings, optionalAuth } = require('../controllers/recommendationController');

const router = express.Router();

router.get('/recommend', auth, getRecommendations);
router.post('/rate', auth, addRating);
router.get('/history', auth, getUserRatings);

module.exports = router;
