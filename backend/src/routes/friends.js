/**
 * Friends Management Routes
 * Base URL: /api/v1/friends
 * Auth needed: Yes
 */

const router = require('express').Router();

/**
 * POST /friends/request/:userId
 * Send a friend request
 * Auth needed: Yes
 */
router.post('/request/:userId', (req, res) => {
  // TODO: Implement send friend request logic
});

/**
 * POST /friends/accept/:userId
 * Accept a friend request
 * Auth needed: Yes
 */
router.post('/accept/:userId', (req, res) => {
  // TODO: Implement accept friend request logic
});

module.exports = router;
