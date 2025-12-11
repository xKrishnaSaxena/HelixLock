import { useState } from "react";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("encrypt"); // 'encrypt' or 'decrypt'

  // Default Parameters
  const [params, setParams] = useState({
    a0: 0.1,
    b0: 0.2,
    mu_a: 3.99,
    mu_b: 3.99,
    z0: 0.1,
    q0: 0.2,
    wz: 5,
    wq: 5,
  });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResultUrl(null);
    }
  };

  const handleParamChange = (e) => {
    setParams({ ...params, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);

    // Append all parameters to FormData
    Object.keys(params).forEach((key) => {
      formData.append(key, params[key]);
    });

    try {
      // Point to your FastAPI backend
      const endpoint = `http://127.0.0.1:8000/${mode}`;
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        setResultUrl(downloadUrl);
      } else {
        console.error("Error processing image");
      }
    } catch (error) {
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-teal-400 mb-2">
            DNA-Chaos Image Encryption
          </h1>
          <p className="text-gray-400">
            Secure your images using DNA encoding and Chaotic Maps
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Controls Panel */}
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 h-fit">
            <h2 className="text-xl font-semibold mb-4 text-teal-300">
              Configuration
            </h2>

            {/* Mode Switcher */}
            <div className="flex bg-gray-700 rounded-lg p-1 mb-6">
              <button
                onClick={() => setMode("encrypt")}
                className={`flex-1 py-2 rounded-md transition-all ${
                  mode === "encrypt"
                    ? "bg-teal-500 text-white shadow"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                Encrypt
              </button>
              <button
                onClick={() => setMode("decrypt")}
                className={`flex-1 py-2 rounded-md transition-all ${
                  mode === "decrypt"
                    ? "bg-purple-500 text-white shadow"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                Decrypt
              </button>
            </div>

            {/* File Input */}
            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">
                Select Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-teal-300 hover:file:bg-gray-600"
              />
            </div>

            {/* Parameters Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              {Object.keys(params).map((key) => (
                <div key={key}>
                  <label className="text-xs text-gray-500 uppercase">
                    {key}
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name={key}
                    value={params[key]}
                    onChange={handleParamChange}
                    className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm focus:border-teal-500 outline-none"
                  />
                </div>
              ))}
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading || !selectedFile}
              className={`w-full py-3 rounded-lg font-bold text-lg transition-all ${
                loading
                  ? "bg-gray-600 cursor-wait"
                  : mode === "encrypt"
                  ? "bg-teal-600 hover:bg-teal-500"
                  : "bg-purple-600 hover:bg-purple-500"
              }`}
            >
              {loading
                ? "Processing..."
                : `Execute ${mode === "encrypt" ? "Encryption" : "Decryption"}`}
            </button>
          </div>

          {/* Visualization Panel */}
          <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Input Preview */}
            <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 flex flex-col items-center justify-center min-h-[300px]">
              <h3 className="text-gray-400 mb-4">Input Image</h3>
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Input"
                  className="max-h-64 rounded-lg shadow-md object-contain"
                />
              ) : (
                <div className="text-gray-600">No image selected</div>
              )}
            </div>

            {/* Output Result */}
            <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 flex flex-col items-center justify-center min-h-[300px]">
              <h3 className="text-gray-400 mb-4">Result Image</h3>
              {resultUrl ? (
                <div className="flex flex-col items-center">
                  <img
                    src={resultUrl}
                    alt="Result"
                    className="max-h-64 rounded-lg shadow-md object-contain mb-4"
                  />
                  <a
                    href={resultUrl}
                    download={`result.${mode === "encrypt" ? "png" : "jpg"}`}
                    className="text-sm text-teal-300 hover:underline"
                  >
                    Download Image
                  </a>
                </div>
              ) : (
                <div className="text-gray-600">Waiting for process...</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
