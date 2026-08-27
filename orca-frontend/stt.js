/**
 * ORCA Marine Intelligence Platform - Speech-to-Text (STT) Engine
 * Modular Web Speech API wrapper for real-time speech recognition.
 */
class OrcaSTTEngine {
  constructor() {
    const SpeechRecognition = typeof window !== 'undefined' && (window.SpeechRecognition || window.webkitSpeechRecognition);
    this.SpeechRecognitionClass = SpeechRecognition || null;
    this.recognition = null;
    this.isListening = false;
    this.state = 'idle'; // 'idle' | 'listening' | 'processing'
    this.initialInputValue = '';
    this.finalTranscript = '';
    this.onStateChange = null;
    this.onTranscriptUpdate = null;
    this.targetInputEl = null;

    this.langMap = {
      'en': 'en-IN',
      'hi': 'hi-IN',
      'kn': 'kn-IN',
      'ta': 'ta-IN',
      'te': 'te-IN',
      'mr': 'mr-IN',
      'bn': 'bn-IN',
      'gu': 'gu-IN',
      'ml': 'ml-IN',
      'pa': 'pa-IN',
      'or': 'or-IN',
      'ur': 'ur-IN',
      'as': 'as-IN',
      'brx': 'hi-IN',
      'doi': 'hi-IN',
      'ks': 'hi-IN',
      'kok': 'hi-IN',
      'mai': 'hi-IN',
      'mni': 'hi-IN',
      'ne': 'ne-NP',
      'sa': 'hi-IN',
      'sat': 'hi-IN',
      'sd': 'hi-IN'
    };

    this._bindUnloadHandler();
  }

  isSupported() {
    return !!this.SpeechRecognitionClass;
  }

  getLanguageLocale(langCode) {
    return this.langMap[langCode] || 'en-IN';
  }

  start(langCode, inputEl, stateCallback, transcriptCallback) {
    if (!this.isSupported()) {
      const msg = (window.Orcai18n && window.Orcai18n.getTranslation)
        ? window.Orcai18n.getTranslation('stt_not_supported', 'Voice input is not supported in this browser.')
        : 'Voice input is not supported in this browser.';
      alert(msg);
      return;
    }

    if (this.isListening) {
      this.stop();
      return;
    }

    this.targetInputEl = inputEl;
    this.onStateChange = stateCallback;
    this.onTranscriptUpdate = transcriptCallback;

    this.initialInputValue = inputEl ? inputEl.value : '';
    this.finalTranscript = '';

    try {
      this.recognition = new this.SpeechRecognitionClass();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.maxAlternatives = 1;
      this.recognition.lang = this.getLanguageLocale(langCode || 'en');

      this.recognition.onstart = () => {
        this.isListening = true;
        this._setState('listening');
      };

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            this.finalTranscript += (this.finalTranscript ? ' ' : '') + transcript.trim();
          } else {
            interimTranscript += transcript;
          }
        }

        const combinedText = [
          this.initialInputValue,
          this.finalTranscript,
          interimTranscript
        ].filter(Boolean).join(' ');

        if (this.targetInputEl) {
          this.targetInputEl.value = combinedText;
        }

        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(combinedText);
        }
      };

      this.recognition.onerror = (event) => {
        console.warn('STT Recognition Error:', event.error);
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          const errAlert = (window.Orcai18n && window.Orcai18n.getTranslation)
            ? window.Orcai18n.getTranslation('stt_permission_denied', 'Microphone access was denied. Please allow microphone permissions in browser settings.')
            : 'Microphone access was denied. Please allow microphone permissions in browser settings.';
          alert(errAlert);
        }
        this._setState('idle');
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this._setState('idle');
      };

      this.recognition.start();

    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      this.isListening = false;
      this._setState('idle');
    }
  }

  stop() {
    if (this.recognition && this.isListening) {
      this._setState('processing');
      try {
        this.recognition.stop();
      } catch (err) {
        console.warn('Error stopping recognition:', err);
      }
    }
    this.isListening = false;
    this._setState('idle');
  }

  toggle(langCode, inputEl, stateCallback, transcriptCallback) {
    if (this.isListening) {
      this.stop();
    } else {
      this.start(langCode, inputEl, stateCallback, transcriptCallback);
    }
  }

  _setState(newState) {
    this.state = newState;
    if (this.onStateChange) {
      this.onStateChange(this.state);
    }
  }

  _bindUnloadHandler() {
    if (typeof window === 'undefined') return;
    const cleanup = () => this.stop();
    window.addEventListener('beforeunload', cleanup);
    window.addEventListener('pagehide', cleanup);
  }
}

// Global Singleton Initialization
if (typeof window !== 'undefined') {
  window.OrcaSTT = new OrcaSTTEngine();
}
