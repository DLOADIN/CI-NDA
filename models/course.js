const mongoose = require('mongoose');

const courseSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  category: {
    type: String,
    required: true,
    enum: ['CINEMATOGRAPHY', 'EDITING', 'DIRECTING', 'SOUND DESIGN', 'SCREENWRITING', 'LIGHTING', 'PRODUCTION DESIGN', 'COLOR GRADING', 'DOCUMENTARY']
  },
  instructor: {
    name: { type: String, required: true },
    avatar: String,
    bio: String
  },
  description: {
    type: String,
    required: true
  },
  image: String,
  duration: String,
  level: {
    type: String,
    enum: ['Beginner', 'Intermediate', 'Advanced'],
    required: true
  },
  price: {
    type: Number,
    default: 0
  },
  enrolledStudents: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    enrolledAt: {
      type: Date,
      default: Date.now
    },
    progress: {
      type: Number,
      default: 0
    }
  }],
  lessons: [{
    title: String,
    videoUrl: String,
    duration: Number,
    resources: [String],
    order: Number
  }],
  ratings: {
    average: { type: Number, default: 0 },
    count: { type: Number, default: 0 }
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Course', courseSchema);
