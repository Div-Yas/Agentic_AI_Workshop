// backend/api/routes.js
const express = require("express");

module.exports = (upload) => {
    const router = express.Router();
    const controller = require("../controllers/payrollController");

    router.post("/upload", upload.single("contract"), controller.uploadContract);

    return router;
};