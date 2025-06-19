import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import Icon from "../icons/Icon";
import CircularProgress from "../components/CircularProgress";
import Swal from "sweetalert2";

const Validation = () => {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [currentStep, setCurrentStep] = useState(undefined);
  const [isStepFailed, setIsStepFailed] = useState(false);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [durations, setDurations] = useState({});
  const fileInputRef = useRef(null);
  const controllerRef = useRef(null);
  const { certificate_id } = useParams();

  const handleReset = () => {
    if (controllerRef.current) {
      controllerRef.current.abort(); // stop verifikasi backend
    }
    setImage(null);
    setResult(null);
    setCurrentStep(undefined);
    setCompletedSteps([]);
    setDurations({});
    setIsStepFailed(false);
    if (fileInputRef.current) fileInputRef.current.value = "";

    Swal.fire({
      icon: "info",
      title: "Dibatalkan",
      text: "Proses verifikasi telah dihentikan.",
      timer: 1800,
      showConfirmButton: false,
    });
  };

  const handleUpload = async () => {
    if (!image) return;

    controllerRef.current = new AbortController();
    setCompletedSteps([0]);

    const formData = new FormData();
    formData.append("file", image);

    try {
      const response = await fetch("https://localhost:5000/verify_certificate", {
        method: "POST",
        body: formData,
        signal: controllerRef.current.signal,
      });

      const data = await response.json();

      if (data.already_verified) {
        Swal.fire({
          icon: "info",
          title: "Sudah Diverifikasi",
          text: `${"Sertifikat ini sudah diverifikasi sebelumnya pada"} (${
            data.verified_at
          })`,
          confirmButtonColor: "#3085d6",
          confirmButtonText: "OK",
        }).then(() => {
          handleReset();
        });
        return;
      }

      setResult({
        ...data,
        source: "upload",
      });

      if (data.valid) {
        Swal.fire({
          icon: "success",
          title: "Sertifikat Valid",
          text: data.note || "Sertifikat berhasil diverifikasi.",
          confirmButtonColor: "#3085d6",
          confirmButtonText: "OK",
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Verifikasi Gagal",
          text: "Sertifikat tidak valid atau data tidak sesuai.",
          confirmButtonColor: "#DF0404",
          confirmButtonText: "Tutup",
        });
      }

      const stepDur = data.step_durations || {};
      const stepMap = {
        1: 1000,
        2: stepDur.extract || 1000,
        3: stepDur.blockchain || 1000,
        4: stepDur.rsa || 1000,
        5: stepDur.generate || 1000,
      };

      for (let i = 2; i <= 4; i++) {
        setCurrentStep(i);
        await new Promise((res) => setTimeout(res, stepMap[i]));
        setCompletedSteps((prev) =>
          prev.includes(i - 1) ? prev : [...prev, i - 1]
        );
      }

      setCurrentStep(5);
      await new Promise((res) => setTimeout(res, stepMap[5]));

      if (data.valid) {
        setCompletedSteps((prev) =>
          prev.includes(3) ? [...prev, 4] : [...prev, 3, 4]
        );
      } else {
        setIsStepFailed(true);
      }
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("✅ Verifikasi dibatalkan.");
      } else {
        console.error("⚠️ Gagal verifikasi:", error);
      }
    }
  };

  // Mode scan QR: langsung fetch data dari backend
  useEffect(() => {
    if (!certificate_id) return;

    fetch(`https://localhost:5000/api/verify/${certificate_id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Sertifikat belum diverifikasi.");
        return res.json();
      })
      .then((data) => {
        if (data.valid === true) {
          setResult({
            ...data,
            image_base64: null,
            source: "qr",
          });
          setCompletedSteps([0, 1, 2, 3, 4]);

          Swal.fire({
            icon: "success",
            title: "Sertifikat Valid",
            text: `${"Sertifikat ini telah diverifikasi pada"} (${
              data.verified_at
            })`,
            confirmButtonColor: "#3085d6",
            confirmButtonText: "OK",
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Sertifikat Tidak Valid",
            text: data.message,
          });
        }
      })
      .catch((err) => {
        setResult({
          valid: false,
          source: "qr",
        });
        Swal.fire({
          icon: "info",
          title: "Belum Diverifikasi",
          text: "Sertifikat ini belum diverifikasi oleh admin.",
        });
      });
  }, [certificate_id]);

  useEffect(() => {
    const role = localStorage.getItem("role");

    if (!certificate_id && role !== "admin") {
      Swal.fire({
        title: "Akses Terbatas",
        text: "Halaman ini hanya bisa diakses melalui scan QR Code di sertifikat.",
        icon: "info",
        confirmButtonText: "Saya Mengerti",
      });
    }
  }, []);

  const steps = [
    "Unggah File",
    "Ekstrak Data Gambar",
    "Get Data Blockchain",
    "Verifikasi Sertifikat",
    "Generate Sertifikat",
  ];

  return (
    <div className="flex flex-col min-h-screen px-14 py-7 dark:bg-gray-900 dark:text-white">
      <h2 className="text-[30px] font-bold text-blue-dark mb-4 md:text-[50px]">
        Verifikasi Sertifikat
      </h2>

      {/* Verifikasi Upload */}
      {localStorage.getItem("role") === "admin" && (
        <div className="bg-white shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 mb-4 dark:bg-gray-800">
          <div className="px-4 py-8 grid grid-cols-1 md:grid-cols-[240px_1fr] gap-8">
            <div className="space-y-6">
              <ul className="relative space-y-10 pl-9">
                {steps.map((step, idx) => {
                  const isCompleted = completedSteps.includes(idx);
                  const isCurrent = idx === currentStep;
                  const isStepError = (idx === 3 || idx === 4) && isStepFailed;

                  const statusClass = isStepError
                    ? "bg-red-dark text-white"
                    : isCompleted
                    ? "bg-green-success text-white"
                    : isCurrent
                    ? "bg-gray-unsuccess text-white"
                    : "bg-gray-unsuccess text-white";

                  return (
                    <li key={idx} className="relative pl-6">
                      {idx !== steps.length - 1 && (
                        <div
                          className={`absolute left-[19px] top-[45px] h-[calc(100%+4px)] w-[2px] z-0 ${
                            isStepFailed && (idx === 3 || idx === 4)
                              ? "bg-red-dark"
                              : isCompleted
                              ? "bg-green-success"
                              : "bg-gray-unsuccess"
                          }`}
                        />
                      )}

                      <div className="absolute left-0 top-1">
                        {isCurrent && !isCompleted && !isStepError ? (
                          <CircularProgress
                            duration={durations[idx] || 1000}
                            onDone={() => {
                              if (!completedSteps.includes(idx)) {
                                setCompletedSteps((prev) => [...prev, idx]);
                              }
                            }}
                          />
                        ) : (
                          <div
                            className={`w-[40px] h-[40px] rounded-50 flex items-center justify-center ${statusClass}`}
                          >
                            <Icon
                              name="checklist"
                              className="w-[22px] h-[22px]"
                            />
                          </div>
                        )}
                      </div>

                      <div className="pl-6">
                        <span className="text-sm text-gray-unsuccess dark:text-gray-500">
                          Langkah {idx + 1}
                        </span>
                        <br />
                        <span className="text-black text-base font-semibold dark:text-white">
                          {step}
                        </span>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>

            <div className="space-y-6">
              <h2 className="text-lg font-semibold mb-2">Unggah File</h2>
              <div
                onDrop={(e) => {
                  e.preventDefault();
                  const file = e.dataTransfer.files[0];
                  if (file) {
                    setImage(file);
                    setResult(null);
                    setCompletedSteps([]);
                    setCurrentStep(undefined);
                  }
                }}
                onDragOver={(e) => e.preventDefault()}
                className="flex flex-col items-center justify-center border-2 border-dashed border-blue-dark rounded-10 cursor-pointer bg-blue-light md:w-[130px] md:h-[90px] lg:w-[530px] lg:h-[300px] dark:bg-gray-700 dark:border-gray-500"
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Icon
                    name="image"
                    className="text-blue md:w-[35px] md:h-[35px] lg:w-[55px] lg:h-[55px] mb-2"
                    style={{ width: "50px", height: "50px" }}
                  />
                  <p className="mb-2 text-lg text-gray-500 md:text-2xl">
                    Drag & drop files or{" "}
                    <span className="font-semibold text-blue-dark underline">
                      Browse
                    </span>
                  </p>
                  <p className="text-xs text-gray-500">
                    Supported formats: PNG, JPG, JPEG
                  </p>
                </div>

                {image && (
                  <div className="text-center mt-2 text-sm text-blue-dark font-medium">
                    File terpilih: <span className="italic">{image.name}</span>
                  </div>
                )}

                <input
                  ref={fileInputRef}
                  id="dropzone-file"
                  type="file"
                  className="hidden"
                  accept="image/png, image/jpeg"
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      setImage(file);
                      setResult(null);
                      setCompletedSteps([]);
                      setCurrentStep(undefined);
                    }
                  }}
                />
              </div>

              <div className="mt-4 flex gap-2">
                <button
                  onClick={handleUpload}
                  className="bg-blue-dark text-white rounded-5 md:px-6 py-2"
                >
                  Verifikasi
                </button>
                <button
                  onClick={handleReset}
                  className="border border-blue-dark px-7 py-2 rounded-5"
                >
                  Batal
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hasil */}
      {result && result.image_base64 && (
        <div className="bg-green-50 shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-4 py-8 border border-green-200 dark:bg-gray-800 dark:text-white">
          <div className="flex flex-col items-start px-6">
            <h3 className="font-semibold text-2xl mb-4 text-blue-dark">
              Hasil Verifikasi Sertifikat
            </h3>
            <img
              src={`data:image/png;base64,${result.image_base64}`}
              alt="Verified"
              className="rounded-10 md: w-[500px] lg:w-[688px] h-auto mb-6"
            />
            <div className="flex gap-4">
              <a
                href={`data:image/png;base64,${result.image_base64}`}
                download={`${result.certificate_id}_verified.png`}
                className=" inline-block bg-green-light border-2 border-green-dark text-green-dark rounded-10 md:px-4 py-2 lg:px-7   hover:bg-green-dark hover:text-white transition duration-300"
              >
                Download Sertifikat
              </a>
              <a
                href={`${result.ipfs_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className=" inline-block bg-blue-light text-blue-dark rounded-10 border border-blue-dark md:px-4 py-2 lg:px-7 hover:bg-blue-dark hover:text-white transition duration-300"
              >
                Lihat di IPFS
              </a>
            </div>
          </div>
          <div className="flex flex-col items-start px-6 py-6">
            <h3 className="font-semibold text-lg mb-4 text-blue-dark ">
              Detail Sertifikat
            </h3>
            <ul className="text-sm space-y-4">
              <li className="flex items-center gap-2">
                <strong>Status:</strong>
                {result.valid ? (
                  <span className="flex items-center gap-2 text-green-success font-medium">
                    <span className="bg-green-success text-white rounded-50">
                      <Icon name="checklist" className="w-[15px] h-[15px]" />
                    </span>
                    Sertifikat valid!
                  </span>
                ) : (
                  <span className="flex items-center gap-2 text-red-dark font-medium">
                    <span className="bg-red-dark text-white rounded-50">
                      <Icon name="close" className="w-[15px] h-[15px]" />
                    </span>
                    Sertifikat tidak valid
                  </span>
                )}
              </li>
              <li>
                <strong>Certificate ID:</strong> {result.certificate_id}
              </li>
              <li>
                <strong>No Sertifikat:</strong> {result.no_sertifikat}
              </li>
              <li>
                <strong>Nama:</strong> {result.name}
              </li>
              <li>
                <strong>Student ID:</strong> {result.student_id}
              </li>
              <li>
                <strong>Department:</strong> {result.department}
              </li>
              <li>
                <strong>Tanggal Tes:</strong> {result.test_date}
              </li>
              <li>
                <strong>Hash MD5:</strong> {result.hash}
              </li>
              <li className="flex items-center gap-2">
                <strong>Signature:</strong>{" "}
                <span className="flex items-center gap-2 text-green-success font-medium">
                  <span className="bg-green-success text-white rounded-50">
                    <Icon name="checklist" className="w-[15px] h-[15px]" />
                  </span>
                  Diverifikasi oleh RSA Signature
                </span>
              </li>
            </ul>
          </div>
        </div>
      )}
      {/* Gagal Verifikasi */}
      {result && result.source === "upload" && !result.image_base64 && (
        <div className="bg-red-50 shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-8 py-8 border border-red-200">
          <div className="flex flex-col justify-center items-start px-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="bg-red-200 p-3 rounded-50 animate-pulse">
                <Icon
                  name="close"
                  className="w-[24px] h-[24px] text-red-dark"
                />
              </div>
              <h3 className="font-bold text-2xl text-red-700">
                Sertifikat Tidak Valid
              </h3>
            </div>
            <p className="text-red-dark text-sm">
              Gambar yang Anda unggah tidak cocok dengan data yang disimpan di
              blockchain. Pastikan Anda menggunakan gambar sertifikat asli tanpa
              modifikasi.
            </p>
          </div>
          <div className="flex justify-center items-center p-4">
            <div className="w-full max-w-[200px] aspect-square overflow-hidden ">
              <iframe
                src="https://lottie.host/embed/07456d93-dbf7-4796-a38b-fc36b27605f1/nVMOALJJDT.lottie"
                className="w-full h-full"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        </div>
      )}

      {!certificate_id && localStorage.getItem("role") !== "admin" && (
        <div className="bg-red-50 shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-8 py-8 border border-red-200">
          <div className="flex flex-col justify-center items-start px-6 space-y-8">
            <div className="flex items-center gap-3">
              <div className="bg-red-200 p-3 rounded-50 animate-pulse">
                <Icon
                  name="notif"
                  className="w-[30px] h-[30px] text-red-dark"
                />
              </div>
              <h3 className="font-bold text-2xl text-red-700">
                Scan QRCode Sertifikat Anda
              </h3>
            </div>
            <p className="text-red-dark text-sm">
              Menu ini hanya bisa digunakan jika Anda melakukan scan QR dari
              sertifikat. Silhakan scan QR untuk menampilkan hasil verifikasi.
            </p>
          </div>
          <div className="flex justify-center items-center p-4">
            <div className="w-full max-w-[300px] aspect-square overflow-hidden ">
              <iframe
                src="https://lottie.host/embed/a8e408dc-8e2b-42f8-a9db-fea306e741e9/PwbOIWvmB6.lottie"
                className="w-full h-full"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        </div>
      )}

      {/* Hasil Scan QRcode */}
      {result &&
        !result.image_base64 &&
        result.source === "qr" &&
        result.valid && (
          <div className="bg-green-50 shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-4 py-8 border border-green-200 dark:bg-gray-800 dark:text-white">
            <div className="flex flex-col items-start px-6">
              <h3 className="font-semibold text-2xl mb-4 text-blue-dark">
                Sertikat Telah Diverifikasi Pada {result.verified_at}
              </h3>
              <div
                className="relative w-full rounded-10 overflow-hidden mb-6 flex justify-center"
                onContextMenu={(e) => e.preventDefault()}
              >
                <img
                  src={result.ipfs_url}
                  alt="Sertifikat"
                  className={`w-full max-w-[680px] h-auto rounded-10 select-none pointer-events-none mx-auto ${
                    localStorage.getItem("role") !== "admin" ? "blur-sm" : ""
                  }`}
                  onContextMenu={(e) => e.preventDefault()}
                  draggable={false}
                />
              </div>
            </div>
            <div className="flex flex-col items-start px-6 py-6">
              <h3 className="font-semibold text-lg mb-4 text-blue-dark ">
                Detail Sertifikat
              </h3>
              <ul className="text-sm space-y-4">
                <li className="flex items-center gap-2">
                  <strong>Status:</strong>
                  <span className="flex items-center gap-2 text-green-success font-medium">
                    <span className="bg-green-success text-white rounded-50">
                      <Icon name="checklist" className="w-[15px] h-[15px]" />
                    </span>
                    Sertifikat valid!
                  </span>
                </li>
                <li>
                  <strong>Certificate ID:</strong> {result.certificate_id}
                </li>
                <li>
                  <strong>No Sertifikat:</strong> {result.no_sertifikat}
                </li>
                <li>
                  <strong>Hash MD5:</strong> {result.hash}
                </li>
                <li className="flex items-center gap-2">
                  <strong>Signature:</strong>
                  <span className="flex items-center gap-2 text-green-success font-medium">
                    <span className="bg-green-success text-white rounded-50">
                      <Icon name="checklist" className="w-[15px] h-[15px]" />
                    </span>
                    Diverifikasi oleh RSA Signature
                  </span>
                </li>
              </ul>
            </div>
          </div>
        )}

      {result &&
        !result.image_base64 &&
        result.source === "qr" &&
        result.valid === false && (
          <div className="bg-red-50 shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-8 py-8 border border-red-200">
            <div className="flex flex-col justify-center items-start px-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="bg-red-200 p-3 rounded-50 animate-pulse">
                  <Icon
                    name="close"
                    className="w-[30px] h-[30px] text-red-dark"
                  />
                </div>
                <h3 className="font-bold text-2xl text-red-700">
                  Sertifikat Belum Diverifikasi
                </h3>
              </div>
              <p className="text-red-dark text-sm">
                Sertifikat ini belum diverifikasi di sistem. Silakan hubungi
                administrator untuk memverifikasi sertifikat Anda.
              </p>
            </div>
            <div className="flex justify-center items-center p-4">
              <div className="w-full max-w-[200px] aspect-square overflow-hidden ">
                <iframe
                  src="https://lottie.host/embed/07456d93-dbf7-4796-a38b-fc36b27605f1/nVMOALJJDT.lottie"
                  className="w-full h-full"
                  allowFullScreen
                ></iframe>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default Validation;
