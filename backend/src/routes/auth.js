/**
 * Authentication Routes
 * Base URL: /api/v1/auth
 */

const router = require('express').Router();

/**
 * POST /auth/register
 * Create a new account
 * Auth needed: No
 * 
 * Request body:
 * {
 *   "email": "john.doe@example.com",
 *   "password": "Password123!",
 *   "username": "JohnDoe",
 *   "city": "Paris"
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "userId": "usr_123456",
 *     "username": "JohnDoe",
 *     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
 *   }
 * }
 */
router.post('/register', (req, res) => {
  // TODO: Implement registration logic
});

/**
 * POST /auth/login
 * Login to an existing account
 * Auth needed: No
 * 
 * Request body:
 * {
 *   "email": "john.doe@example.com",
 *   "password": "Password123!"
 * }
 * 
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "userId": "usr_123456",
 *     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
 *   }
 * }
 */
router.post('/login', (req, res) => {
  // TODO: Implement login logic
});

module.exports = router;
