/**
 * Publications/Actions Routes (Posts)
 * Base URL: /api/v1/posts
 * Auth needed: Yes
 */

const router = require('express').Router();

/**
 * POST /posts
 * Create a post
 * Auth needed: Yes
 * 
 * Request body:
 * {
 *   "content": "Post content here",
 *   "image": "optional image URL"
 * }
 */
router.post('/', (req, res) => {
  // TODO: Implement create post logic
});

/**
 * DELETE /posts/:postId
 * Delete a post
 * Auth needed: Yes (only post creator)
 */
router.delete('/:postId', (req, res) => {
  // TODO: Implement delete post logic
});

module.exports = router;
