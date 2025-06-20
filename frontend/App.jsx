// src/App.jsx
import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [mockResponse, setMockResponse] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append("resume_file", resumeFile);
    formData.append("job_description", jobDesc);
    formData.append("mock_response_text", mockResponse);

    try {
      const res = await axios.post("http://localhost:8000/evaluate_all", formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error during evaluation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Interview Outcome Predictor</h1>

      <label className="block mb-2">Upload Resume (PDF/DOCX):</label>
      <input
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={(e) => setResumeFile(e.target.files[0])}
        className="mb-4"
      />

      <label className="block mb-2">Job Description:</label>
      <textarea
        value={jobDesc}
        onChange={(e) => setJobDesc(e.target.value)}
        className="w-full border p-2 mb-4"
        rows={5}
      />

      <label className="block mb-2">Mock Interview Response (text):</label>
      <textarea
        value={mockResponse}
        onChange={(e) => setMockResponse(e.target.value)}
        className="w-full border p-2 mb-4"
        rows={4}
      />

      <button
        onClick={handleSubmit}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        disabled={loading}
      >
        {loading ? "Evaluating..." : "Submit"}
      </button>

      {result && (
        <div className="mt-6 border-t pt-4">
          <h2 className="text-xl font-semibold mb-2">Results</h2>

          <div className="mb-4">
            <h3 className="font-semibold">Resume Scores:</h3>
            <ul>
              <li>Clarity: {result.resume_scores.clarity}</li>
              <li>Relevance: {result.resume_scores.relevance}</li>
              <li>Structure: {result.resume_scores.structure}</li>
              <li>Feedback: {result.resume_scores.feedback.join(", ")}</li>
            </ul>
          </div>

          <div className="mb-4">
            <h3 className="font-semibold">Mock Evaluation:</h3>
            <ul>
              <li>Tone: {result.mock_evaluation.tone}</li>
              <li>Confidence: {result.mock_evaluation.confidence}</li>
              <li>Relevance: {result.mock_evaluation.relevance}</li>
              <li>Feedback: {result.mock_evaluation.feedback.join(", ")}</li>
            </ul>
          </div>

          <div className="mb-4">
            <h3 className="font-semibold">Prediction:</h3>
            <p>Score: {result.success_prediction.score}</p>
            <p>Reason: {result.success_prediction.reason}</p>
          </div>

          <div>
            <h3 className="font-semibold">Improvement Plan:</h3>
            <ul>
              {result.improvement_plan.suggestions.map((s, i) => (
                <li key={i}>✅ {s}</li>
              ))}
            </ul>
            <p className="mt-2 font-semibold">Resources:</p>
            <ul>
              {result.improvement_plan.resources.map((r, i) => (
                <li key={i}><a href={r} className="text-blue-600 underline" target="_blank">{r}</a></li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}