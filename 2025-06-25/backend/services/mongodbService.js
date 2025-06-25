// backend/services/mongodbService.js
const Contract = require("../models/contractModel");

exports.createEmployeeFromContract = async (contractData) => {
    try {
        const newContract = new Contract(contractData);
        await newContract.save();
        console.log("✅ Contract saved to MongoDB");
        return newContract;
    } catch (err) {
        throw new Error("❌ Failed to save contract to MongoDB: " + err.message);
    }
};