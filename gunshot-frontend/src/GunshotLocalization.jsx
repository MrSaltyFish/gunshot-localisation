import React, { useState } from "react";
import { Upload, MapPin, Mic, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

const GunshotLocalization = () => {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
  };

  const processAudio = async () => {
    if (!file) return;
    setLoading(true);

    setTimeout(() => {
      setResult({
        location: "Lat: 40.7128, Lon: -74.0060",
        trajectory: "North-East",
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="flex flex-col md:flex-row items-center justify-center min-h-screen bg-gray-900 text-white p-6 md:p-12 w-full">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-3xl font-bold mb-6 md:mb-0 md:mr-8"
      >
        Gunshot Sound Localization
      </motion.h1>

      <div className="w-full max-w-3xl bg-gray-800 p-6 rounded-xl shadow-lg flex flex-col md:flex-row md:gap-6 items-center">
        <label className="cursor-pointer flex flex-col items-center gap-2 border p-4 rounded-md border-gray-500 hover:border-red-500 transition w-full text-center">
          <Upload className="h-6 w-6" />
          <span>{file ? file.name : "Upload Audio File"}</span>
          <input
            type="file"
            className="hidden"
            accept="audio/*"
            onChange={handleFileUpload}
          />
        </label>

        <button
          className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded w-full h-full flex flex-col items-center gap-2 border p-4"
          onClick={processAudio}
          disabled={!file || loading}
        >
          {loading ? (
            <Loader2 className="animate-spin inline-block mr-2" />
          ) : (
            "Process Audio"
          )}
        </button>

        {result && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-center w-full"
          >
            <p>
              <MapPin className="inline" /> <strong>Location:</strong>{" "}
              {result.location}
            </p>
            <p>
              <Mic className="inline" /> <strong>Trajectory:</strong>{" "}
              {result.trajectory}
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default GunshotLocalization;
