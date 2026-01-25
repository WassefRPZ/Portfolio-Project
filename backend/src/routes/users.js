/**
 * User Profile Routes
 * Base URL: /api/v1/users
 * Auth needed: Yes (for most endpoints)
 */

const router = require('express').Router();

/**
 * GET /users/me
 * See your profile
 * Auth needed: Yes
 */
router.get('/me', (req, res) => {
  // TODO: Implement get profile logic
});

/**
 * PUT /users/me
 * Update your profile
 * Auth needed: Yes
 */
router.put('/me', (req, res) => {
  // TODO: Implement update profile logic
});

/**
 * GET /users/search
 * Search other players
 * Auth needed: Yes
 * Query params: ?city={city}&username={username}
 */
router.get('/search', (req, res) => {
  // TODO: Implement search players logic
});

/**
 * POST /users/me/favorite-games
 * Add a favorite game to profile
 * Auth needed: Yes
 */
router.post('/me/favorite-games', (req, res) => {
  // TODO: Implement add favorite game logic
});

/**
 * DELETE /users/me/favorite-games/:gameId
 * Remove a favorite game from profile
 * Auth needed: Yes
 */
router.delete('/me/favorite-games/:gameId', (req, res) => {
  // TODO: Implement remove favorite game logic
});

module.exports = router;
