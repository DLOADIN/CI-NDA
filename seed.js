const mongoose = require('mongoose');
const dotenv = require('dotenv');
const Course = require('./models/Course');
const Opportunity = require('./models/Opportunity');

dotenv.config();

const courses = [
  {
    title: "Introduction to Cinematography",
    category: "CINEMATOGRAPHY",
    instructor: {
      name: "Roger Deakins",
      bio: "Award-winning cinematographer"
    },
    description: "Master the fundamentals of camera work, lighting composition, and visual storytelling techniques used in professional film production.",
    image: "d.jpeg",
    duration: "12 weeks",
    level: "Beginner"
  },
  // Add all other courses...
];

const opportunities = [
  {
    type: "GRANT",
    title: "Independent Film Production Grant",
    company: "Sundance Institute",
    description: "We're seeking original, compelling narratives from emerging filmmakers...",
    details: {
      funding: "$50,000",
      location: "Remote/Worldwide",
      category: "Feature Film"
    },
    deadline: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000) // 60 days from now
  },
  // Add all other opportunities...
];

async function seedDatabase() {
  try {
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('Connected to MongoDB');

    await Course.deleteMany({});
    await Opportunity.deleteMany({});
    
    await Course.insertMany(courses);
    await Opportunity.insertMany(opportunities);

    console.log('✅ Database seeded successfully');
    process.exit(0);
  } catch (error) {
    console.error('❌ Seeding error:', error);
    process.exit(1);
  }
}

seedDatabase();
