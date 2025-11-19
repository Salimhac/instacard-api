// backend/routes/profile.js
const express = require("express");
const router = express.Router();
const imagekit = require("../utils/imagekit");
const multer = require("multer");

// Setup multer to temporarily hold the image in memory
const storage = multer.memoryStorage();
const upload = multer({ storage });

// POST /api/upload
router.post("/upload", upload.single("image"), async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: "No file uploaded" });

        const result = await imagekit.upload({
            file: req.file.buffer, // multer gives you the file buffer
            fileName: req.file.originalname,
            folder: "/instacard-profiles" // optional folder
        });

        // result.url is the hosted image URL
        res.json({ url: result.url });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Upload failed" });
    }
});

module.exports = router;
