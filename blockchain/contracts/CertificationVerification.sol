// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

contract CertificateVerification {
    struct Certificate {
        string certificateId;
        string certificateSignature; 
    }

    mapping(string => Certificate) public certificates;
    uint256 public certificateCounter;

    // Fungsi internal untuk membuat ID format CERT-001
    function generateCertificateID() private returns (string memory) {
        certificateCounter++;
        return string(abi.encodePacked("CERT-", zeroPad(certificateCounter, 3)));
    }

    // Simpan sertifikat baru
    function addCertificate(string memory _signature) public returns (string memory) {
        require(bytes(_signature).length > 0, "Signature required");

        string memory certID = generateCertificateID();
        certificates[certID] = Certificate(certID, _signature);
        return certID;
    }

    // Ambil data sertifikat
    function getCertificate(string memory _certificateId) public view returns (bool, string memory, string memory) {
        Certificate memory cert = certificates[_certificateId];
        if (bytes(cert.certificateId).length == 0) {
            return (false, "", "");
        }
        return (true, cert.certificateId, cert.certificateSignature);
    }

     // Fungsi untuk konversi uint ke string (tanpa padding)
    function uintToStr(uint256 _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        j = _i;
        while (j != 0) {
            bstr[--k] = bytes1(uint8(48 + j % 10));
            j /= 10;
        }
        return string(bstr);
    }

    // Fungsi untuk konversi uint ke string dengan zero-padding
    function zeroPad(uint256 number, uint256 digits) internal pure returns (string memory) {
        bytes memory numberStr = bytes(uintToStr(number));
        uint256 length = numberStr.length;

        if (length >= digits) {
            return string(numberStr);
        }

        bytes memory padded = new bytes(digits);
        uint256 padLength = digits - length;

        for (uint256 i = 0; i < padLength; i++) {
            padded[i] = "0";
        }

        for (uint256 i = 0; i < length; i++) {
            padded[padLength + i] = numberStr[i];
        }

        return string(padded);
    }
}
