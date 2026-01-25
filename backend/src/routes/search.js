/**
 * Global Search Routes
 * Base URL: /api/v1/search
 * Auth needed: Yes
 */

const router = require('express').Router();

/**
 * GET /search
 * Search for events or users
 * Auth needed: Yes
 * Query params: ?q={query}&type={events|users|all}
 * 
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "users": [...],
 *     "events": [...]
 *   }
 * }
 */
router.get('/', (req, res) => {
  // TODO: Implement global search logic
});

module.exports = router;
