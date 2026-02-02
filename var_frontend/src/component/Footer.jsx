import React from "react";
import { FaFacebookF, FaInstagram, FaTwitter, FaLinkedinIn } from "react-icons/fa";
import QR from '../assets/Contact Us.png';

const Footer = () => {
    return (
        <footer className="bg-[#1F304A] text-white ">

            {/* Top Title */}
            <div className="text-center pt-14">
                <h2 className="text-3xl font-medium font-poppins">
                    Bring your Ideas into Reality
                </h2>
                <div className="w-2/3 mx-auto border-b border-white/40 mt-6"></div>
            </div>

            {/* Content */}
            <div className="max-w-6xl mx-auto px-20 py-14 grid grid-cols-1 md:grid-cols-4 gap-10 text-center md:text-left">

                {/* Vision */}
                <div>
                    <h3 className="font-semibold mb-3 font-poppins text-2xl">Our Vision</h3>
                    <p className="text-sm text-white/80 leading-relaxed font-inter">
                        Bridging language <br />
                        and vision through <br />
                        autoregressive <br />
                        image generation
                    </p>
                </div>

                {/* Author */}
                <div>
                    <h3 className="font-semibold mb-3 font-inter">Author</h3>
                    <p className="text-sm text-white/80 font-inter">
                        Mr. Pasindu Madusara
                    </p>

                    <h3 className="font-semibold mt-5 mb-2 font-inter">Supervised By</h3>
                    <p className="text-sm text-white/80">
                        Mr. Dilum de Silva
                    </p>
                </div>

                {/* Pages */}
                <div>
                    <h3 className="font-semibold mb-3 font-inter">Pages</h3>
                    <ul className="text-sm text-white/80 space-y-2">
                        <li className="hover:text-white cursor-pointer font-inter">Homepage</li>
                        <li className="hover:text-white cursor-pointer font-inter">Documentation</li>
                        <li className="hover:text-white cursor-pointer font-inter">Research Info</li>
                    </ul>
                </div>

                {/* Contact */}
                <div>
                    <h3 className="font-semibold mb-3 font-inter">Contact Us</h3>

                    {/* QR Code */}
                    <div className="bg-white w-24 h-24 flex items-center justify-center mb-4 mx-auto md:mx-0">
                        <img
                            src={QR}
                            alt="Contact QR"
                            className="w-full h-full object-contain p-1"
                        />
                    </div>

                    {/* Social Icons */}
                    <div className="flex gap-3 justify-center md:justify-start">
                        <FaFacebookF className="cursor-pointer hover:opacity-70" />
                        <FaInstagram className="cursor-pointer hover:opacity-70" />
                        <FaLinkedinIn className="cursor-pointer hover:opacity-70" />
                    </div>
                </div>

            </div>

            {/* Bottom */}
            <div className="text-center text-sm text-white/70 pb-8 font-inter">
                © 2026 TextVAR. All rights reserved.
            </div>

        </footer>
    );
};

export default Footer;
