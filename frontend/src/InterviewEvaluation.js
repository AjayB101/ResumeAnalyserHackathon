import React, { useState } from 'react';
import { Upload, FileText, MessageSquare, Target, TrendingUp, CheckCircle, AlertCircle, Clock, Star, ExternalLink } from 'lucide-react';

const InterviewEvaluationApp = () => {
  const [formData, setFormData] = useState({
    resume: null,
    jobDescription: '',
    candidateResponse: ''
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      resume: e.target.files[0]
    });
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResults(null);

    if (!formData.resume || !formData.jobDescription.trim() || !formData.candidateResponse.trim()) {
      setError('Please fill in all fields and upload a resume');
      setLoading(false);
      return;
    }

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('resume', formData.resume);
      formDataToSend.append('job_description', formData.jobDescription);
      formDataToSend.append('candidate_response', formData.candidateResponse);

      const response = await fetch('http://localhost:8000/run-interview-evaluation/', {
        method: 'POST',
        body: formDataToSend,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(`Failed to evaluate interview: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const ScoreCard = ({ title, score, icon: Icon, feedback = [] }) => (
    <div className="bg-white p-6 rounded-lg shadow-md border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Icon className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-bold ${getScoreColor(score)}`}>
          {score}/100
        </div>
      </div>
      {feedback.length > 0 && (
        <div className="space-y-2">
          {feedback.map((item, index) => (
            <div key={index} className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
              <p className="text-sm text-gray-600">{item}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Interview Evaluation System</h1>
          <p className="text-xl text-gray-600">Upload your resume and get comprehensive interview feedback</p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="space-y-6">
            <div>
              <label className="flex items-center space-x-2 text-lg font-medium text-gray-700 mb-3">
                <Upload className="w-5 h-5" />
                <span>Upload Resume</span>
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx,.txt"
                required
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="flex items-center space-x-2 text-lg font-medium text-gray-700 mb-3">
                <FileText className="w-5 h-5" />
                <span>Job Description</span>
              </label>
              <textarea
                name="jobDescription"
                value={formData.jobDescription}
                onChange={handleInputChange}
                required
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Paste the job description here..."
              />
            </div>

            <div>
              <label className="flex items-center space-x-2 text-lg font-medium text-gray-700 mb-3">
                <MessageSquare className="w-5 h-5" />
                <span>Mock Interview Response</span>
              </label>
              <textarea
                name="candidateResponse"
                value={formData.candidateResponse}
                onChange={handleInputChange}
                required
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your response to a behavioral interview question..."
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <Target className="w-5 h-5" />
                  <span>Run Evaluation</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center space-x-2">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-8">
            {/* Overall Score */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-lg shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Overall Success Score</h2>
                  <p className="text-blue-100">{results.outcome?.reason}</p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold">{results.outcome?.success_score}/100</div>
                  <div className="flex items-center space-x-1 mt-2">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${
                          i < Math.round((results.outcome?.success_score || 0) / 20)
                            ? 'text-yellow-300 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Resume Scores */}
            {results.resume_scores && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <span>Resume Analysis</span>
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <ScoreCard
                    title="Clarity"
                    score={results.resume_scores.clarity}
                    icon={CheckCircle}
                  />
                  <ScoreCard
                    title="Relevance"
                    score={results.resume_scores.relevance}
                    icon={Target}
                  />
                  <ScoreCard
                    title="Structure"
                    score={results.resume_scores.structure}
                    icon={FileText}
                  />
                  <ScoreCard
                    title="Experience"
                    score={results.resume_scores.experience * 20}
                    icon={TrendingUp}
                  />
                </div>
                {results.resume_scores.feedback && (
                  <div className="mt-6 bg-blue-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-blue-900 mb-3">Resume Feedback</h3>
                    <ul className="space-y-2">
                      {results.resume_scores.feedback.map((feedback, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-blue-800">{feedback}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Mock Interview Scores */}
            {results.mock_scores && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-3">
                  <MessageSquare className="w-8 h-8 text-blue-600" />
                  <span>Mock Interview Analysis</span>
                </h2>
                <div className="bg-white p-6 rounded-lg shadow-md border mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Question Asked:</h3>
                  <p className="text-gray-600 italic mb-4">"{results.mock_scores.question}"</p>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Your Response:</h3>
                  <p className="text-gray-600 bg-gray-50 p-4 rounded-lg">"{results.mock_scores.response}"</p>
                </div>
                
                <div className="grid md:grid-cols-3 gap-6 mb-6">
                  <ScoreCard
                    title="Tone"
                    score={results.mock_scores.tone}
                    icon={MessageSquare}
                  />
                  <ScoreCard
                    title="Confidence"
                    score={results.mock_scores.confidence}
                    icon={TrendingUp}
                  />
                  <ScoreCard
                    title="Relevance"
                    score={results.mock_scores.relevance}
                    icon={Target}
                  />
                </div>

                {results.mock_scores.feedback && (
                  <div className="bg-yellow-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-yellow-900 mb-3">Interview Feedback</h3>
                    <ul className="space-y-2">
                      {results.mock_scores.feedback.map((feedback, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-yellow-800">{feedback}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Behavioral Questions */}
            {results.behavioral_patterns?.questions && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-3">
                  <Clock className="w-8 h-8 text-blue-600" />
                  <span>Practice Questions for You</span>
                </h2>
                <div className="grid gap-6">
                  {results.behavioral_patterns.questions.slice(0, 3).map((item, index) => (
                    <div key={index} className="bg-white p-6 rounded-lg shadow-md border">
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">
                        Question {index + 1}:
                      </h3>
                      <p className="text-gray-700 mb-4 font-medium">{item.question}</p>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="text-sm font-semibold text-green-800 mb-2">Sample Answer:</h4>
                        <p className="text-green-700 text-sm">{item.sample_answer}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Improvement Plan */}
           {/* Improvement Plan */}
            {results.improvement_plan && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-3">
                  <TrendingUp className="w-8 h-8 text-blue-600" />
                  <span>Improvement Plan</span>
                </h2>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Suggestions</h3>
                    {/* Corrected path: results.improvement_plan.improvement_plan.suggestions */}
                    <ul className="space-y-3">
                      {results.improvement_plan.improvement_plan?.suggestions?.map((suggestion, index) => (
                        <li key={index} className="flex flex-col space-y-1">
                          <div className="flex items-start space-x-2">
                            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-900 font-medium">{suggestion.title}</span>
                          </div>
                          <p className="pl-7 text-gray-600 text-sm">{suggestion.description}</p>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Recommended Resources</h3>
                    {/* Corrected path: results.improvement_plan.improvement_plan.resources */}
                    <ul className="space-y-3">
                      {results.improvement_plan.improvement_plan?.resources?.map((resource, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <ExternalLink className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
                          <div className="flex flex-col">
                            <a
                              href={resource.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 font-medium"
                            >
                              {resource.title}
                            </a>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewEvaluationApp;