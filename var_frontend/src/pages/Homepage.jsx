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
  const [cfgScale, setCfgScale] = useState(10);
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
    <div className="min-h-screen bg-[#294466] flex flex-col items-center py-8 px-4 sm:py-12 sm:px-6 md:py-16 md:px-8 lg:py-20 lg:px-12">

      {/* Heading */}
      <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-semibold text-white text-center font-poppins leading-tight">
        Transform text into <br className="hidden sm:block" /> 
        <span className="sm:hidden"> </span>stunning images
      </h1>

      <p className="text-sm sm:text-base md:text-lg text-white/80 text-center mt-4 sm:mt-6 md:mt-8 max-w-xs sm:max-w-lg md:max-w-2xl lg:max-w-4xl font-poppins px-2">
        Turn your idea into reality using text-conditioned VAR model
      </p>

      {/* Prompt Card */}
      <div className="bg-[#58769A] w-full max-w-sm sm:max-w-xl md:max-w-2xl lg:max-w-4xl rounded-xl p-4 sm:p-5 md:p-6 mt-8 sm:mt-12 md:mt-16 lg:mt-20">
        
        {/* API Status Indicator */}
        {apiStatus && (
          <div className={`inline-block px-2 py-1 sm:px-3 rounded-full text-xs ${
            apiStatus.model_loaded
              ? "bg-green-500 text-white"
              : "bg-yellow-500 text-black"
          }`}>
            {apiStatus.model_loaded ? "✓ Model Ready" : "⏳ Loading..."}
          </div>
        )}
        
        <p className="text-white text-xs mt-2 text-left mb-2">
          *This model is trained on flower images. For best results, use flower-related prompts.
        </p>
        
        {/* Input and Button - Stack on mobile, row on larger screens */}
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your text prompt..."
            className="flex-1 bg-[#E9EEF6] text-[#1F304A] px-3 py-3 sm:px-4 sm:py-4 rounded-lg outline-none text-sm sm:text-base"
          />

          <button
            onClick={handleGenerate}
            disabled={loading || !apiStatus?.model_loaded}
            className="bg-[#1F304A] text-white px-4 py-3 sm:px-6 sm:py-4 rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
          >
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>

        {/* Advanced Options Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-white/80 text-xs mt-3 hover:text-white transition-colors"
        >
          {showAdvanced ? "▼ Hide" : "▶ Show"} Advanced Options
        </button>

        {/* Advanced Options - Stack on mobile */}
        {showAdvanced && (
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-3 p-3 bg-[#4a6a8a] rounded-lg">
            <div className="flex items-center gap-2">
              <label className="text-white text-xs whitespace-nowrap">CFG Scale:</label>
              <input
                type="number"
                value={cfgScale}
                onChange={(e) => setCfgScale(parseFloat(e.target.value) || 10)}
                min="1"
                max="10"
                step="0.1"
                className="w-20 sm:w-16 bg-[#E9EEF6] text-[#1F304A] px-2 py-1 rounded text-sm"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-white text-xs whitespace-nowrap">Seed:</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                placeholder="Random"
                className="w-28 sm:w-24 bg-[#E9EEF6] text-[#1F304A] px-2 py-1 rounded text-sm"
              />
            </div>
          </div>
        )}

        {/* Suggested Prompts - Scrollable on mobile */}
        <div className="mt-4">
          <p className="text-white/60 text-xs mb-2">Suggested prompts:</p>
          <div className="flex flex-wrap gap-2 max-h-24 sm:max-h-none overflow-y-auto sm:overflow-visible">
            {suggestions.map((item, index) => (
              <button
                key={index}
                onClick={() => setPrompt(item)}
                className="bg-[#E9EEF6] text-[#1F304A] px-2 py-1 sm:px-3 rounded-full text-xs hover:bg-white transition-colors whitespace-nowrap"
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Image Preview Card */}
      <div className="bg-[#58769A] w-full max-w-sm sm:max-w-xl md:max-w-2xl lg:max-w-4xl rounded-xl p-4 sm:p-5 md:p-6 mt-6 sm:mt-8 md:mt-10 lg:mt-14">
        
        <div className="flex justify-between items-center mb-3">
          <p className="text-white font-medium text-sm sm:text-base">Image Preview</p>

          {generatedImage && (
            <button
              onClick={handleDownload}
              className="bg-[#1F304A] text-white px-2 py-1 sm:px-3 rounded text-xs hover:opacity-90 transition-opacity"
            >
              ⬇ Download
            </button>
          )}
        </div>

        {/* Image container - Responsive height */}
        <div className="bg-white w-full h-[250px] sm:h-[300px] md:h-[350px] lg:h-[400px] rounded-lg flex items-center justify-center overflow-hidden">
          {loading && (
            <div className="flex flex-col items-center gap-3 p-4">
              <div className="w-8 h-8 sm:w-10 sm:h-10 border-4 border-[#294466] border-t-transparent rounded-full animate-spin"></div>
              <span className="text-gray-400 text-sm sm:text-base text-center">
                Generating image...
                <br />
                <span className="text-xs text-gray-300">This may take a moment</span>
              </span>
            </div>
          )}

          {!loading && generatedImage && (
            <img
              src={generatedImage}
              alt="Generated"
              className="max-h-full max-w-full object-contain rounded-lg p-2"
            />
          )}

          {!loading && !generatedImage && !error && (
            <span className="text-gray-400 text-sm sm:text-base text-center px-4">
              Generated image will appear here
            </span>
          )}

          {error && (
            <div className="text-center px-4">
              <span className="text-red-500 text-sm sm:text-base">{error}</span>
              <br />
              <button
                onClick={handleGenerate}
                className="mt-2 text-[#294466] text-sm underline hover:no-underline"
              >
                Try again
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <p className="text-white/40 text-xs mt-6 sm:mt-8 text-center px-4">
        Powered by TextVAR • Built with VAR, CLIP & VQVAE
      </p>
    </div>
  );
};

export default Homepage;