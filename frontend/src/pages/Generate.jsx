import { useState } from "react";

const Generate = () => {
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    coursename: "",
    courseid: "",
    institution: "",
    startdate: "",
    enddate: "",
  });
  const [certificateUrl, setCertificateUrl] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleGenerate = async () => {
    const response = await fetch(
      "http://localhost:5000/certificate/generate_certificate",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      }
    );
    const data = await response.json();
    if (data.download_url) {
      setCertificateUrl(`http://localhost:5000${data.download_url}`);
    }
  };

  return (
    <div className="flex flex-col min-h-screen px-6 py-4 dark:bg-gray-900 dark:text-white">
      <h2 className="text-[50px] font-bold text-blue-dark mb-4">
        Generate Sertifikat
      </h2>
      <div className="bg-white rounded-30 shadow-md grid grid-cols-1 md:grid-cols-2 gap-10 px-4 py-2 dark:bg-gray-800 dark:text-white">
        <div className="space-y-4 px-8 py-6">
          {[
            { label: "Nama", name: "name" },
            { label: "Email", name: "email" },
            { label: "No HP", name: "phone" },
            { label: "Nama Kursus", name: "coursename" },
            { label: "Course ID", name: "courseid" },
            { label: "Asal Kampus dan Kota", name: "institution" },
            { label: "Tanggal Mulai", name: "startdate", type: "date" },
            { label: "Tanggal Selesai", name: "enddate", type: "date" },
          ].map((item) => (
            <div key={item.name}>
              <label className="text-sm text-gray-dark dark:text-gray-500">{item.label}</label>
              <input
                type={item.type || "text"}
                name={item.name}
                value={form[item.name]}
                onChange={handleChange}
                className="w-full mt-1 border border-gray-light rounded-5 px-3 py-2 focus:outline-none focus:border-blue dark:bg-gray-800 dark:text-white dark:border-gray-600"
                placeholder={`Masukkan ${item.label.toLowerCase()}`}
              />
            </div>
          ))}

          <div className="flex gap-3 mt-4">
            <button
              className="bg-blue-dark text-blue-light px-4 py-2 rounded-5"
              onClick={handleGenerate}
            >
              Generate
            </button>
            {certificateUrl && (
              <a
                href={certificateUrl}
                className="bg-green-light text-green-dark px-4 py-2 rounded-5 hover:bg-green-dark hover:text-white"
                download
              >
                Download
              </a>
            )}
          </div>
        </div>

        <div className="hidden md:flex justify-center items-center">
          <img
            src="/generate.png"
            alt="Generate Illustration"
            className="max-w-[800px]"
          />
        </div>
      </div>
    </div>
  );
};

export default Generate;
