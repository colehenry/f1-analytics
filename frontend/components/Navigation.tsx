"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export default function Navigation() {
  const pathname = usePathname();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    }

    if (isDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isDropdownOpen]);

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/results", label: "Results" },
    { href: "/analyze", label: "Analyze" },
    { href: "/about", label: "About" },
  ];

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 bg-black shadow-lg z-50 opacity-100">
      <div className="max-w-7xl mx-auto px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo - left side */}
          <div className="flex-shrink-0">
            <Link href="/" className="block">
              <div className="h-16 w-16 rounded flex items-center justify-center hover:opacity-80 transition-opacity">
                <Image
                  src="/favicon.ico"
                  alt="lapwise logo"
                  width={64}
                  height={64}
                  className="rounded"
                />
              </div>
            </Link>
          </div>

          {/* Navigation links - center */}
          <div className="absolute left-1/2 transform -translate-x-1/2 flex space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`hover:text-purple-200 hover:bg-white/10 rounded-md transition-all px-4 py-2 text-base ${
                  isActive(link.href)
                    ? "font-bold text-purple-500"
                    : "font-medium text-white"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Profile icon - right side */}
          <div className="flex-shrink-0 relative" ref={dropdownRef}>
            <button
              type="button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors"
              aria-label="Profile menu"
            >
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <title>User profile</title>
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </button>

            {/* Dropdown menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-900 rounded-md shadow-lg py-1 border-2 border-purple-500/50">
                <Link
                  href="/profile"
                  className="block px-4 py-2 text-sm text-white hover:bg-purple-600/20 hover:border-l-4 hover:border-purple-500 transition-all"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Profile
                </Link>
                <Link
                  href="/settings"
                  className="block px-4 py-2 text-sm text-white hover:bg-purple-600/20 hover:border-l-4 hover:border-purple-500 transition-all"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Settings
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
