// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateVerification {
    struct Certificate {
        string certificateHash;
        address owner;
        uint256 timestamp;
    }

    mapping(string => Certificate) public certificates;
    uint256 public documentCount; // Counter for the number of documents

    event CertificateAdded(string indexed certificateHash, address indexed owner, uint256 timestamp);

    function addCertificate(string memory _certificateHash) public {
        require(bytes(_certificateHash).length > 0, "Certificate hash cannot be empty");
        require(certificates[_certificateHash].owner == address(0), "Document already exists");

        certificates[_certificateHash] = Certificate({
            certificateHash: _certificateHash,
            owner: msg.sender,
            timestamp: block.timestamp
        });

        documentCount++; // Increment the document count

        emit CertificateAdded(_certificateHash, msg.sender, block.timestamp);
    }

    function verifyCertificate(string memory _certificateHash) public view returns (bool) {
        return certificates[_certificateHash].owner != address(0);
    }
}