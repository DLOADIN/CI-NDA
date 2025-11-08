const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: function() {
      return !this.socialLogin.provider;
    }
  },
  userType: {
    type: String,
    enum: ['filmmaker', 'mentor', 'sponsor'],
    default: 'filmmaker'
  },
  avatar: String,
  bio: String,
  location: String,
  specialization: [String],
  website: String,
  socialLogin: {
    provider: String,
    providerId: String
  },
  stats: {
    followers: { type: Number, default: 0 },
    following: { type: Number, default: 0 },
    projects: { type: Number, default: 0 },
    awards: { type: Number, default: 0 }
  },
  enrolledCourses: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Course'
  }],
  isVerified: {
    type: Boolean,
    default: false
  },
  lastLogin: Date,
  createdAt: {
    type: Date,
    default: Date.now
  }
});

userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  if (this.password) {
    this.password = await bcrypt.hash(this.password, 10);
  }
  next();
});

userSchema.methods.comparePassword = async function(candidatePassword) {
  if (!this.password) return false;
  return await bcrypt.compare(candidatePassword, this.password);
};

module.exports = mongoose.model('User', userSchema);
