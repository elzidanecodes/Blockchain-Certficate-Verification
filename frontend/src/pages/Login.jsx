import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../icons/Icon";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("https://localhost:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        navigate("/home");
      } else {
        alert(data.error || "Email atau password salah!");
      }
    } catch (error) {
      alert("Terjadi kesalahan server");
    }
  };

  // redirect jika sudah login
  useEffect(() => {
    fetch("https://localhost:5000/api/check_role", {
      method: "GET",
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.role) {
          navigate("/home");
        }
      })
      .catch(() => {});
  }, [navigate]);

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Left Side - Login Form */}
      <div className="w-full md:w-1/2 flex flex-col justify-center px-6 sm:px-16 md:px-28 lg:px-40 xl:px-56 bg-white py-14 md:py-24">
        <div className="flex items-center gap-3 mb-8">
          <img
            src="/logo.png"
            alt="CertGuard Logo"
            className="h-20"
            loading="lazy"
          />
          <h1 className="text-3xl font-bold text-teal-700">CekSertif</h1>
        </div>

        <h2 className="text-4xl font-bold text-gray-800 mb-4">
          Masuk ke Akun Anda
        </h2>
        <p className="text-gray-500 text-base mb-10">
          Silahkan login untuk mengelola dan memverifikasi sertifikat Anda.
        </p>

        <form onSubmit={handleLogin} className="space-y-8">
          <div className="relative">
            <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 pointer-events-none">
              <Icon name="email" className="w-5 h-5" />
            </span>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-gray-50 w-full pl-10 pr-4 py-4 border border-gray-200 rounded-10 focus:outline-none"
              required
            />
          </div>
          <div className="relative">
            <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 pointer-events-none">
              <Icon name="lock" className="w-5 h-5" />
            </span>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Kata Sandi"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-gray-50 w-full pl-10 pr-10 py-4 border border-gray-200 rounded-10 focus:outline-none"
              required
            />
            <button
              type="button"
              className="absolute inset-y-0 right-3 flex items-center text-gray-600"
              onClick={() => setShowPassword(!showPassword)}
              tabIndex={-1}
            >
              <Icon
                name={showPassword ? "eye_off" : "eye"}
                className="w-5 h-5"
              />
            </button>
          </div>

          <div className="flex justify-between items-center text-sm mt-3">
            <label className="flex items-center gap-2">
              <input type="checkbox" className="form-checkbox rounded-5" />{" "}
              Ingat saya
            </label>
            <a href="#" className="text-blue-dark hover:underline">
              Lupa kata sandi?
            </a>
          </div>
          <button
            type="submit"
            className="w-full py-4 bg-blue-dark text-white rounded-10 hover:bg-blue-700 transition"
          >
            Masuk
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          Atau lanjut sebagai{" "}
          <button
            onClick={() => navigate("/home")}
            className="text-blue-dark hover:underline font-normal"
          >
            Pengguna Publik
          </button>
        </p>

        <p className="mt-4 text-base text-center text-gray-500">
          Belum punya akun?{" "}
          <a href="#" className="text-blue-dark hover:underline">
            Hubungi administrator.
          </a>
        </p>
      </div>
      <div className="hidden md:flex w-1/2 items-center justify-center bg-blue-dark text-white p-6 md:p-10 lg:p-16 xl:p-24">
        <div className="text-center w-full max-w-2xl">
          <img
            src="/blockchain-illustration.png"
            alt="Ilustrasi Login"
            className="w-full h-auto max-h-[500px] md:max-h-[600px] object-contain mb-10"
          />
          <h2 className="text-2xl font-bold mb-4">
            Sistem Verifikasi Sertifikat Berbasis Blockchain
          </h2>
          <p className="text-base">
            Kelola dan verifikasi sertifikat Anda dengan mudah, aman, dan
            terpercaya.
          </p>
        </div>
      </div>
    </div>
  );
}
