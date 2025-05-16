async function uploadCertificateInfo() {
  const data = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    phnumber: document.getElementById("phnumber").value,
    coursename: document.getElementById("coursename").value,
    courseid: document.getElementById("courseid").value,
    instname: document.getElementById("instname").value,
    startdate: document.getElementById("startdate").value,
    enddate: document.getElementById("enddate").value,
  };

  console.log("📤 Mengirim data ke backend:", data);

  try {
    const res = await fetch("http://127.0.0.1:5000/certificate/generate_certificate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "Gagal generate sertifikat.");
    }

    const { certificate_id, download_url } = await res.json();
    console.log("✅ Sertifikat ID:", certificate_id);

    const certificateLink = document.getElementById("downloadLink");
    certificateLink.href = `http://127.0.0.1:5000${download_url}`;
    certificateLink.style.display = "block";

    alert("✅ Sertifikat berhasil dibuat. Klik link untuk mengunduh.");
  } catch (error) {
    console.error("❌ Error:", error);
    alert("Gagal upload data sertifikat.");
  }
}