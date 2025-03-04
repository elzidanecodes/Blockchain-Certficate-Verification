document.getElementById("certificateForm").addEventListener("submit", async function(e) {
    e.preventDefault();  // Mencegah form dikirim sebagai GET

    let formData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        coursename: document.getElementById("coursename").value,
        institution: document.getElementById("institution").value,
        startdate: document.getElementById("startdate").value,
        enddate: document.getElementById("enddate").value
    };

    try {
        const response = await fetch("http://127.0.0.1:5000/certificate/generate_certificate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"  // Pastikan format JSON
            },
            body: JSON.stringify(formData)  // Ubah objek menjadi string JSON
        });

        const data = await response.json();

        if (response.ok) {
            let resultDiv = document.getElementById("result");
            resultDiv.innerHTML = `
                <p style='color:green;'>${data.message} ✅</p>
                <p><strong>Blockchain Hash:</strong> ${data.hash}</p>
                <a id="downloadLink" href='${data.download_url}' download>
                    <button>Download Certificate</button>
                </a>
            `;
        } else {
            throw new Error(data.error || "Failed to generate certificate");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to generate certificate. Please try again.");
    }
});



document.getElementById("uploadForm").addEventListener("submit", function(e) {
    e.preventDefault();

    let fileInput = document.getElementById("file");
    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/verify_certificate", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("verificationResult");
        if (data.is_verified) {
            resultDiv.innerHTML = `<p style='color:green;'>Certificate is valid ✅</p>
                                   <p><strong>Signature:</strong> ${data.signature}</p>
                                   <a href='${data.download_url}' download><button>Download Verified Certificate</button></a>`;
        } else {
            resultDiv.innerHTML = `<p style='color:red;'>${data.message} ❌</p>`;
        }
    })
    .catch(error => console.error("Error:", error));
});
