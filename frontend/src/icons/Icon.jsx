import React from "react";

const Icon = ({ name, className }) => {
  const icons = {
    // lokal PNG/SVG di public/icons/
    document: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="file-alt">
        <path
          fill="currentColor"
          d="M9,10h1a1,1,0,0,0,0-2H9a1,1,0,0,0,0,2Zm0,2a1,1,0,0,0,0,2h6a1,1,0,0,0,0-2ZM20,8.94a1.31,1.31,0,0,0-.06-.27l0-.09a1.07,1.07,0,0,0-.19-.28h0l-6-6h0a1.07,1.07,0,0,0-.28-.19.32.32,0,0,0-.09,0A.88.88,0,0,0,13.05,2H7A3,3,0,0,0,4,5V19a3,3,0,0,0,3,3H17a3,3,0,0,0,3-3V9S20,9,20,8.94ZM14,5.41,16.59,8H15a1,1,0,0,1-1-1ZM18,19a1,1,0,0,1-1,1H7a1,1,0,0,1-1-1V5A1,1,0,0,1,7,4h5V7a3,3,0,0,0,3,3h3Zm-3-3H9a1,1,0,0,0,0,2h6a1,1,0,0,0,0-2Z"
        ></path>
      </svg>
    ),
    document_verified: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        id="approve-file"
      >
        <path
          fill="currentColor"
          d="M11.5,20h-6a1,1,0,0,1-1-1V5a1,1,0,0,1,1-1h5V7a3,3,0,0,0,3,3h3v5a1,1,0,0,0,2,0V9s0,0,0-.06a1.31,1.31,0,0,0-.06-.27l0-.09a1.07,1.07,0,0,0-.19-.28h0l-6-6h0a1.07,1.07,0,0,0-.28-.19.29.29,0,0,0-.1,0A1.1,1.1,0,0,0,11.56,2H5.5a3,3,0,0,0-3,3V19a3,3,0,0,0,3,3h6a1,1,0,0,0,0-2Zm1-14.59L15.09,8H13.5a1,1,0,0,1-1-1ZM7.5,14h6a1,1,0,0,0,0-2h-6a1,1,0,0,0,0,2Zm4,2h-4a1,1,0,0,0,0,2h4a1,1,0,0,0,0-2Zm-4-6h1a1,1,0,0,0,0-2h-1a1,1,0,0,0,0,2Zm13.71,6.29a1,1,0,0,0-1.42,0l-3.29,3.3-1.29-1.3a1,1,0,0,0-1.42,1.42l2,2a1,1,0,0,0,1.42,0l4-4A1,1,0,0,0,21.21,16.29Z"
        ></path>
      </svg>
    ),
    search: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="search">
        <path
          fill="currentColor"
          stroke="currentColor"
          strokeWidth="1"
          d="M21.71,20.29,18,16.61A9,9,0,1,0,16.61,18l3.68,3.68a1,1,0,0,0,1.42,0A1,1,0,0,0,21.71,20.29ZM11,18a7,7,0,1,1,7-7A7,7,0,0,1,11,18Z"
        ></path>
      </svg>
    ),
    generate: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        id="add-new-file"
      >
        <path
          fill="currentColor"
          d="M20,18H19V17a1,1,0,0,0-2,0v1H16a1,1,0,0,0,0,2h1v1a1,1,0,0,0,2,0V20h1a1,1,0,0,0,0-2Zm-7,2H6a1,1,0,0,1-1-1V5A1,1,0,0,1,6,4h5V7a3,3,0,0,0,3,3h3v3a1,1,0,0,0,2,0V9s0,0,0-.06a1.31,1.31,0,0,0-.06-.27l0-.09a1.07,1.07,0,0,0-.19-.28h0l-6-6h0a1.07,1.07,0,0,0-.28-.19.29.29,0,0,0-.1,0A1.1,1.1,0,0,0,12.06,2H6A3,3,0,0,0,3,5V19a3,3,0,0,0,3,3h7a1,1,0,0,0,0-2ZM13,5.41,15.59,8H14a1,1,0,0,1-1-1ZM8,8a1,1,0,0,0,0,2H9A1,1,0,0,0,9,8Zm5,8H8a1,1,0,0,0,0,2h5a1,1,0,0,0,0-2Zm1-4H8a1,1,0,0,0,0,2h6a1,1,0,0,0,0-2Z"
        ></path>
      </svg>
    ),
    home: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="home">
        <path
          fill="currentColor"
          d="M20,8h0L14,2.74a3,3,0,0,0-4,0L4,8a3,3,0,0,0-1,2.26V19a3,3,0,0,0,3,3H18a3,3,0,0,0,3-3V10.25A3,3,0,0,0,20,8ZM14,20H10V15a1,1,0,0,1,1-1h2a1,1,0,0,1,1,1Zm5-1a1,1,0,0,1-1,1H16V15a3,3,0,0,0-3-3H11a3,3,0,0,0-3,3v5H6a1,1,0,0,1-1-1V10.25a1,1,0,0,1,.34-.75l6-5.25a1,1,0,0,1,1.32,0l6,5.25a1,1,0,0,1,.34.75Z"
        ></path>
      </svg>
    ),
    image: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        enable-background="new 0 0 24 24"
        viewBox="0 0 24 24"
        id="image"
      >
        <path
          fill="#B9E3FF"
          d="M13.5 9a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"
        ></path>
        <path
          fill="#59ACE3"
          d="M19 2H5a3.009 3.009 0 0 0-3 3v8.86l3.88-3.88a3.075 3.075 0 0 1 4.24 0l2.871 2.887.888-.888a3.008 3.008 0 0 1 4.242 0L22 15.86V5a3.009 3.009 0 0 0-3-3zm-5.5 7a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"
        ></path>
        <path
          fill="#197BBD"
          d="M10.12 9.98a3.075 3.075 0 0 0-4.24 0L2 13.86V19a3.009 3.009 0 0 0 3 3h14c.815 0 1.595-.333 2.16-.92L10.12 9.98z"
        ></path>
        <path
          fill="#B9E3FF"
          d="m22 15.858-3.879-3.879a3.008 3.008 0 0 0-4.242 0l-.888.888 8.165 8.209c.542-.555.845-1.3.844-2.076v-3.142z"
        ></path>
      </svg>
    ),
    success: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        id="check-circle"
      >
        <path
          fill="currentColor"
          d="M14.72,8.79l-4.29,4.3L8.78,11.44a1,1,0,1,0-1.41,1.41l2.35,2.36a1,1,0,0,0,.71.29,1,1,0,0,0,.7-.29l5-5a1,1,0,0,0,0-1.42A1,1,0,0,0,14.72,8.79ZM12,2A10,10,0,1,0,22,12,10,10,0,0,0,12,2Zm0,18a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
        ></path>
      </svg>
    ),
    checklist: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="check">
        <path
          fill="currentColor"
          d="M18.71,7.21a1,1,0,0,0-1.42,0L9.84,14.67,6.71,11.53A1,1,0,1,0,5.29,13l3.84,3.84a1,1,0,0,0,1.42,0l8.16-8.16A1,1,0,0,0,18.71,7.21Z"
        ></path>
      </svg>
    ),

    close: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" id="times">
        <path
          fill="currentColor"
          d="M13.41,12l4.3-4.29a1,1,0,1,0-1.42-1.42L12,10.59,7.71,6.29A1,1,0,0,0,6.29,7.71L10.59,12l-4.3,4.29a1,1,0,0,0,0,1.42,1,1,0,0,0,1.42,0L12,13.41l4.29,4.3a1,1,0,0,0,1.42,0,1,1,0,0,0,0-1.42Z"
        ></path>
      </svg>
    ),
  };

  const icon = icons[name];

  if (!icon) return null;

  // ⬇️ Jika icon berupa string (path), render <img>
  if (typeof icon === "string") {
    return <img src={icon} alt={name} className={className} loading="lazy" />;
  }

  return React.cloneElement(icon, { className });
};

export default Icon;
