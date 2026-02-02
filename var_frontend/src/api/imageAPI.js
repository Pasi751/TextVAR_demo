// ===== api/imageAPI.js =====

import axios from "axios";

// Update to your VAR API URL
const API_BASE_URL = process.env.REACT_APP_API_URL;

/**
 * Generate image from text prompt using VAR model
 * @param {string} prompt - Text description of the image
 * @param {object} options - Generation options
 * @returns {Promise<{image: string, prompt: string, parameters: object}>}
 */
export const generateImage = async (prompt, options = {}) => {
  const {
    cfg_scale = 1.5,
    top_k = 900,
    top_p = 0.96,
    seed = null,
  } = options;

  const response = await axios.post(
    `${API_BASE_URL}/generate`,
    {
      prompt,
      cfg_scale,
      top_k,
      top_p,
      seed,
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 60000, // 60 second timeout for generation
    }
  );

  const data = response.data;

  if (!data.success) {
    throw new Error(data.error || "Failed to generate image");
  }

  // Return in format expected by frontend
  return {
    image: data.image_base64,
    prompt: data.prompt,
    parameters: data.parameters,
  };
};

/**
 * Generate multiple images from text prompts
 * @param {string[]} prompts - Array of text prompts
 * @param {object} options - Generation options
 * @returns {Promise<{images: Array, parameters: object}>}
 */
export const generateBatchImages = async (prompts, options = {}) => {
  const {
    cfg_scale = 1.5,
    top_k = 900,
    top_p = 0.96,
    seed = null,
  } = options;

  const response = await axios.post(
    `${API_BASE_URL}/generate/batch`,
    {
      prompts,
      cfg_scale,
      top_k,
      top_p,
      seed,
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 120000, // 2 minute timeout for batch
    }
  );

  const data = response.data;

  if (!data.success) {
    throw new Error(data.error || "Failed to generate images");
  }

  return {
    images: data.images.map((item) => ({
      image: item.image_base64,
      prompt: item.prompt,
    })),
    parameters: data.parameters,
  };
};

/**
 * Check API health status
 * @returns {Promise<{status: string, model_loaded: boolean}>}
 */
export const checkHealth = async () => {
  const response = await axios.get(`${API_BASE_URL}/health`, {
    timeout: 5000,
  });
  return response.data;
};