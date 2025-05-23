import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import Icon from "../icons/Icon";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [isDark, setIsDark] = useState(false);

  const menus = [
    { name: "Beranda", to: "/home", icon: "home" },
    { name: "Generate", to: "/generate", icon: "generate" },
    { name: "Verifikasi", to: "/validation", icon: "document_verified" },
  ];

  // Auto-collapse for small screens
  useEffect(() => {
    const handleResize = () => {
      setIsOpen(window.innerWidth >= 768);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Apply/remove dark mode globally
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add("dark", "bg-gray-900");
    } else {
      root.classList.remove("dark", "bg-gray-900");
    }
  }, [isDark]);

  return (
    <aside
      className={`sticky top-0 h-screen bg-white dark:bg-gray-900 dark:shadow-gray-800 shadow-lg z-50 p-6 transition-all duration-300 overflow-y-auto select-none cursor-default ${
        isOpen ? "w-64" : "w-20"
      }`}
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <img
            src="/logo.png"
            alt="CertGuard Logo"
            className={`h-[49px] ${isOpen ? "mr-2" : "mx-auto"}`}
          />
          {isOpen && (
            <h1 className="text-xl font-bold text-teal-700 dark:text-white">
              CertGuard
            </h1>
          )}
        </div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-gray-600 dark:text-gray-300 focus:outline-none"
        >
          <Icon name={isOpen ? "close" : "menu"} className="w-6 h-6" />
        </button>
      </div>

      <nav className="flex flex-col gap-2 mb-6">
        {menus.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-8 transition-all duration-300 ease-in-out border-l-4 ${
                isActive
                  ? "bg-blue-light text-blue-dark font-semibold border-blue-dark"
                  : "text-gray-600 dark:text-gray-300 hover:bg-blue-light hover:text-blue-dark border-transparent dark:hover:bg-gray-700 dark:hover:text-white"
              }`
            }
          >
            <Icon name={item.icon} className="w-5 h-5" />
            {isOpen && <span>{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Dark Mode Toggle */}
      <div className="mt-auto flex items-center justify-between px-2">
        {isOpen && (
          <span className="text-sm font-semibold text-gray-dark dark:text-gray-400">Dark Mode</span>
        )}
        <button
          onClick={() => setIsDark(!isDark)}
          className="bg-gray-300 dark:bg-gray-600 rounded-30 w-10 h-5 relative"
        >
          <div
            className={`absolute w-4 h-4 bg-white rounded-50 top-0.5 transition-transform ${
              isDark ? "translate-x-5" : "translate-x-0.5"
            }`}
          ></div>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;