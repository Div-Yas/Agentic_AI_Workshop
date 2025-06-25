// backend/config.js
const mongoose = require("mongoose");

const dbUrl = process.env.MONGODB_URI;

mongoose.connect(dbUrl, {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => console.log("✅ MongoDB connected"))
  .catch(err => console.error("❌ MongoDB connection error:", err));

module.exports = mongoose;