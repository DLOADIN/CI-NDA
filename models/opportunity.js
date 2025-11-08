const mongoose = require('mongoose');

const opportunitySchema = new mongoose.Schema({
  type: {
    type: String,
    required: true,
    enum: ['GRANT', 'JOB', 'COMPETITION', 'COLLABORATION', 'INTERNSHIP']
  },
  title: {
    type: String,
    required: true
  },
  company: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  details: {
    funding: String,
    location: String,
    duration: String,
    category: String
  },
  deadline: {
    type: Date,
    required: true
  },
  applications: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    status: {
      type: String,
      enum: ['pending', 'accepted', 'rejected'],
      default: 'pending'
    },
    coverLetter: String,
    appliedAt: {
      type: Date,
      default: Date.now
    }
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Opportunity', opportunitySchema);
