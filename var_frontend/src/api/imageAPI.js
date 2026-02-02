// ===== api/imageAPI.js =====

import axios from "axios";

// Read API URL from environment variable, fallback to localhost for development
const API_BASE_URL = "https://mpm751-textvar-demo-space.hf.space/api";

// Remove trailing slash if present to avoid double slashes in URLs
const normalizedApiUrl = API_BASE_URL.endsWith('/') 
  ? API_BASE_URL.slice(0, -1) 
  : API_BASE_URL;

// DEBUG: Log the API URL being used
console.log('🔍 Environment check:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  API_BASE_URL: API_BASE_URL,
  normalizedApiUrl: normalizedApiUrl,
  allEnvVars: process.env
});

/**
 * Check API health status
 * @returns {Promise<{status: string, model_loaded: boolean}>}
 */
export const checkHealth = async () => {
  const url = `${normalizedApiUrl}/health`;
  console.log('🏥 Checking health at:', url);
  
  try {
    const response = await axios.get(url, {
      timeout: 5000,
    });
    console.log('✅ Health check response:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Health check failed:', {
      url: url,
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    throw error;
  }
};

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

  const url = `${normalizedApiUrl}/generate`;
  console.log('🎨 Generating image at:', url, 'with prompt:', prompt);

  try {
    const response = await axios.post(
      url,
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

    console.log('✅ Image generated successfully');

    // Return in format expected by frontend
    return {
      image: data.image_base64,
      prompt: data.prompt,
      parameters: data.parameters,
    };
  } catch (error) {
    console.error('❌ Image generation failed:', error);
    throw error;
  }
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

  const url = `${normalizedApiUrl}/generate/batch`;
  console.log('🎨 Batch generating images at:', url);

  try {
    const response = await axios.post(
      url,
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

    console.log('✅ Batch images generated successfully');

    return {
      images: data.images.map((item) => ({
        image: item.image_base64,
        prompt: item.prompt,
      })),
      parameters: data.parameters,
    };
  } catch (error) {
    console.error('❌ Batch generation failed:', error);
    throw error;
  }
};