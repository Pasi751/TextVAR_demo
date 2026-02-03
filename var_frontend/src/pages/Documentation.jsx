import React from "react";

const Documentation = () => {
  return (
    /* Page Background */
    <div className="min-h-screen bg-[#264061] py-20 px-4">

      {/* Documentation Container */}
      <div className="max-w-6xl mx-auto bg-[#58769A] rounded-2xl p-8 md:p-14 text-white">

        {/* Title */}
        <h1 className="text-4xl md:text-5xl font-poppins font-semibold text-center mb-4">
          Documentation
        </h1>

        <p className="text-center text-lg font-inter text-white/80 font-inter max-w-3xl mx-auto mb-16">
          Technical and user documentation for the Text-Conditioned Visual
          Autoregressive Image Generation Platform(TextVAR)
        </p>

        <div className="space-y-14">

          {/* 1. Overview */}
          <section className="mb-5">
            <h2 className="text-xl font-inter font-semibold mb-2">
              1. Overview
            </h2>
            <p className="font-inter text-sm text-white/90 leading-relaxed">
              This platform enables users to generate high-quality images using
              text prompts through a Visual Autoregressive(VAR) model. The system
              extends a previously class-conditioned VAR model by integrating text
              conditioning.
            </p>

            <ul className="text-sm list-disc list-inside mt-3 font-inter text-white/80 space-y-1">
              <li>Enter custom text prompts</li>
              <li>Select from suggested prompts</li>
              <li>Generate images via an API</li>
              <li>Preview generated images</li>
              <li>Download generated images</li>
            </ul>
          </section>

          {/* 2. System Architecture */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              2. System Architecture
            </h2>

            <h3 className="text-lg font-inter mb-1">2.1 Frontend</h3>
            <ul className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              <li>Web-based user interface</li>
              <li>Accepts text prompts</li>
              <li>Displays suggested prompts</li>
              <li>Sends requests to backend API</li>
              <li>Displays and downloads images</li>
            </ul>

            <h3 className="text-lg font-inter mb-1">2.2 Backend API</h3>
            <ul className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              <li>Image generation endpoint</li>
              <li>Text conditioning logic</li>
              <li>VAR model inference</li>
              <li>Returns generated images</li>
            </ul>

            <h3 className="text-lg font-inter mb-1">2.3 Model</h3>
            <ul className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              <li>Visual Autoregressive (VAR) model</li>
              <li>Extended to support text conditioning</li>
              <li>Autoregressive token-based generation</li>
            </ul>
          </section>

          {/* 3. Features */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              3. Features
            </h2>

            <h3 className="text-lg font-inter mb-1">
              3.1 Text Prompt Input
            </h3>
            <p className="text-sm font-inter text-white/80">
              Users can enter natural language descriptions to guide image
              generation.
            </p>

            <div className="bg-[#1F304A] rounded-lg p-4 mt-3 font-inter text-sm mb-3">
              <pre>'a beautiful red rose flower'</pre>
              <pre>'a yellow sunflower with green leaves'</pre>
              <pre>'a purple orchid flower'</pre>
            </div>

            <h3 className="text-lg font-inter mb-1">
              3.2 Suggested Prompts
            </h3>
            <p className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              Predefined prompts help users explore the model’s capabilities.
            </p>

            <h3 className="text-lg font-inter mb-1">
              3.3 Image Generation
            </h3>
            <ul className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              <li>Prompt sent to backend API</li>
              <li>Text conditioning applied</li>
              <li>VAR model generates image</li>
              <li>Image returned to UI</li>
            </ul>
          </section>

          {/* 4. API Documentation */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              4. API Documentation
            </h2>

            {/* Base URL */}
            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">Base URL</p>
              <pre className="text-green-400">
                {`https://mpm751-textvar-demo-space.hf.space/api`}
              </pre>
            </div>

            {/* Health Check */}
            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">GET /api/health</p>
              <p className="text-gray-400 mb-2">Check API status</p>
              <p className="font-semibold mb-1">Response</p>
              <pre>
                {`{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda"
}`}
              </pre>
            </div>

            {/* Generate Image */}
            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">POST /api/generate</p>
              <p className="text-gray-400 mb-2">Generate image from text prompt</p>
              <p className="font-semibold mb-1">Request Body</p>
              <pre>
                {`{
  "prompt": "a beautiful red rose flower",
  "cfg_scale": 10,
  "top_k": 900,
  "top_p": 0.96,
  "seed": 42  // optional, null for random
}`}
              </pre>
            </div>

            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">Response (Success)</p>
              <pre>
                {`{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "a beautiful red rose flower",
  "parameters": {
    "cfg_scale": 10,
    "top_k": 900,
    "top_p": 0.96,
    "seed": 42
  }
}`}
              </pre>
            </div>

            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">Response (Error)</p>
              <pre>
                {`{
  "success": false,
  "error": "Error message here"
}`}
              </pre>
            </div>

            {/* Example cURL */}
            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm">
              <p className="font-semibold mb-2">Example (cURL)</p>
              <pre className="whitespace-pre-wrap break-all">
                {`curl -X POST https://mpm751-textvar-demo-space.hf.space/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "a beautiful red rose flower", "cfg_scale": 10}'`}
              </pre>
            </div>
          </section>

          {/* 5. User workflow */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              5. User Workflow
            </h2>
            <ol className="text-sm font-inter text-white/80 space-y-1 mb-3">
              <li>1. Web-based user interface</li>
              <li>2. Enter a custom text prompt or select a suggested prompt</li>
              <li>3. Click Generate Image</li>
              <li>4. Wait for the image to be generated</li>
              <li>5. Preview the generated image</li>
              <li>6. Click Download to save the image</li>
            </ol>
          </section>

          {/* 6. Prompt Guidelines */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              6. Prompt Guidelines
            </h2>
            <p className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              To get better results:
            </p>
            <ul className="text-sm list-disc list-inside font-inter text-white/80 space-y-1 mb-3">
              <li> Web-based user interface</li>
              <li> Enter a custom text prompt or select a suggested prompt</li>
              <li> Click Generate Image</li>
              <li> Wait for the image to be generated</li>
              <li> Preview the generated image</li>
              <li> Click Download to save the image</li>
            </ul>
            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">Good Prompt Example</p>
              <pre>
                'A yellow sunflower with green leaves'
              </pre>
            </div>

            <div className="bg-[#1F304A] rounded-lg p-4 font-inter text-sm mb-4">
              <p className="font-semibold mb-2">Poor Prompt Example</p>
              <pre>
                'Sunflower'
              </pre>
            </div>
          </section>

          {/* 7. Limitations */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              7. Limitations
            </h2>
            <ul className="list-disc list-inside text-sm font-inter text-white/80 space-y-1 mb-3">
              <li>Image quality depends on prompt clarity</li>
              <li>Complex scenes may require more detailed prompts</li>
              <li>Generation time varies based on system load and model size</li>
              <li>The model may not always produce perfectly accurate results</li>
            </ul>
          </section>

          {/* 8. Security & Usage Considerations*/}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              8. Security & Usage Considerations
            </h2>
            <ul className="list-disc list-inside text-sm font-inter text-white/80 space-y-1 mb-3">
              <li>Inputs are validated before processing</li>
              <li>Rate limiting can be applied to prevent abuse</li>
              <li>Generated images are not permanently stored unless explicitly saved</li>
            </ul>
          </section>

          {/* 9. Future Enhancements        */}
          <section className="mb-5">
            <h2 className="font-inter text-xl font-inter font-semibold mb-2">
              9. Future Enhancements
            </h2>
            <ul className="list-disc list-inside text-sm font-inter text-white/80 space-y-1 mb-3">
              <li>Prompt history</li>
              <li>Multiple image generation per prompt</li>
              <li>Style selection options</li>
              <li>Image resolution control</li>
              <li>User accounts and saved generations</li>
            </ul>
          </section>



        </div>
      </div>
    </div>
  );
};

export default Documentation;
