import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import Icon from "../icons/Icon";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [isDark, setIsDark] = useState(false);
  const navigate = useNavigate();
  const role = localStorage.getItem("role") || "public";

  const menus = [
    { name: "Beranda", to: "/home", icon: "home" },
    { name: "Generate", to: "/generate", icon: "generate" },
    { name: "Verifikasi", to: "/validation", icon: "document_verified" },
  ];

  const visibleMenus = menus.filter((menu) => {
    if (role === "admin") return true;
    return menu.to !== "/generate";
  });

  useEffect(() => {
    const handleResize = () => {
      setIsOpen(window.innerWidth >= 768);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

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
      className={`sticky top-0 h-screen bg-white dark:bg-gray-900 dark:shadow-gray-800 shadow-lg z-50 p-4 transition-all duration-300 overflow-y-auto select-none cursor-default flex flex-col justify-between ${
        isOpen ? "w-64" : "w-24"
      }`}
    >
      {/* === Bagian Atas Sidebar === */}
      <div>
        <div className="relative mb-6 flex flex-col items-center">
          {/* Toggle button */}
          <div
            className={`w-full flex mb-2 ${
              isOpen ? "justify-end pr-1" : "justify-center"
            }`}
          >
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="flex justify-center items-center transition-transform duration-300"
            >
              <Icon name={isOpen ? "close" : "menu"} className="w-6 h-6" />
            </button>
          </div>

          {/* Logo + Title */}
          <div
            className={`flex items-center ${
              isOpen ? "justify-start w-full" : "justify-center"
            }`}
          >
            <img src="/logo.png" alt="Logo" className="h-[40px]" />
            {isOpen && (
              <h1 className="ml-2 text-xl font-bold text-teal-700 dark:text-white">
                CekSertif
              </h1>
            )}
          </div>
        </div>

        <div className="border-b border-gray-300 dark:border-gray-600 mb-4"></div>

        {/* === MENU NAVIGASI === */}
        <nav className="flex flex-col gap-2 mb-6">
          {isOpen && (
            <h3
              className={`font-sans text-gray-400 tracking-wider mb-2 ${
                isOpen
                  ? "text-sm px-4 text-left"
                  : "text-[5px] w-full text-center whitespace-nowrap"
              }`}
            >
              {role === "admin" ? "Navigasi Admin" : "Navigasi"}
            </h3>
          )}
          {visibleMenus.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive, location }) => {
                const currentPath =
                  location?.pathname || window.location.pathname;
                const isValidationActive =
                  item.to === "/validation" &&
                  (currentPath.startsWith("/validation") ||
                    currentPath.startsWith("/verify"));

                const active = isActive || isValidationActive;

                return `flex items-center gap-3 px-4 py-2 rounded-8 transition-all duration-300 ease-in-out border-l-4 ${
                  active
                    ? "bg-blue-light text-blue-dark font-semibold border-blue-dark"
                    : "text-gray-600 dark:text-gray-300 hover:bg-blue-light hover:text-blue-dark border-transparent dark:hover:bg-gray-700 dark:hover:text-white"
                }`;
              }}
            >
              <Icon name={item.icon} className="w-5 h-5" />
              {isOpen && <span>{item.name}</span>}
            </NavLink>
          ))}
        </nav>
      </div>

      <div>
        {/* User Profile Card */}
        {role === "admin" ? (
          <div
            className={`transition-all duration-300 ${
              isOpen
                ? "bg-blue-light px-4 py-4 rounded-10"
                : "bg-blue-light py-4 rounded-5 flex flex-col items-center"
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              <Icon name="avatar" className="w-10 h-10" />
              {isOpen && (
                <div>
                  <p className="text-sm font-semibold text-blue-dark dark:text-white">
                    {localStorage.getItem("username") || "Admin"}
                  </p>
                  <p className="text-xs text-gray-500">Admin</p>
                </div>
              )}
            </div>
            <div
              className={`mt-2 flex ${
                isOpen ? "justify-between" : "flex-col items-center gap-2"
              } text-sm text-gray-600 dark:text-gray-300`}
            >
              <button className="flex items-center gap-1 hover:text-blue-dark">
                <Icon name="setting" className="w-5 h-5" />{" "}
                {isOpen && "Setting"}
              </button>
              <button
                onClick={() => {
                  localStorage.clear();
                  navigate("/login");
                }}
                className="flex items-center gap-1 hover:text-red-dark"
              >
                <Icon name="logout" className="w-5 h-5" /> {isOpen && "Logout"}
              </button>
            </div>
          </div>
        ) : (
          <div
            className={`text-sm mt-4 ${
              isOpen ? "px-4" : "flex flex-col items-center"
            }`}
          >
            <button
              onClick={() => {
                window.location.href = "/login";
              }}
              className="flex items-center gap-2 bg-blue-light px-4 py-2 rounded-5 text-blue-dark dark:text-blue-dark hover:bg-blue-dark hover:text-white transition-colors duration-300"
            >
              <Icon name="signin" className="w-6 h-6" />
              {isOpen && <span>Login</span>}
            </button>
          </div>
        )}

        {/* Dark Mode Toggle */}
        <div className="mt-6 flex items-center justify-between px-2 mb-5">
          {isOpen && (
            <span className="text-sm font-semibold text-gray-dark dark:text-gray-400">
              Dark Mode
            </span>
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
      </div>
    </aside>
  );
};

export default Sidebar;
