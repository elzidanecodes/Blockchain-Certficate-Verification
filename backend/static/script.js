let generated_qr_code;

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

  console.log("Uploading certificate data:", data);

  try {
    const res = await fetch(
      "http://127.0.0.1:5000/certificate/generate_certificate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }
    );

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "Failed to upload certificate data");
    }

    const { certificate_id, download_url } = await res.json();
    console.log("Certificate ID:", certificate_id);
    console.log("Download URL:", download_url);

    // Set download link
    const certificateLink = document.getElementById("downloadLink");
    certificateLink.href = `http://127.0.0.1:5000${download_url}`;
    certificateLink.style.display = "block";

    return true;
  } catch (error) {
    console.error("Error uploading certificate data:", error);
    alert("Failed to upload certificate data. Please try again.");
    return false;
  }
}

async function generateCertificate() {
  const name = document.getElementById("name").value;
  const coursename = document.getElementById("coursename").value;
  const courseid = document.getElementById("courseid").value;
  const instname = document.getElementById("instname").value;
  const startdate = document.getElementById("startdate").value;
  const enddate = document.getElementById("enddate").value;

  if (!name) {
    alert("Please enter a name.");
    return;
  }

  const uploadSuccess = await uploadCertificateInfo();
  if (!uploadSuccess) return;

  const certificateCanvas = document.getElementById("certificateCanvas");
  const certificateContext = certificateCanvas.getContext("2d");

  // Load the certificate template image
  const templateImage = new Image();
  templateImage.src = "/static/certificate_template.png";
  templateImage.crossOrigin = "anonymous";

  // Load the generated QR Code image
  const generated_qr_code_img = new Image();
  generated_qr_code_img.crossOrigin = "anonymous";
  generated_qr_code_img.src = generated_qr_code;

  // Wait for both images to load before drawing on the canvas
  Promise.all([
    new Promise((resolve) => {
      templateImage.onload = resolve;
    }),
    new Promise((resolve) => {
      generated_qr_code_img.onload = resolve;
    }),
  ])
    .then(() => {
      // Set canvas dimensions
      certificateCanvas.width = templateImage.width;
      certificateCanvas.height = templateImage.height;

      // Draw certificate template
      certificateContext.drawImage(templateImage, 0, 0);

      // Add text
      certificateContext.font = "bold 80px Arial";
      certificateContext.fillStyle = "black";
      certificateContext.fillText(name, 200, 480);
      certificateContext.font = "bold 50px Arial";
      certificateContext.fillText(coursename, 210, 665);
      certificateContext.fillText(courseid, 550, 734);
      certificateContext.fillText(instname, 210, 860);
      certificateContext.fillText(startdate, 400, 935);
      certificateContext.fillText(enddate, 850, 935);

      // Draw QR Code
      certificateContext.drawImage(generated_qr_code_img, 1500, 950, 300, 300);

      // Convert to image & enable download
      const certificateDataURL = certificateCanvas.toDataURL("image/png");
      const certificateLink = document.getElementById("downloadLink");
      certificateLink.href = certificateDataURL;
      console.log("Certificate generated, showing download button...");
      certificateLink.style.display = "block";
    })
    .catch((error) => {
      console.error("Error loading images:", error);
      alert("Failed to load images. Please try again.");
    });
}
