// Navbar.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-[#1F304A] text-[#FAF5F5] py-2">
      <div className="mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo */}
          <Link to="/" className="text-2xl font-bold font-Inter">
            TextVAR
          </Link>

          {/* Desktop Links */}
          <div className="hidden md:flex space-x-8">
            <Link to="/" class="hover:text-gray-300 font-inter text-sm">Homepage</Link>
            <Link to="/documentation" className="hover:text-gray-300 font-inter text-sm">Documentation</Link>
            <Link to="/research-info" className="hover:text-gray-300 font-inter text-sm">Research Info</Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="focus:outline-none"
            >
              ☰
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden px-4 pb-4 space-y-2">
          <Link to="/" onClick={() => setIsOpen(false)} className="block hover:bg-[#27395D] px-3 py-2 rounded">
            Homepage
          </Link>
          <Link to="/documentation" onClick={() => setIsOpen(false)} className="block hover:bg-[#27395D] px-3 py-2 rounded">
            Documentation
          </Link>
          <Link to="/research-info" onClick={() => setIsOpen(false)} className="block hover:bg-[#27395D] px-3 py-2 rounded">
            Research Info
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
