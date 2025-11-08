const express = require('express');
const router = express.Router();
const Opportunity = require('../models/Opportunity');
const auth = require('../middleware/auth');

// Get all opportunities
router.get('/', async (req, res) => {
  try {
    const { type } = req.query;
    let query = { isActive: true };
    
    if (type && type !== 'All') {
      query.type = type.toUpperCase();
    }

    const opportunities = await Opportunity.find(query)
      .sort({ deadline: 1 });
    
    res.json(opportunities);
  } catch (error) {
    console.error('Error fetching opportunities:', error);
    res.status(500).json({ message: 'Error fetching opportunities' });
  }
});

// Apply to opportunity
router.post('/:id/apply', auth, async (req, res) => {
  try {
    const opportunity = await Opportunity.findById(req.params.id);
    if (!opportunity) {
      return res.status(404).json({ message: 'Opportunity not found' });
    }

    const alreadyApplied = opportunity.applications.some(
      app => app.user.toString() === req.userId
    );

    if (alreadyApplied) {
      return res.status(400).json({ message: 'Already applied to this opportunity' });
    }

    opportunity.applications.push({
      user: req.userId,
      coverLetter: req.body.coverLetter
    });
    await opportunity.save();

    res.json({ message: 'Application submitted successfully' });
  } catch (error) {
    console.error('Application error:', error);
    res.status(500).json({ message: 'Error submitting application' });
  }
});

module.exports = router;
