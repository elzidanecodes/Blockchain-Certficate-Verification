import { useState, useRef } from "react";
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


  const handleReset = () => {
    if (controllerRef.current) {
      controllerRef.current.abort(); // stop verifikasi backend
    }
    setImage(null);
    setResult(null);
    setCurrentStep(0);
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
      const response = await fetch(
        "http://localhost:5000/verification/verify_certificate",
        {
          method: "POST",
          body: formData,
          signal: controllerRef.current.signal,
        }
      );

      const data = await response.json();
      setResult(data);

      if (!data.valid) {
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

  const steps = [
    "Unggah File",
    "Ekstrak Data Gambar",
    "Get Data Blockchain",
    "Verifikasi Sertifikat",
    "Generate Sertifikat",
  ];

  return (
    <div className="flex flex-col min-h-screen px-6 py-4 dark:bg-gray-900 dark:text-white">
      <h2 className="text-[30px] font-bold text-blue-dark mb-4 md:text-[50px]">
        Verifikasi Sertifikat
      </h2>
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
            <label
              htmlFor="dropzone-file"
              className="flex flex-col items-center justify-center w-[330px] h-[208px] border-2 border-dashed border-blue-dark rounded-10 cursor-pointer bg-blue-light md:w-[530px] md:h-[250px] lg:w-[500px] lg:h-[300px] dark:bg-gray-700 dark:border-gray-500"
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Icon
                  name="image"
                  className="text-blue md:w-[35px] lg:w-[55px]"
                />
                <p className="mb-2 text-lg  text-gray-500 md:text-2xl">
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
            </label>
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

      {/* Hasil */}
      {/* Hasil */}
      {result && result.image_base64 && (
        <div className="bg-white shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-4 py-8 dark:bg-gray-800 dark:text-white">
          <div className="flex flex-col items-start px-6">
            <h3 className="font-semibold text-2xl mb-4 text-blue-dark">
              Hasil Verifikasi Sertifikat
            </h3>
            <img
              src={`data:image/png;base64,${result.image_base64}`}
              alt="Verified"
              className="rounded-10 md: w-[500px] lg:w-[688px] h-auto"
            />
            <a
              href={`data:image/png;base64,${result.image_base64}`}
              download={`${result.certificate_id}_verified.png`}
              className="mt-4 inline-block bg-green-light border-2 border-green-dark text-green-dark rounded-10 md:px-4 py-2 lg:px-2   hover:bg-green-dark hover:text-white transition duration-300"
            >
              Download Sertifikat
            </a>
          </div>
          <div className="flex flex-col items-start px-6 py-6">
            <h3 className="font-semibold text-lg mb-4 text-blue-dark ">
              Detail Sertifikat
            </h3>
            <ul className="text-sm space-y-4">
              <li>
                <strong>Status:</strong>{" "}
                <span
                  className={
                    result.valid
                      ? "text-green-success font-medium"
                      : "text-red-dark font-bold"
                  }
                >
                  {result.valid ? "✅ Sertifikat valid" : "❌ Tidak valid"}
                </span>
              </li>
              <li>
                <strong>Cert ID:</strong> {result.certificate_id}
              </li>
              <li>
                <strong>Nama:</strong> {result.name}
              </li>
              <li>
                <strong>Course ID:</strong> {result.course_id}
              </li>
              <li>
                <strong>Periode:</strong> {result.start_date} –{" "}
                {result.end_date}
              </li>
              <li>
                <strong>Diverifikasi Pada:</strong>{" "}
                {new Date(result.verified_at).toLocaleString("id-ID", {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              </li>
              <li>
                <strong>Hash MD5:</strong> {result.hash}
              </li>
              <li>
                <strong>Signature:</strong>{" "}
                <span className="text-green-success">
                  ✔ Diverifikasi menggunakan RSA
                </span>
              </li>
            </ul>
          </div>
        </div>
      )}
      {result && !result.image_base64 && (
        <div className="bg-white shadow-md rounded-30 grid grid-cols-1 md:grid-cols-2 gap-10 px-6 py-6">
          <div className="flex flex-col items-start px-6">
            <h3 className="font-semibold text-2xl mb-4 text-blue-dark">
              Hasil Verifikasi Sertifikat
            </h3>
            <p className="text-red-dark font-bold">
              Sertifikat tidak valid atau data tidak sesuai.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Validation;
