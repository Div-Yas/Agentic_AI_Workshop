// backend/controllers/payrollController.js
const { exec } = require("child_process");
const path = require("path");

exports.uploadContract = (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
    }

    const filePath = req.file.path;
    const pythonScriptPath = path.resolve(__dirname, "../agents/contract_reader.py");

    // Run Python script
    exec(`python ${pythonScriptPath} "${filePath}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Python execution failed: ${stderr}`);
            return res.status(500).json({ error: "Failed to parse contract" });
        }

        try {
            const parsedData = JSON.parse(stdout);
            return res.json(parsedData);
        } catch (parseError) {
            console.error("❌ Failed to parse Python output:", parseError);
            return res.status(500).json({ error: "Invalid response from parser" });
        }
    });
};