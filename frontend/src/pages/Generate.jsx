import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Swal from "sweetalert2";

const Generate = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    no_sertifikat: "",
    name: "",
    student_id: "",
    department: "",
    test_date: "",
    listening: "",
    reading: "",
    writing: "",
  });
  const [errors, setErrors] = useState({});
  const [certificateUrl, setCertificateUrl] = useState("");
  const [isAllowed, setIsAllowed] = useState(null);
  const [excelFile, setExcelFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState(
    "Belum ada file dipilih"
  );

  useEffect(() => {
    const cekRole = async () => {
      try {
        const res = await fetch("https://localhost:5000/api/check_role", {
          credentials: "include",
        });
        const data = await res.json();

        if (res.ok && data.role === "admin") {
          setIsAllowed(true);
        } else {
          navigate("/home", { replace: true });
        }
      } catch (err) {
        navigate("/home", { replace: true });
      }
    };
    cekRole();
  }, [navigate]);

  if (isAllowed === null) {
    return (
      <div className="flex justify-center items-center h-screen text-gray-600 dark:text-white">
        Mengecek akses...
      </div>
    );
  }

  const handleChange = (e) => {
    const { name, value, files } = e.target;

    if (name === "file") {
      setExcelFile(files[0]);
      setSelectedFileName(
        files.length > 0 ? files[0].name : "Belum ada file dipilih"
      );
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    Object.entries(form).forEach(([key, value]) => {
      if (!value) {
        newErrors[key] = "Wajib diisi";
      } else if (
        ["listening", "reading", "writing"].includes(key) &&
        isNaN(value)
      ) {
        newErrors[key] = "Harus berupa angka";
      }
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleGenerate = async () => {
    if (excelFile) {
      Swal.fire({
        icon: "error",
        title: "Pilihan Input Ganda",
        text: "Silakan kosongkan file Excel jika ingin mengisi form manual.",
      });
      return;
    }

    if (!validateForm()) {
      Swal.fire({
        icon: "error",
        title: "Form Belum Lengkap",
        text: "Harap isi semua field yang dibutuhkan dengan benar.",
      });
      return;
    }

    const total_lr =
      parseInt(form.listening || 0) + parseInt(form.reading || 0);
    const total_writing = parseInt(form.writing || 0);

    const dataToSend = {
      ...form,
      total_lr,
      total_writing,
    };

    const response = await fetch(
      "https://localhost:5000/certificate/generate_certificate",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dataToSend),
        credentials: "include",
      }
    );

    const data = await response.json();
    if (data.download_url) {
      setCertificateUrl(`https://localhost:5000${data.download_url}`);
      Swal.fire({
        icon: "success",
        title: "Sertifikat Berhasil Dibuat",
        text: "Silakan download sertifikat Anda.",
        confirmButtonColor: "#00B140",
      });
    } else if (data.error) {
      Swal.fire({
        icon: "error",
        title: "Gagal Generate",
        text: data.error,
      });
    }
  };

  const handleUploadExcel = async () => {
    const isFormFilled = Object.values(form).some((value) => value);

    if (isFormFilled) {
      Swal.fire({
        icon: "error",
        title: "Pilihan Input Ganda",
        text: "Silakan kosongkan semua form jika ingin upload file Excel.",
      });
      return;
    }

    if (!excelFile) {
      Swal.fire({
        icon: "error",
        title: "File belum dipilih",
        text: "Silakan pilih file Excel terlebih dahulu.",
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", excelFile);

    try {
      const response = await fetch(
        "https://localhost:5000/certificate/upload_excel",
        {
          method: "POST",
          body: formData,
          credentials: "include",
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "all_certificates.zip";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        Swal.fire({
          icon: "success",
          title: "Download ZIP Sukses",
          text: "Sertifikat berhasil digenerate dan ZIP berhasil diunduh.",
        });

        setExcelFile(null);
        setSelectedFileName("Belum ada file dipilih");
      } else {
        const errorText = await response.text();
        Swal.fire({
          icon: "error",
          title: "Gagal Upload",
          text: errorText,
        });
      }
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: error.message,
      });
    }
  };

  const fields = [
    { label: "No Sertifikat", name: "no_sertifikat" },
    { label: "Nama", name: "name" },
    { label: "Student ID", name: "student_id" },
    { label: "Department", name: "department" },
    { label: "Test Date", name: "test_date", type: "date" },
    { label: "Listening", name: "listening", type: "number" },
    { label: "Reading", name: "reading", type: "number" },
    { label: "Writing", name: "writing", type: "number" },
  ];

  return (
    <div className="flex flex-col min-h-screen px-14 py-7 dark:bg-gray-900 dark:text-white overflow-y-auto">
      <h2 className="text-[50px] font-bold text-blue-dark mb-4">
        Generate Sertifikat PECT
      </h2>

      <p className="inline-block w-fit text-red-dark text-sm mb-4 bg-red-50 border border-red-200 rounded-5 px-4 py-2 min-w-min dark:bg-gray-800 dark:text-white">
        Pilih salah satu metode input: <strong>isi form manual</strong> atau{" "}
        <strong>upload file Excel</strong>. Tidak boleh keduanya bersamaan.
      </p>

      <div className="bg-white rounded-30 shadow-md grid grid-cols-1 md:grid-cols-2 gap-10 px-4 py-2 dark:bg-gray-800 dark:text-white">
        <div className="space-y-4 px-8 py-6">
          {fields.map((item) => (
            <div key={item.name}>
              <label className="text-sm text-gray-dark dark:text-gray-500">
                {item.label}
              </label>
              <input
                type={item.type || "text"}
                name={item.name}
                value={form[item.name]}
                onChange={handleChange}
                className={`w-full mt-1 border px-3 py-2 rounded-5 focus:outline-none ${
                  errors[item.name]
                    ? "border-red-dark"
                    : "border-gray-light dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                }`}
                placeholder={`Masukkan ${item.label}`}
              />
              {errors[item.name] && (
                <p className="text-red-dark text-sm mt-1">
                  {errors[item.name]}
                </p>
              )}
            </div>
          ))}

          <div>
            <label className="text-sm text-gray-dark dark:text-gray-500 mb-1 block">
              Pilih File Excel
            </label>

            <label
              htmlFor="fileUpload"
              className="inline-block px-24 py-2 bg-blue-600 text-white rounded-5 cursor-pointer hover:bg-blue-700"
            >
              Pilih File
            </label>

            <input
              type="file"
              name="file"
              accept=".xlsx, .xls, .csv"
              onChange={handleChange}
              className="hidden"
              id="fileUpload"
            />

            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {selectedFileName}
            </p>
          </div>

          <div className="flex gap-3 mt-4">
            <button
              className="bg-blue-dark text-blue-light px-4 py-2 rounded-5"
              onClick={handleGenerate}
            >
              Generate
            </button>

            <button
              className="bg-green-500 text-white px-4 py-2 rounded-5"
              onClick={handleUploadExcel}
            >
              Upload Excel
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

        <div className="hidden md:flex justify-center items-center p-4">
          <div className="w-full max-w-[800px] aspect-[4/3] overflow-hidden">
            <iframe
              src="https://lottie.host/embed/8dd7ef03-638c-45d8-b824-72b60af952bf/o4i0xm2aiE.lottie"
              className="w-full h-full"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Generate;