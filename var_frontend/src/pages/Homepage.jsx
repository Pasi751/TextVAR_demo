// ===== components/Homepage.jsx =====

import React, { useState, useEffect } from "react";
import { generateImage, checkHealth } from "../api/imageAPI";

const Homepage = () => {
  const [prompt, setPrompt] = useState("");
  const [generatedImage, setGeneratedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState(null);

  // Advanced options (optional)
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [cfgScale, setCfgScale] = useState(1.5);
  const [seed, setSeed] = useState("");

  // Flower-specific suggestions (since model is trained on flowers)
  const suggestions = [
    "a beautiful red rose flower",
    "a yellow sunflower with green leaves",
    "a purple orchid flower",
    "a white daisy flower",
    "a pink tulip in bloom",
    "a blue iris flower",
  ];

  // Check API health on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const health = await checkHealth();
        setApiStatus(health);
      } catch (err) {
        setApiStatus({ status: "offline", model_loaded: false });
      }
    };
    checkApiHealth();
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError("");
    setGeneratedImage(null);

    try {
      const data = await generateImage(prompt, {
        cfg_scale: cfgScale,
        top_k: 900,
        top_p: 0.96,
        seed: seed ? parseInt(seed) : null,
      });

      // Backend returns base64 image
      setGeneratedImage(`data:image/png;base64,${data.image}`);
    } catch (err) {
      if (err.response?.status === 503) {
        setError("Model is still loading. Please wait and try again.");
      } else if (err.code === "ECONNABORTED") {
        setError("Request timed out. Please try again.");
      } else {
        setError(err.message || "Failed to generate image. Please try again.");
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      handleGenerate();
    }
  };

  const handleDownload = () => {
    if (!generatedImage) return;

    const link = document.createElement("a");
    link.href = generatedImage;
    link.download = `generated_${Date.now()}.png`;
    link.click();
  };

  return (
    <div className="min-h-screen bg-[#294466] flex flex-col items-center py-25 px-15">

      {/* Heading */}
      <h1 className="text-7xl font-semibold text-white text-center font-poppins">
        Transform text into <br /> stunning images
      </h1>

      <p className="text-lg text-white/80 text-center mt-8 max-w-8xl font-poppins">
        Turn your idea into reality using text-conditioned VAR model
      </p>

      {/* Prompt Card */}
      <div className="bg-[#58769A] w-full max-w-4xl rounded-xl p-6 mt-20">
        {/* API Status Indicator */}
        {apiStatus && (
          <div className={`top-4 left-4 px-3 py-1 rounded-full text-xs max-w-28 ${apiStatus.model_loaded
            ? "bg-green-500 text-white"
            : "bg-yellow-500 text-black"
            }`}>
            {apiStatus.model_loaded ? "✓ Model Ready" : "⏳ Model Loading..."}
          </div>
        )}
        <p className="text-white text-xs mt-2 text-left mb-2">
          *This model is trained on flower images. For best results, use flower-related prompts.
        </p>
        <div className="flex gap-4">
          {/* Footer Note */}
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your text prompt (e.g., 'a beautiful red rose flower')..."
            className="flex-1 bg-[#E9EEF6] text-[#1F304A] px-4 py-4 rounded-lg outline-none"
          />

          <button
            onClick={handleGenerate}
            disabled={loading || !apiStatus?.model_loaded}
            className="bg-[#1F304A] text-white px-6 rounded-lg text-sm hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>

        {/* Advanced Options Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-white text-xs mt-3 hover:text-white"
        >
          {showAdvanced ? "▼ Hide" : "▶ Show"} Advanced Options
        </button>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="flex gap-4 mt-3">
            <div className="flex items-center gap-2">
              <label className="text-white text-xs">CFG Scale:</label>
              <input
                type="number"
                value={cfgScale}
                onChange={(e) => setCfgScale(parseFloat(e.target.value) || 10)}
                min="1"
                max="10"
                step="0.1"
                className="w-16 bg-[#E9EEF6] text-[#1F304A] px-2 py-1 rounded text-sm"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-white text-xs">Seed:</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                placeholder="Random"
                className="w-24 bg-[#E9EEF6] text-[#1F304A] px-2 py-1 rounded text-sm"
              />
            </div>
          </div>
        )}

        {/* Suggested Prompts */}
        <div className="flex flex-wrap gap-2 mt-4">
          {suggestions.map((item, index) => (
            <button
              key={index}
              onClick={() => setPrompt(item)}
              className="bg-[#E9EEF6] text-[#1F304A] px-3 py-1 rounded-full text-xs hover:bg-white transition-colors"
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {/* Image Preview Card */}
      <div className="bg-[#58769A] w-full max-w-4xl rounded-xl p-6 mt-14">
        <div className="flex justify-between items-center mb-3">
          <p className="text-white font-medium">Image Preview</p>

          {generatedImage && (
            <button
              onClick={handleDownload}
              className="bg-[#1F304A] text-white px-3 py-1 rounded text-xs hover:opacity-90"
            >
              ⬇ Download
            </button>
          )}
        </div>

        <div className="bg-white w-full h-[350px] rounded-lg flex items-center justify-center overflow-hidden">
          {loading && (
            <div className="flex flex-col items-center gap-3">
              <div className="w-10 h-10 border-4 border-[#294466] border-t-transparent rounded-full animate-spin"></div>
              <span className="text-gray-400">Generating image...</span>
            </div>
          )}

          {!loading && generatedImage && (
            <img
              src={generatedImage}
              alt="Generated"
              className="h-full object-contain rounded-lg"
            />
          )}

          {!loading && !generatedImage && !error && (
            <span className="text-gray-400">
              Generated image will appear here
            </span>
          )}

          {error && (
            <div className="text-center px-4">
              <span className="text-red-500">{error}</span>
              <br />
              <button
                onClick={handleGenerate}
                className="mt-2 text-[#294466] text-sm underline"
              >
                Try again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Homepage;