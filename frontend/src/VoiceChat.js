import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './VoiceChat.css';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import SendIcon from '@mui/icons-material/Send';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import SchoolIcon from '@mui/icons-material/School';

const API_URL = 'http://localhost:5000';

function VoiceChat({ fen, move, bestMove, evaluation, cpLoss, quality, phase }) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [aiStatus, setAiStatus] = useState({ ollama: false, models: [] });
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const currentAudio = useRef(null);

  useEffect(() => {
    checkAIStatus();
  }, []);

  const checkAIStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/check-ai-status`);
      console.log('AI Status:', response.data);
      setAiStatus(response.data);
    } catch (error) {
      console.error('Failed to check AI status:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        await processVoiceInput(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      alert('Microphone access denied. Please allow microphone access to use voice features.');
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob) => {
    setIsProcessing(true);
    try {
      // Convert speech to text
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const transcriptResponse = await axios.post(`${API_URL}/api/voice-to-text`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const userText = transcriptResponse.data.text;
      setTranscript(userText);

      // Get AI response
      await getAIResponse(userText);
    } catch (error) {
      console.error('Error processing voice:', error);
      const errorMsg = error.response?.data?.error || 'Voice recognition failed. Please type your question instead.';
      setAiResponse(`⚠️ ${errorMsg}`);
      setTranscript('(Voice input failed)');
    } finally {
      setIsProcessing(false);
    }
  };

  const getAIResponse = async (question) => {
    try {
      const response = await axios.post(`${API_URL}/api/chat-analysis`, {
        fen,
        move,
        bestMove,
        evaluation,
        cpLoss,
        quality,
        phase,
        question
      });

      const aiText = response.data.response;
      setAiResponse(aiText);

      // Speak the response
      await speakText(aiText);
    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMsg = error.response?.data?.error || 'AI Coach is not available. Please make sure Ollama is installed and running.';
      setAiResponse(errorMsg);
    }
  };

  const speakText = async (text) => {
    try {
      setIsSpeaking(true);
      
      // Stop any currently playing audio
      if (currentAudio.current) {
        currentAudio.current.pause();
        currentAudio.current = null;
      }

      const response = await axios.post(`${API_URL}/api/text-to-speech`, 
        { text }, 
        { responseType: 'blob' }
      );

      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      currentAudio.current = audio;

      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
    } catch (error) {
      console.error('Error speaking text:', error);
      setIsSpeaking(false);
    }
  };

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;

    setTranscript(textInput);
    setIsProcessing(true);
    await getAIResponse(textInput);
    setIsProcessing(false);
    setTextInput('');
  };

  const stopSpeaking = () => {
    if (currentAudio.current) {
      currentAudio.current.pause();
      currentAudio.current = null;
      setIsSpeaking(false);
    }
  };

  return (
    <div className="voice-chat-container">
      <div className="voice-chat-header">
        <h3>
          <SchoolIcon style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          AI Chess Coach
        </h3>
        {!aiStatus.ollama && (
          <div className="ai-warning">
            ⚠️ Ollama not detected. <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer">Install Ollama</a> to use AI features.
          </div>
        )}
        {aiStatus.ollama && !aiStatus.whisper && (
          <div className="ai-warning">
            ℹ️ Voice input unavailable. Install Whisper for voice features: <code>pip install openai-whisper</code>
          </div>
        )}
      </div>

      <div className="voice-chat-content">
        {/* Voice Input */}
        <div className="voice-input-section">
          <button 
            className={`voice-button ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing || !aiStatus.ollama || !aiStatus.whisper}
            title={
              !aiStatus.ollama ? 'Ollama not installed' :
              !aiStatus.whisper ? 'Whisper not installed' :
              isRecording ? 'Click to stop recording' : 'Click to start recording'
            }
          >
            {isRecording ? (
              <>
                <StopIcon style={{ marginRight: '8px' }} />
                Recording...
              </>
            ) : (
              <>
                <MicIcon style={{ marginRight: '8px' }} />
                Ask Coach
              </>
            )}
          </button>
          
          {isSpeaking && (
            <button 
              className="stop-speaking-button"
              onClick={stopSpeaking}
            >
              <VolumeOffIcon style={{ marginRight: '8px' }} />
              Stop Speaking
            </button>
          )}
        </div>

        {/* Text Input Alternative */}
        <form onSubmit={handleTextSubmit} className="text-input-section">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Or type your question here..."
            className="text-input"
            disabled={isProcessing || !aiStatus.ollama}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={isProcessing || !textInput.trim() || !aiStatus.ollama}
          >
            <SendIcon style={{ marginRight: '8px' }} />
            Send
          </button>
        </form>

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="processing-indicator">
            <div className="spinner"></div>
            <span>Thinking...</span>
          </div>
        )}

        {/* Conversation Display */}
        {transcript && (
          <div className="conversation">
            <div className="message user-message">
              <strong>You:</strong> {transcript}
            </div>
            {aiResponse && (
              <div className="message ai-message">
                <strong>Coach:</strong> {aiResponse}
              </div>
            )}
          </div>
        )}

        {/* Quick Questions */}
        {!transcript && aiStatus.ollama && (
          <div className="quick-questions">
            <p className="quick-questions-label">Quick questions:</p>
            <button onClick={() => { setTextInput('Why is this move good or bad?'); }}>
              Why is this move good/bad?
            </button>
            <button onClick={() => { setTextInput('What should I look for in this position?'); }}>
              What should I look for?
            </button>
            <button onClick={() => { setTextInput('What are better alternatives?'); }}>
              Better alternatives?
            </button>
            <button onClick={() => { setTextInput('Explain the key ideas in this position.'); }}>
              Key ideas?
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default VoiceChat;
