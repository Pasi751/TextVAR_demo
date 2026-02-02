import React from "react";

const ResearchInfo = () => {
  return (
    <div className="min-h-screen bg-[#264061] text-white">

      {/* Page Title */}
      <section className="text-center py-14">
        <h2 className="text-4xl font-poppins font-semibold">Research Info</h2>
      </section>

      {/* Research Content Card */}
      <section className="flex justify-center px-15 mb-25">
        <div className="bg-[#58769A] max-w-4xl w-full rounded-xl p-10 shadow-lg">

          <h3 className="text-lg font-inter font-semibold text-center mb-6">
            TextVAR : Integrating text condition image generation <br />
            into Visual Autoregressive model
          </h3>

          <div className="font-inter space-y-5 text-sm leading-relaxed text-white/90">
            <p>
              This research focuses on the integration of text-conditioned image
              generation into a visual autoregressive modeling framework. The
              objective is to explore how natural language descriptions can
              effectively guide the sequential generation of visual content,
              enabling coherent and context-aware image synthesis.
            </p>

            <p>
              Traditional image generation approaches often rely on latent
              diffusion or purely visual representations. In contrast, this work
              investigates a visual autoregressive model that generates images
              step-by-step while being explicitly conditioned on textual input.
              By incorporating text embeddings into the autoregressive process,
              the model learns to align linguistic semantics with visual
              structures during image formation.
            </p>

            <p>
              The proposed system allows users to interact with the model through
              a web-based interface, where custom or predefined prompts can be
              provided as textual conditions. This interaction enables practical
              observation of how different prompts influence generated outputs,
              offering insight into the relationship between language and visual
              creativity.
            </p>

            <p>
              Through experimental evaluation and user-driven prompt
              exploration, this research aims to demonstrate the effectiveness,
              flexibility, and limitations of text-guided visual autoregressive
              models. The findings contribute to ongoing research in multimodal
              learning, human-AI interaction, and controllable image generation.
            </p>
          </div>

          {/* Author Info */}
          <div className="text-center mt-10 text-sm">
            <p><span className="font-semibold">Author:</span> Mr. Pasindu Madusara</p>
            <p><span className="font-semibold">Supervised By:</span> Mr. Dilum de Silva</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ResearchInfo;
