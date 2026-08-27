/**
 * ORCA Marine Intelligence Platform - Text-to-Speech (TTS) Engine
 * Modular Web Speech API wrapper with multilingual voice selection and playback controls.
 */
class OrcaTTSEngine {
  constructor() {
    this.synth = typeof window !== 'undefined' && 'speechSynthesis' in window ? window.speechSynthesis : null;
    this.activeUtterance = null;
    this.activeMsgId = null;
    this.activeCallback = null;
    this.playbackState = 'stopped'; // 'stopped' | 'playing' | 'paused'
    this.cachedVoices = [];

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

    this._initVoices();
    this._bindUnloadHandler();
  }

  isSupported() {
    return !!this.synth;
  }

  isEnabled() {
    return localStorage.getItem('orca_tts_enabled') !== 'false';
  }

  getRate() {
    const rate = parseFloat(localStorage.getItem('orca_tts_rate') || '1.0');
    return isNaN(rate) ? 1.0 : rate;
  }

  getSavedVoiceURI() {
    return localStorage.getItem('orca_tts_voice') || '';
  }

  setPreference(key, value) {
    localStorage.setItem(key, value);
  }

  _initVoices() {
    if (!this.synth) return;
    const loadVoices = () => {
      this.cachedVoices = this.synth.getVoices();
    };
    loadVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = loadVoices;
    }
  }

  getVoices() {
    if (!this.synth) return [];
    if (!this.cachedVoices || this.cachedVoices.length === 0) {
      this.cachedVoices = this.synth.getVoices();
    }
    return this.cachedVoices;
  }

  getLanguageTag(langCode) {
    return this.langMap[langCode] || 'en-US';
  }

  findBestVoice(langCode) {
    const voices = this.getVoices();
    if (!voices || voices.length === 0) return null;

    const savedURI = this.getSavedVoiceURI();
    if (savedURI) {
      const matchSaved = voices.find(v => v.voiceURI === savedURI);
      if (matchSaved) return matchSaved;
    }

    const targetTag = this.getLanguageTag(langCode || 'en').toLowerCase();
    const primaryLang = targetTag.split('-')[0];

    // 1. Exact match (e.g. hi-IN)
    let match = voices.find(v => (v.lang || '').toLowerCase().replace('_', '-') === targetTag);
    if (match) return match;

    // 2. Primary language match (e.g. hi)
    match = voices.find(v => (v.lang || '').toLowerCase().startsWith(primaryLang));
    if (match) return match;

    // 3. English-India or English fallback
    match = voices.find(v => (v.lang || '').toLowerCase().startsWith('en-in'));
    if (match) return match;

    match = voices.find(v => (v.lang || '').toLowerCase().startsWith('en'));
    if (match) return match;

    // 4. Default system voice
    return voices[0] || null;
  }

  cleanTextForSpeech(rawText) {
    if (!rawText) return '';
    return rawText
      .replace(/<[^>]*>/g, '') // Strip HTML tags
      .replace(/[\*\#\`\_]/g, '') // Strip markdown formatting
      .replace(/https?:\/\/\S+/g, 'link') // Replace URLs
      .replace(/[\n\r]+/g, '. ') // Replace newlines with pauses
      .trim();
  }

  speak(text, msgId, langCode, stateCallback) {
    if (!this.isSupported()) {
      console.warn('Speech synthesis is not supported on this browser.');
      return;
    }

    if (!this.isEnabled()) {
      console.info('TTS is disabled in settings.');
      return;
    }

    // Toggle pause/resume if clicking the same message while active
    if (this.activeMsgId === msgId) {
      if (this.playbackState === 'playing') {
        this.pause();
        return;
      } else if (this.playbackState === 'paused') {
        this.resume();
        return;
      }
    }

    // Stop any existing speech
    this.stop();

    const cleanText = this.cleanTextForSpeech(text);
    if (!cleanText) return;

    this.activeMsgId = msgId;
    this.activeCallback = stateCallback;
    this.activeUtterance = new SpeechSynthesisUtterance(cleanText);

    const voice = this.findBestVoice(langCode);
    if (voice) {
      this.activeUtterance.voice = voice;
      this.activeUtterance.lang = voice.lang;
    } else {
      this.activeUtterance.lang = this.getLanguageTag(langCode);
    }

    this.activeUtterance.rate = this.getRate();
    this.activeUtterance.pitch = 1.0;
    this.activeUtterance.volume = 1.0;

    this.activeUtterance.onstart = () => {
      this.playbackState = 'playing';
      if (this.activeCallback) this.activeCallback('playing', this.activeMsgId);
    };

    this.activeUtterance.onpause = () => {
      this.playbackState = 'paused';
      if (this.activeCallback) this.activeCallback('paused', this.activeMsgId);
    };

    this.activeUtterance.onresume = () => {
      this.playbackState = 'playing';
      if (this.activeCallback) this.activeCallback('playing', this.activeMsgId);
    };

    this.activeUtterance.onend = () => {
      const endedMsgId = this.activeMsgId;
      this._resetState();
      if (stateCallback) stateCallback('stopped', endedMsgId);
    };

    this.activeUtterance.onerror = (e) => {
      console.error('TTS Utterance Error:', e);
      const errMsgId = this.activeMsgId;
      this._resetState();
      if (stateCallback) stateCallback('stopped', errMsgId);
    };

    this.synth.speak(this.activeUtterance);
  }

  pause() {
    if (this.synth && this.playbackState === 'playing') {
      this.synth.pause();
    }
  }

  resume() {
    if (this.synth && this.playbackState === 'paused') {
      this.synth.resume();
    }
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
    }
    const previousMsgId = this.activeMsgId;
    const previousCallback = this.activeCallback;
    this._resetState();
    if (previousCallback && previousMsgId) {
      previousCallback('stopped', previousMsgId);
    }
  }

  _resetState() {
    this.activeUtterance = null;
    this.activeMsgId = null;
    this.activeCallback = null;
    this.playbackState = 'stopped';
  }

  _bindUnloadHandler() {
    if (typeof window === 'undefined') return;
    const stopAudio = () => this.stop();
    window.addEventListener('beforeunload', stopAudio);
    window.addEventListener('pagehide', stopAudio);
  }
}

// Global Singleton Initialization
if (typeof window !== 'undefined') {
  window.OrcaTTS = new OrcaTTSEngine();
}
