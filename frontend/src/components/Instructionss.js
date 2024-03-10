import React from 'react';
import './instructions.css';

const Instructionss = () => {
  const handleDownload = () => {
    const downloadFile = (fileUrl, fileName) => {
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = fileName;
      link.click();
    };

    downloadFile(process.env.PUBLIC_URL + '/zeroshield.exe', 'zeroshield.exe');
    downloadFile(process.env.PUBLIC_URL + '/npcap.exe', 'npcap.exe');
  };

  return (
    <div className="instructions-container">
    </div>
  );
};

export default Instructionss;
