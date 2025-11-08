const mongoose = require('mongoose');

const mentorshipSchema = new mongoose.Schema({
  mentor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  mentee: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'active', 'completed', 'cancelled'],
    default: 'pending'
  },
  specialties: [String],
  bio: String,
  yearsExperience: Number,
  availableSlots: {
    type: Number,
    default: 5
  },
  sessions: [{
    title: String,
    scheduledDate: Date,
    duration: Number,
    notes: String,
    completed: {
      type: Boolean,
      default: false
    },
    feedback: String
  }],
  messages: [{
    sender: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    content: String,
    timestamp: {
      type: Date,
      default: Date.now
    }
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Mentorship', mentorshipSchema);

