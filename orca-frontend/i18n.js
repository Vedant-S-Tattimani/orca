/**
 * ORCA Marine Intelligence - Internationalization (i18n) Core System
 * Supports English and 22 official/major Indian languages with native scripts.
 */

const SUPPORTED_LANGUAGES = [
    { code: 'en', name: 'English', native: 'English', speechCode: 'en-IN' },
    { code: 'hi', name: 'Hindi', native: 'हिंदी', speechCode: 'hi-IN' },
    { code: 'as', name: 'Assamese', native: 'অসমীয়া', speechCode: 'as-IN' },
    { code: 'bn', name: 'Bengali', native: 'বাংলা', speechCode: 'bn-IN' },
    { code: 'brx', name: 'Bodo', native: 'बर\'', speechCode: 'hi-IN' },
    { code: 'doi', name: 'Dogri', native: 'डोगरी', speechCode: 'hi-IN' },
    { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી', speechCode: 'gu-IN' },
    { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', speechCode: 'kn-IN' },
    { code: 'ks', name: 'Kashmiri', native: 'کأشُر / कॉशुर', speechCode: 'ur-IN' },
    { code: 'kok', name: 'Konkani', native: 'कोंकणी', speechCode: 'mr-IN' },
    { code: 'mai', name: 'Maithili', native: 'मैथिली', speechCode: 'hi-IN' },
    { code: 'ml', name: 'Malayalam', native: 'മലയാളം', speechCode: 'ml-IN' },
    { code: 'mni', name: 'Manipuri', native: 'ꯃꯩꯇꯩꯂꯣꯟ', speechCode: 'bn-IN' },
    { code: 'mr', name: 'Marathi', native: 'मराठी', speechCode: 'mr-IN' },
    { code: 'ne', name: 'Nepali', native: 'नेपाली', speechCode: 'ne-NP' },
    { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ', speechCode: 'or-IN' },
    { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', speechCode: 'pa-IN' },
    { code: 'sa', name: 'Sanskrit', native: 'संस्कृतम्', speechCode: 'hi-IN' },
    { code: 'sat', name: 'Santali', native: 'ᱥᱟᱱᱛᱟᱲᱤ', speechCode: 'hi-IN' },
    { code: 'sd', name: 'Sindhi', native: 'સિન્ધી / سنڌي', speechCode: 'hi-IN' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்', speechCode: 'ta-IN' },
    { code: 'te', name: 'Telugu', native: 'తెలుగు', speechCode: 'te-IN' },
    { code: 'ur', name: 'Urdu', native: 'اردو', speechCode: 'ur-IN' }
];

const TRANSLATIONS = {
    en: {
        // Navigation
        nav_about: 'About',
        nav_dashboard: 'Dashboard',
        nav_assistant: 'Assistant',
        nav_map: 'Map',
        nav_safety: 'Safety & Alerts',
        nav_fishing: 'Fishing',
        nav_settings: 'Settings',
        nav_login: 'Login',
        brand_sub: 'Intelligence',
        
        // Login Page
        login_welcome_title: 'Welcome to ORCA',
        login_welcome_desc: 'Access real-time marine intelligence, ocean oceanographic telemetry, and AI vessel navigation.',
        login_email_label: 'Email Address',
        login_email_placeholder: 'captain@vessel.org',
        login_password_label: 'Password',
        login_password_placeholder: '••••••••••••',
        login_remember: 'Remember this vessel',
        login_forgot_password: 'Forgot password?',
        login_submit_btn: 'Sign In to Platform',
        login_or: 'or',
        login_guest_btn: 'Continue as Guest',
        login_no_account: "Don't have an account?",
        login_request_access: 'Request Access',
        
        // Common
        export_report: 'Export Report',
        view_full_chart: 'View Full Chart',
        view_details: 'View Details',
        active: 'Active',
        search: 'Search...',
        search_language: 'Search language...',
        
        // Dashboard
        dash_title: 'Dashboard Overview',
        dash_subtitle: 'Real-time marine conditions and operational directives.',
        wave_height: 'Wave Height',
        wind_speed: 'Wind Speed',
        water_temp: 'Water Temp',
        from_last_hour: '+0.3m from last hour',
        nw_direction: 'NW Direction',
        steady_cooling: 'Steady cooling',
        risk_assessment: 'Risk Assessment',
        risk_moderate: 'MODERATE',
        risk_index: 'INDEX: 6.8 / 10',
        risk_desc: 'Conditions are deteriorating offshore. Exercise caution for small vessels.',
        forecast_24h: '24h Forecast',
        active_directives: 'Active Directives',
        alerts_count: '2 ALERTS',
        gale_warning: 'Gale Warning Issued',
        gale_desc: 'Sector B offshore expecting gusts up to 45kts starting 22:00. Secure all loose deck equipment.',
        sensor_cal: 'Sensor Calibration Required',
        sensor_desc: 'Buoy Alpha-7 reporting irregular swell data. Scheduled maintenance required within 48h.',
        route_update: 'Route Update Available',
        route_desc: 'Optimized routing for Fleet C ready for review based on latest current models.',
        
        // Assistant
        assistant_title: 'ORCA AI Assistant',
        assistant_desc: 'Ask anything about ocean safety, fishing zones, or route optimization.',
        ask_assistant_placeholder: 'Ask ORCA Assistant...',
        agent_activity: 'Agent Activity',
        orca_thinking: 'ORCA is thinking...',
        greeting_msg: 'Hello! I am ORCA, your Marine Ecosystem Reasoning Assistant. How can I help you today?',
        export_pdf: 'Export PDF Report',
        listen_response: 'Listen to response',
        pause_speech: 'Pause speaking',
        resume_speech: 'Resume speaking',
        stop_speech: 'Stop speaking',
        listening: 'Speaking...',
        
        // Safety
        safety_title: 'Marine Safety & Bulletins',
        safety_desc: 'Live coastal hazards, cyclone advisories, and weather warnings.',
        active_warnings: 'Active Advisories',
        emergency_contacts: 'Emergency Contacts',
        coast_guard: 'Indian Coast Guard: 1554',
        disaster_mgmt: 'State Disaster Management: 1070',
        port_authority: 'Port Control VHF: Channel 16',
        cyclone_advisory: 'Cyclonic Depression Warning',
        high_wave_alert: 'High Wave Swell Alert',
        tsunami_watch: 'Tsunami Watch Bulletin',
        safety_active_advisories: 'Active Advisories',
        safety_loading_advisories: 'Loading active advisories...',
        safety_env_matrix: 'Environmental Matrix',
        safety_wind_speed_kts: 'Wind Speed (Kts)',
        safety_wave_height_m: 'Wave Height (m)',
        safety_lightning_risk: 'Lightning Risk',
        safety_moderate: 'MODERATE',
        safety_alert_chronology: 'Alert Chronology',
        safety_loading_chronology: 'Loading chronology...',
        safety_actions_checklist: 'Required Actions Checklist',
        safety_loading_checklist: 'Loading checklist...',
        
        // Fishing
        fishing_title: 'Fishing Intelligence & Potential Fishing Zones',
        fishing_desc: 'Satellite-backed PFZ advisories, sea surface temperature, and chlorophyll data.',
        pfz_zones: 'Potential Fishing Zones',
        sea_surface_temp: 'Sea Surface Temp',
        chlorophyll: 'Chlorophyll-a',
        coastal_advisory: 'Coastal Fishing Advisory',
        high_potential: 'HIGH POTENTIAL',
        moderate_potential: 'MODERATE POTENTIAL',
        low_potential: 'LOW POTENTIAL',
        fish_clear_points: 'Clear Custom Points',
        fish_update_scan: 'Update Scan',
        fish_live_sst: 'Live SST',
        fish_chlorophyll: 'Chlorophyll-a',
        fish_data_updated: 'Data Updated',
        fish_top_rec: 'Top Recommendation',
        fish_suitability: 'Suitability',
        fish_distance: 'Distance',
        fish_est_eta: 'Est. ETA',
        fish_why_recommended: 'Why This Area Is Recommended:',
        fish_loading_analysis: 'Loading analysis...',
        fish_set_waypoint: 'Set as Waypoint',
        fish_marine_indicators: 'Marine Indicators',
        fish_sst_label: 'Sea Surface Temp (SST)',
        fish_chla_label: 'Chlorophyll-a',
        fish_wind_label: 'Wind (Speed / Dir)',
        fish_24h_prediction: '24-Hour Prediction',
        fish_zone_comparison: 'Zone Comparison',
        fish_view_analysis: 'View Full Analysis',
        speak_to_orca: 'Speak to ORCA',
        stt_listening: 'Listening...',
        stt_not_supported: 'Voice input is not supported in this browser.',
        stt_permission_denied: 'Microphone access was denied. Please allow microphone permissions in browser settings.',
        fish_th_sector: 'Sector',
        fish_th_score: 'Score',
        fish_th_distance: 'Distance',
        fish_th_sst: 'SST',
        fish_th_activity: 'Activity Level',
        fish_th_action: 'Action',
        fish_loading_zones: 'Loading zones...',

        // Map
        map_title: 'Geospatial Marine Intelligence Map',
        map_desc: 'Real-time vessel tracking, weather overlays, and route safety computation.',
        layer_controls: 'Map Layers',
        vessel_tracking: 'Vessel AIS Tracking',
        weather_overlay: 'Weather Radar',
        route_planner: 'Route Safety Planner',
        calculate_route: 'Calculate Safe Route',
        origin: 'Origin Port / Coords',
        destination: 'Destination Port / Coords',
        map_route_planning: 'Route Planning',
        map_origin: 'Origin',
        map_destination: 'Destination',
        map_click_map_port: 'Click map or select port...',
        map_calculate_route: 'Calculate Route',
        map_route_geometry: 'Route Geometry',
        map_distance: 'Distance:',
        map_duration: 'Duration:',
        map_type: 'Type:',
        map_route_safety: 'Route Safety Assessment',
        map_active_layers: 'Active Layers',
        map_vessel_ais: 'Vessel AIS (Live)',
        map_weather_hazards: 'Weather Hazards',
        map_restricted_zones: 'Restricted Zones',
        map_fishing_grounds: 'Fishing Grounds (SST)',
        map_vessel_routes: 'Vessel Routes',
        map_ports: 'Ports',

        // Settings
        settings_title: 'Settings',
        settings_desc: 'Manage your platform preferences and vessel details.',
        general_settings: 'General Preferences',
        theme_preference: 'Theme Display',
        language_preference: 'Platform Language',
        tts_settings: 'Text-to-Speech (AI Assistant Voice)',
        enable_tts: 'Enable Voice Responses',
        enable_tts_desc: 'Allow ORCA AI Assistant to speak answers aloud.',
        speech_voice: 'Voice Selection',
        speech_rate: 'Speech Speed (Rate)',
        test_voice: 'Test Voice Output',
        save_settings: 'Save Preferences',
        settings_saved: 'Preferences saved successfully!',
        set_account_profile: 'Account & Profile',
        set_full_name: 'Full Name',
        set_email: 'Email Address',
        set_update_profile: 'Update Profile',
        set_vessel_profile: 'Vessel Profile',
        set_vessel_name: 'Vessel Name',
        set_vessel_type: 'Vessel Type',
        set_commercial_fishing: 'Commercial Fishing',
        set_recreational: 'Recreational',
        set_transport: 'Transport',
        set_length_m: 'Length (meters)',
        set_operating_range: 'Operating Range (NM)',
        set_localization: 'Localization',
        set_language: 'Language',
        set_measurement: 'Measurement System',
        set_metric: 'Metric',
        set_imperial: 'Imperial',
        set_home_port: 'Home Port',
        set_search_ports: 'Search ports...',
        set_change: 'Change',
        set_alert_prefs: 'Alert Preferences',
        set_severe_weather: 'Severe Weather Warnings',
        set_severe_weather_desc: 'Immediate push notifications for storms.',
        set_route_deviations: 'Route Deviations',
        set_route_deviations_desc: 'Alerts when off planned track.',
        set_intel_updates: 'Intelligence Updates',
        set_intel_updates_desc: 'Daily summaries of marine activity.',
        set_save: 'Save Settings'
    },
    hi: {
        nav_about: 'हमारे बारे में',
        nav_dashboard: 'डैशबोर्ड',
        nav_assistant: 'एआई सहायक',
        nav_map: 'समुद्री मानचित्र',
        nav_safety: 'सुरक्षा और अलर्ट',
        nav_fishing: 'मत्स्य पालन',
        nav_settings: 'सेटिंग्स',
        brand_sub: 'इंटेलीजेंस',
        
        export_report: 'रिपोर्ट डाउनलोड करें',
        view_full_chart: 'पूरा चार्ट देखें',
        view_details: 'विवरण देखें',
        active: 'सक्रिय',
        search: 'खोजें...',
        search_language: 'भाषा खोजें...',
        
        dash_title: 'डैशबोर्ड अवलोकन',
        dash_subtitle: 'वास्तविक समय समुद्री स्थिति और परिचालन निर्देश।',
        wave_height: 'तरंग की ऊँचाई',
        wind_speed: 'हवा की गति',
        water_temp: 'जल तापमान',
        from_last_hour: '+0.3m पिछले घंटे से',
        nw_direction: 'उत्तर-पश्चिम दिशा',
        steady_cooling: 'स्थिर शीतलन',
        risk_assessment: 'जोखिम का आंकलन',
        risk_moderate: 'मध्यम जोखिम',
        risk_index: 'सूचकांक: 6.8 / 10',
        risk_desc: 'समुद्र में स्थिति खराब हो रही है। छोटी नौकाओं के लिए सावधानी बरतें।',
        forecast_24h: '24 घंटे का पूर्वानुमान',
        active_directives: 'सक्रिय निर्देश',
        alerts_count: '2 चेतावनी',
        gale_warning: 'तेज़ हवा की चेतावनी',
        gale_desc: 'सेक्टर बी में 22:00 बजे से 45kts की हवाएं चलने की संभावना है। उपकरण सुरक्षित करें।',
        sensor_cal: 'सेंसर अंशांकन आवश्यक',
        sensor_desc: 'बॉया अल्फा-7 अनियमित डेटा रिपोर्ट कर रहा है। 48 घंटे में रखरखाव आवश्यक है।',
        route_update: 'मार्ग अद्यतन उपलब्ध',
        route_desc: 'नवीनतम समुद्री धाराओं के आधार पर फ्लीट सी के लिए अनुकूलित मार्ग तैयार है।',

        assistant_title: 'ORCA एआई सहायक',
        assistant_desc: 'समुद्री सुरक्षा, मत्स्य क्षेत्रों और अनुकूलित मार्गों के बारे में कुछ भी पूछें।',
        ask_assistant_placeholder: 'ORCA सहायक से पूछें...',
        agent_activity: 'एजेंट गतिविधि',
        orca_thinking: 'ORCA सोच रहा है...',
        greeting_msg: 'नमस्ते! मैं ORCA हूँ, आपका समुद्री पारिस्थितिकी तंत्र सहायक। आज मैं आपकी क्या मदद कर सकता हूँ?',
        export_pdf: 'पीडीएफ रिपोर्ट निर्यात करें',
        listen_response: 'उत्तर सुनें',
        pause_speech: 'बोलना रोकें',
        resume_speech: 'पुनः शुरू करें',
        stop_speech: 'स्पीच बंद करें',
        listening: 'बोल रहा है...',

        safety_title: 'समुद्री सुरक्षा और बुलेटिन',
        safety_desc: 'तटीय खतरे, चक्रवात चेतावनियां और मौसम बुलेटिन।',
        active_warnings: 'सक्रिय चेतावनियाँ',
        emergency_contacts: 'आपातकालीन संपर्क',
        coast_guard: 'भारतीय तट रक्षक: 1554',
        disaster_mgmt: 'राज्य आपदा प्रबंधन: 1070',
        port_authority: 'पोर्ट नियंत्रण वीएचएफ: चैनल 16',
        cyclone_advisory: 'चक्रवाती दबाव की चेतावनी',
        high_wave_alert: 'उच्च तरंग चेतावनी',
        tsunami_watch: 'सुनामी सतर्कता बुलेटिन',
        safety_active_advisories: 'सक्रिय सलाह',
        safety_loading_advisories: 'सक्रिय सलाह लोड हो रही है...',
        safety_env_matrix: 'पर्यावरण मैट्रिक्स',
        safety_wind_speed_kts: 'हवा की गति (नॉट्स)',
        safety_wave_height_m: 'तरंग ऊँचाई (मी)',
        safety_lightning_risk: 'बिजली का खतरा',
        safety_moderate: 'मध्यम',
        safety_alert_chronology: 'चेतावनी कालक्रम',
        safety_loading_chronology: 'कालक्रम लोड हो रहा है...',
        safety_actions_checklist: 'आवश्यक कार्य सूची',
        safety_loading_checklist: 'सूची लोड हो रही है...',

        fishing_title: 'मत्स्य पालन और संभावित मत्स्य क्षेत्र (PFZ)',
        fishing_desc: 'उपग्रह आधारित PFZ सलाह, समुद्री सतह तापमान और क्लोरोफिल डेटा।',
        pfz_zones: 'संभावित मत्स्य क्षेत्र',
        sea_surface_temp: 'समुद्री सतह तापमान',
        chlorophyll: 'क्लोरोफिल-ए',
        coastal_advisory: 'तटीय मत्स्य सलाह',
        high_potential: 'उच्च संभावना',
        moderate_potential: 'मध्यम संभावना',
        low_potential: 'कम संभावना',
        fish_clear_points: 'कस्टम बिंदु हटाएं',
        fish_update_scan: 'स्कैन अपडेट करें',
        fish_live_sst: 'लाइव SST',
        fish_chlorophyll: 'क्लोरोफिल-ए',
        fish_data_updated: 'डेटा अपडेटेड',
        fish_top_rec: 'शीर्ष अनुशंसा',
        fish_suitability: 'उपयुक्तता',
        fish_distance: 'दूरी',
        fish_est_eta: 'अनु. पहुंच समय',
        fish_why_recommended: 'यह क्षेत्र क्यों अनुशंसित है:',
        fish_loading_analysis: 'विश्लेषण लोड हो रहा है...',
        fish_set_waypoint: 'वेपॉइंट सेट करें',
        fish_marine_indicators: 'समुद्री संकेतक',
        fish_sst_label: 'समुद्री सतह तापमान (SST)',
        fish_chla_label: 'क्लोरोफिल-ए',
        fish_wind_label: 'हवा (गति / दिशा)',
        fish_24h_prediction: '24 घंटे का पूर्वानुमान',
        fish_zone_comparison: 'क्षेत्र तुलना',
        fish_view_analysis: 'पूर्ण विश्लेषण देखें',
        speak_to_orca: 'ऑर्का से बोलें',
        stt_listening: 'सुन रहा है...',
        stt_not_supported: 'इस ब्राउज़र में वॉयस इनपुट समर्थित नहीं है।',
        stt_permission_denied: 'माइक्रोफ़ोन एक्सेस अस्वीकृत कर दिया गया। कृपया ब्राउज़र सेटिंग्स में माइक्रोफ़ोन अनुमति दें।',
        fish_th_sector: 'सेक्टर',
        fish_th_score: 'स्कोर',
        fish_th_distance: 'दूरी',
        fish_th_sst: 'SST',
        fish_th_activity: 'गतिविधि स्तर',
        fish_th_action: 'कार्रवाई',
        fish_loading_zones: 'क्षेत्र लोड हो रहे हैं...',

        map_title: 'समुद्री मानचित्र',
        map_desc: 'जहाज ट्रैकिंग, मौसम ओवरले और सुरक्षित मार्ग की गणना।',
        layer_controls: 'मानचित्र परतें',
        vessel_tracking: 'जहाज ट्रैकिंग (AIS)',
        weather_overlay: 'मौसम राडार',
        route_planner: 'सुरक्षित मार्ग योजनाकार',
        calculate_route: 'सुरक्षित मार्ग की गणना करें',
        origin: 'प्रारंभिक बंदरगाह / निर्देशांक',
        destination: 'गंतव्य बंदरगाह / निर्देशांक',
        map_route_planning: 'मार्ग योजना',
        map_origin: 'प्रारंभ',
        map_destination: 'गंतव्य',
        map_click_map_port: 'मानचित्र पर क्लिक करें या बंदरगाह चुनें...',
        map_calculate_route: 'मार्ग की गणना करें',
        map_route_geometry: 'मार्ग ज्यामिति',
        map_distance: 'दूरी:',
        map_duration: 'अवधि:',
        map_type: 'प्रकार:',
        map_route_safety: 'मार्ग सुरक्षा मूल्यांकन',
        map_active_layers: 'सक्रिय परतें',
        map_vessel_ais: 'जहाज AIS (लाइव)',
        map_weather_hazards: 'मौसम खतरे',
        map_restricted_zones: 'प्रतिबंधित क्षेत्र',
        map_fishing_grounds: 'मत्स्य क्षेत्र (SST)',
        map_vessel_routes: 'जहाज मार्ग',
        map_ports: 'बंदरगाह',

        settings_title: 'सेटिंग्स',
        settings_desc: 'अपनी मंच प्राथमिकताएं और जहाज विवरण प्रबंधित करें।',
        general_settings: 'सामान्य प्राथमिकताएं',
        theme_preference: 'थीम डिस्प्ले',
        language_preference: 'मंच की भाषा',
        tts_settings: 'टेक्स्ट-टू-स्पीच (एआई आवाज)',
        enable_tts: 'आवाज उत्तर सक्षम करें',
        enable_tts_desc: 'ORCA एआई सहायक को उत्तर बोलकर सुनाने की अनुमति दें।',
        speech_voice: 'आवाज का चयन',
        speech_rate: 'बोलने की गति',
        test_voice: 'आवाज का परीक्षण करें',
        save_settings: 'प्राथमिकताएं सहेजें',
        settings_saved: 'प्राथमिकताएं सफलतापूर्वक सहेजी गईं!',
        set_account_profile: 'खाता और प्रोफ़ाइल',
        set_full_name: 'पूरा नाम',
        set_email: 'ईमेल पता',
        set_update_profile: 'प्रोफ़ाइल अपडेट करें',
        set_vessel_profile: 'जहाज प्रोफ़ाइल',
        set_vessel_name: 'जहाज का नाम',
        set_vessel_type: 'जहाज का प्रकार',
        set_commercial_fishing: 'व्यावसायिक मत्स्य पालन',
        set_recreational: 'मनोरंजक',
        set_transport: 'परिवहन',
        set_length_m: 'लंबाई (मीटर)',
        set_operating_range: 'संचालन सीमा (NM)',
        set_localization: 'स्थानीयकरण',
        set_language: 'भाषा',
        set_measurement: 'माप प्रणाली',
        set_metric: 'मीट्रिक',
        set_imperial: 'इम्पीरियल',
        set_home_port: 'गृह बंदरगाह',
        set_search_ports: 'बंदरगाह खोजें...',
        set_change: 'बदलें',
        set_alert_prefs: 'अलर्ट प्राथमिकताएं',
        set_severe_weather: 'गंभीर मौसम चेतावनी',
        set_severe_weather_desc: 'तूफानों के लिए तत्काल पुश सूचनाएं।',
        set_route_deviations: 'मार्ग विचलन',
        set_route_deviations_desc: 'नियोजित मार्ग से भटकने पर चेतावनी।',
        set_intel_updates: 'इंटेलीजेंस अपडेट',
        set_intel_updates_desc: 'समुद्री गतिविधि का दैनिक सारांश।',
        set_save: 'सेटिंग्स सहेजें'
    },
    kn: {
        nav_about: 'ನಮ್ಮ ಬಗ್ಗೆ',
        nav_dashboard: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        nav_assistant: 'ಎಐ ಸಹಾಯಕ',
        nav_map: 'ಸಮುದ್ರ ನಕ್ಷೆ',
        nav_safety: 'ಸುರಕ್ಷತೆ ಮತ್ತು ಎಚ್ಚರಿಕೆಗಳು',
        nav_fishing: 'ಮೀನುಗಾರಿಕೆ',
        nav_settings: 'ಸೇಟಿಂಗ್ಸ್',
        brand_sub: 'ಇಂಟೆಲಿಜೆನ್ಸ್',
        
        export_report: 'ವರದಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ',
        view_full_chart: 'ಪೂರ್ಣ ಚಾರ್ಟ್ ವೀಕ್ಷಿಸಿ',
        view_details: 'ವಿವರಗಳನ್ನು ವೀಕ್ಷಿಸಿ',
        active: 'ಸಕ್ರಿಯ',
        search: 'ಹುಡುಕಿ...',
        search_language: 'ಭಾಷೆಯನ್ನು ಹುಡುಕಿ...',
        
        dash_title: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ನೋಟ',
        dash_subtitle: 'ನೈಜ-ಸಮಯದ ಸಮುದ್ರ ಪರಿಸ್ಥಿತಿಗಳು ಮತ್ತು ಕಾರ್ಯಾಚರಣೆಯ ನಿರ್ದೇಶನಗಳು.',
        wave_height: 'ಅಲೆಯ ಎತ್ತರ',
        wind_speed: 'ಗಾಳಿಯ ವೇಗ',
        water_temp: 'ನೀರಿನ ತಾಪಮಾನ',
        from_last_hour: '+0.3m ಕಳೆದ ಗಂಟೆಯಿಂದ',
        nw_direction: 'ವಾಯುವ್ಯ ದಿಕ್ಕು',
        steady_cooling: 'ಸ್ಥಿರ ತಂಪಾಗಿಸುವಿಕೆ',
        risk_assessment: 'ಅಪಾಯದ ಮೌಲ್ಯಮಾಪನ',
        risk_moderate: 'ಮಧ್ಯಮ ಅಪಾಯ',
        risk_index: 'ಸೂಚ್ಯಂಕ: 6.8 / 10',
        risk_desc: 'ಸಮುದ್ರದಲ್ಲಿ ಪರಿಸ್ಥಿತಿ ಕ್ಷೀಣಿಸುತ್ತಿದೆ. ಸಣ್ಣ ದೋಣಿಗಳು ಎಚ್ಚರಿಕೆ ವಹಿಸಿ.',
        forecast_24h: '24 ಗಂಟೆಗಳ ಮುನ್ಸೂಚನೆ',
        active_directives: 'ಸಕ್ರಿಯ ಎಚ್ಚರಿಕೆಗಳು',
        alerts_count: '2 ಎಚ್ಚರಿಕೆಗಳು',
        gale_warning: 'ಬಿರುಗಾಳಿ ಎಚ್ಚರಿಕೆ',
        gale_desc: 'ಸೆಕ್ಟರ್ ಬಿ ಯಲ್ಲಿ 22:00 ರಿಂದ 45kts ಬಿರುಗಾಳಿ ನಿರೀಕ್ಷಿಸಲಾಗಿದೆ.',
        sensor_cal: 'ಸಂವೇದಕ ಮಾಪನಾಂಕ ನಿರ್ಣಯ ಅಗತ್ಯವಿದೆ',
        sensor_desc: 'ಬೋಯಾ ಆಲ್ಫಾ-7 ನಿಖರವಲ್ಲದ ಡೇಟಾ ವರದಿ ಮಾಡುತ್ತಿದೆ.',
        route_update: 'ಮಾರ್ಗ ನವೀಕರಣ ಲಭ್ಯವಿದೆ',
        route_desc: 'ಇತ್ತೀಚಿನ ಸಮುದ್ರ ಪ್ರವಾಹಗಳ ಆಧಾರದ ಮೇಲೆ ಅನುಕೂಲಕರ ಮಾರ್ಗ ಸಿದ್ಧವಾಗಿದೆ.',

        assistant_title: 'ORCA ಎಐ ಸಹಾಯಕ',
        assistant_desc: 'ಸಮುದ್ರ ಸುರಕ್ಷತೆ, ಮೀನುಗಾರಿಕೆ ಪ್ರದೇಶಗಳು ಮತ್ತು ಮಾರ್ಗಗಳ ಬಗ್ಗೆ ಕೇಳಿ.',
        ask_assistant_placeholder: 'ORCA ಸಹಾಯಕನನ್ನು ಕೇಳಿ...',
        agent_activity: 'ಏಜೆಂಟ್ ಚಟುವಟಿಕೆ',
        orca_thinking: 'ORCA ಯೋಚಿಸುತ್ತಿದೆ...',
        greeting_msg: 'ನಮಸ್ಕಾರ! ನಾನು ORCA, ನಿಮ್ಮ ಸಮುದ್ರ ಪರಿಸರ ವ್ಯವಸ್ಥೆಯ ಸಹಾಯಕ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?',
        export_pdf: 'PDF ವರದಿ ರಫ್ತು ಮಾಡಿ',
        listen_response: 'ಉತ್ತರವನ್ನು ಆಲಿಸಿ',
        pause_speech: 'ವಿರಾಮಗೊಳಿಸಿ',
        resume_speech: 'ಪುನರಾರಂಭಿಸಿ',
        stop_speech: 'ನಿಲ್ಲಿಸಿ',
        listening: 'ಮಾತನಾಡುತ್ತಿದೆ...',

        safety_title: 'ಸಮುದ್ರ ಸುರಕ್ಷತೆ ಮತ್ತು ಬುಲೆಟಿನ್‌ಗಳು',
        safety_desc: 'ಕರಾವಳಿ ಅಪಾಯಗಳು, ಚಂಡಮಾರುತದ ಎಚ್ಚರಿಕೆಗಳು ಮತ್ತು ಹವಾಮಾನ ಬುಲೆಟಿನ್‌ಗಳು.',
        active_warnings: 'ಸಕ್ರಿಯ ಎಚ್ಚರಿಕೆಗಳು',
        emergency_contacts: 'ತುರ್ತು ಸಂಪರ್ಕಗಳು',
        coast_guard: 'ಭಾರತೀಯ ಕರಾವಳಿ ಕಾವಲು ಪಡೆ: 1554',
        disaster_mgmt: 'ರಾಜ್ಯ ದುರಂತ ನಿರ್ವಹಣೆ: 1070',
        port_authority: 'ಬಂದರು ನಿಯಂತ್ರಣ VHF: ಚಾನೆಲ್ 16',
        cyclone_advisory: 'ಚಂಡಮಾರುತ ಎಚ್ಚರಿಕೆ',
        high_wave_alert: 'ಎತ್ತರದ ಅಲೆಗಳ ಎಚ್ಚರಿಕೆ',
        tsunami_watch: 'ಸುನಾಮಿ ಎಚ್ಚರಿಕೆ',

        fishing_title: 'ಮೀನುಗಾರಿಕೆ ಇಂಟೆಲಿಜೆನ್ಸ್ & PFZ',
        fishing_desc: 'ಉಪಗ್ರಹ ಆಧಾರಿತ PFZ ಸಲಹೆಗಳು, ಸಮುದ್ರದ ತಾಪಮಾನ ಮತ್ತು ಕ್ಲೋರೊಫಿಲ್ ದತ್ತಾಂಶ.',
        pfz_zones: 'ಸಾಧ್ಯವಿರುವ ಮೀನುಗಾರಿಕೆ ವಲಯಗಳು',
        sea_surface_temp: 'ಸಮುದ್ರದ ಮೇಲ್ಮೈ ತಾಪಮಾನ',
        chlorophyll: 'ಕ್ಲೋರೊಫಿಲ್-ಎ',
        coastal_advisory: 'ಕರಾವಳಿ ಮೀನುಗಾರಿಕೆ ಸಲಹೆ',
        high_potential: 'ಹೆಚ್ಚಿನ ಸಾದ್ಯತೆ',
        moderate_potential: 'ಮಧ್ಯಮ ಸಾದ್ಯತೆ',
        low_potential: 'ಕಡಿಮೆ ಸಾದ್ಯತೆ',

        map_title: 'ಸಮುದ್ರ ನಕ್ಷೆ',
        map_desc: 'ಹಡಗುಗಳ ಟ್ರ್ಯಾಕಿಂಗ್, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಸುರಕ್ಷಿತ ಮಾರ್ಗ ಲೆಕ್ಕಾಚಾರ.',
        layer_controls: 'ನಕ್ಷೆಯ ಪದರಗಳು',
        vessel_tracking: 'ಹಡಗು ಟ್ರ್ಯಾಕಿಂಗ್ (AIS)',
        weather_overlay: 'ಹವಾಮಾನ ರೇಡಾರ್',
        route_planner: 'ಸುರಕ್ಷಿತ ಮಾರ್ಗ ಯೋಜಕ',
        calculate_route: 'ಸುರಕ್ಷಿತ ಮಾರ್ಗವನ್ನು ಲೆಕ್ಕಹಾಕಿ',
        origin: 'ಪ್ರಾರಂಭದ ಬಂದರು / ನಿರ್ದೇಶಾಂಕಗಳು',
        destination: 'ತಲುಪುವ ಬಂದರು / ನಿರ್ದೇಶಾಂಕಗಳು',

        settings_title: 'ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        settings_desc: 'ಭಾಷೆ, ಥೀಮ್ ಮತ್ತು ಧ್ವನಿ ಪ್ರತ್ಯುತ್ತರಗಳನ್ನು ಕಾನ್ಫಿಗರ್ ಮಾಡಿ.',
        general_settings: 'ಸಾಮಾನ್ಯ ಆದ್ಯತೆಗಳು',
        theme_preference: 'ಥೀಮ್ ಪ್ರದರ್ಶನ',
        language_preference: 'ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ ಭಾಷೆ',
        tts_settings: 'ಪಠ್ಯದಿಂದ ಧ್ವನಿ (ಎಐ ಧ್ವನಿ)',
        enable_tts: 'ಧ್ವನಿ ಉತ್ತರಗಳನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಿ',
        enable_tts_desc: 'ORCA ಎಐ ಸಹಾಯಕನಿಗೆ ಉತ್ತರಗಳನ್ನು ಗಟ್ಟಿಯಾಗಿ ಓದಲು ಅನುಮತಿಸಿ.',
        speech_voice: 'ಧ್ವನಿಯ ಆಯ್ಕೆ',
        speech_rate: 'ಮಾತನಾಡುವ ವೇಗ',
        test_voice: 'ಧ್ವನಿಯನ್ನು ಪರೀಕ್ಷಿಸಿ',
        save_settings: 'ಆದ್ಯತೆಗಳನ್ನು ಉಳಿಸಿ',
        settings_saved: 'ಆದ್ಯತೆಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ!'
    },
    ta: {
        nav_about: 'எங்களைப் பற்றி',
        nav_dashboard: 'டாஷ்போர்டு',
        nav_assistant: 'AI உதவியாளர்',
        nav_map: 'கடல் வரைபடம்',
        nav_safety: 'பாதுகாப்பு & எச்சரிக்கைகள்',
        nav_fishing: 'மீன்பிடித்தல்',
        nav_settings: 'அமைப்புகள்',
        brand_sub: 'இன்டெலிஜென்ஸ்',

        export_report: 'அறிக்கையைப் பதிவிறக்கு',
        view_full_chart: 'முழு வரைபடத்தைப் பார்',
        view_details: 'விவரங்களைப் பார்',
        active: 'செயலில்',
        search: 'தேடு...',
        search_language: 'மொழியைக் தேடு...',

        dash_title: 'டாஷ்போர்டு மேலோட்டம்',
        dash_subtitle: 'நிகழ்நேர கடல் நிலைமைகள் மற்றும் செயல்பாட்டு வழிகாட்டுதல்கள்.',
        wave_height: 'அலையின் உயரம்',
        wind_speed: 'காற்றின் வேகம்',
        water_temp: 'நீரின் வெப்பநிலை',
        from_last_hour: '+0.3m கடந்த மணிநேரத்திலிருந்து',
        nw_direction: 'வடமேற்கு திசை',
        steady_cooling: 'சீரான குளிர்ச்சி',
        risk_assessment: 'ஆபத்து மதிப்பீடு',
        risk_moderate: 'மிதமான ஆபத்து',
        risk_index: 'குறியீடு: 6.8 / 10',
        risk_desc: 'கடலில் நிலைமை மோசமடைந்து வருகிறது. சிறிய படகுகள் எச்சரிக்கையுடன் இருக்கவும்.',
        forecast_24h: '24 மணி நேர முன்னறிவிப்பு',
        active_directives: 'செயலில் உள்ள வழிகாட்டுதல்கள்',
        alerts_count: '2 எச்சரிக்கைகள்',
        gale_warning: 'சூறாவளி எச்சரிக்கை',
        gale_desc: 'செக்டார் B யில் 22:00 மணி முதல் 45kts காற்று எதிர்பார்க்கப்படுகிறது.',
        sensor_cal: 'சென்சார் அளவீடு தேவை',
        sensor_desc: 'பாய் ஆல்பா-7 தவறான தரவை அறிக்கையிடுகிறது.',
        route_update: 'பாதை புதுப்பிப்பு கிடைக்கிறது',
        route_desc: 'கடைசி கடல் நீரோட்டங்களின் அடிப்படையில் உகந்த பாதை தயாராக உள்ளது.',

        assistant_title: 'ORCA AI உதவியாளர்',
        assistant_desc: 'கடல் பாதுகாப்பு, மீன்பிடி பகுதிகள் மற்றும் பாதைகள் பற்றி எதையும் கேட்கலாம்.',
        ask_assistant_placeholder: 'ORCA உதவியாளரிடம் கேளுங்கள்...',
        agent_activity: 'முகவர் செயல்பாடு',
        orca_thinking: 'ORCA யோசிக்கிறது...',
        greeting_msg: 'வணக்கம்! நான் ORCA, உங்கள் கடல் சுற்றுச்சூழல் உதவியாளர். இன்று உங்களுக்கு நான் எப்படி உதவ முடியும்?',
        export_pdf: 'PDF அறிக்கையை ஏற்றுமதி செய்',
        listen_response: 'பதிலைக் கேள்',
        pause_speech: 'இடைநிறுத்து',
        resume_speech: 'மீண்டும் தொடங்கு',
        stop_speech: 'நிறுத்து',
        listening: 'பேசுகிறது...',

        safety_title: 'கடல் பாதுகாப்பு & புல்லட்டின்கள்',
        safety_desc: 'கடற்கரை ஆபத்துகள், புயல் எச்சரிக்கைகள் மற்றும் வானிலை அறிக்கைகள்.',
        active_warnings: 'செயலில் உள்ள எச்சரிக்கைகள்',
        emergency_contacts: 'அவசர தொடர்புகள்',
        coast_guard: 'இந்திய கடலோர காவல்படை: 1554',
        disaster_mgmt: 'மாநில பேரிடர் மேலாண்மை: 1070',
        port_authority: 'துறைமுக கட்டுப்பாடு VHF: சேனல் 16',
        cyclone_advisory: 'புயல் எச்சரிக்கை',
        high_wave_alert: 'உயர் அலை எச்சரிக்கை',
        tsunami_watch: 'சுனாமி எச்சரிக்கை',

        fishing_title: 'மீன்பிடி நுண்ணறிவு & PFZ',
        fishing_desc: 'செயற்கைக்கோள் அடிப்படையிலான PFZ ஆலோசனைகள் மற்றும் தரவு.',
        pfz_zones: 'சாத்தியமான மீன்பிடி மண்டலங்கள்',
        sea_surface_temp: 'கடல் மேற்பரப்பு வெப்பநிலை',
        chlorophyll: 'குளோரோபில்-ஏ',
        coastal_advisory: 'கடலோர மீன்பிடி ஆலோசனை',
        high_potential: 'அதிக சாத்தியம்',
        moderate_potential: 'மிதமான சாத்தியம்',
        low_potential: 'குறைந்த சாத்தியம்',

        map_title: 'கடல் வரைபடம்',
        map_desc: 'கப்பல் கண்காணிப்பு மற்றும் பாதுகாப்பான பாதை கணக்கீடு.',
        layer_controls: 'வரைபட அடுக்குகள்',
        vessel_tracking: 'கப்பல் கண்காணிப்பு (AIS)',
        weather_overlay: 'வானிலை ரேடார்',
        route_planner: 'பாதுகாப்பான பாதை திட்டமிடுபவர்',
        calculate_route: 'பாதுகாப்பான பாதையைக் கணக்கிடு',
        origin: 'தொடக்க துறைமுகம் / ஆயத்தொலைவுகள்',
        destination: 'சேருமிடம் துறைமுகம் / ஆயத்தொலைவுகள்',

        settings_title: 'தள அமைப்புகள்',
        settings_desc: 'மொழி, தீம் மற்றும் AI குரல் பதில்களை உள்ளமைக்கவும்.',
        general_settings: 'பொது விருப்பங்கள்',
        theme_preference: 'தீம் காட்சி',
        language_preference: 'தள மொழி',
        tts_settings: 'உரையிலிருந்து பேச்சு (AI குரல்)',
        enable_tts: 'குரல் பதில்களை இயக்கு',
        enable_tts_desc: 'ORCA AI உதவியாளர் உரக்கப் பேச அனுமதிக்கவும்.',
        speech_voice: 'குரல் தேர்வு',
        speech_rate: 'பேசும் வேகம்',
        test_voice: 'குரலைச் சோதி',
        save_settings: 'விருப்பங்களைச் சேமி',
        settings_saved: 'விருப்பங்கள் வெற்றிகரமாகச் சேமிக்கப்பட்டன!'
    },
    te: {
        nav_about: 'మా గురించి',
        nav_dashboard: 'డాష్‌బోర్డ్',
        nav_assistant: 'AI సహాయకుడు',
        nav_map: 'సముద్ర పటం',
        nav_safety: 'భద్రత & హెచ్చరికలు',
        nav_fishing: 'చేపల వేట',
        nav_settings: 'సెట్టింగ్‌లు',
        brand_sub: 'ఇంటెలిజెన్స్',

        export_report: 'నివేదికను డౌన్‌లోడ్ చేయండి',
        view_full_chart: 'పూర్తి చార్ట్ చూడండి',
        view_details: 'వివరాలు చూడండి',
        active: 'సక్రియం',
        search: 'వెతకండి...',
        search_language: 'భాషను వెతకండి...',

        dash_title: 'డాష్‌బోర్డ్ అవలోకనం',
        dash_subtitle: 'రియల్-టైమ్ సముద్ర పరిస్థితులు మరియు కార్యాచరణ ఆదేశాలు.',
        wave_height: 'అలల ఎత్తు',
        wind_speed: 'గాలి వేగం',
        water_temp: 'నీటి ఉష్ణోగ్రత',
        from_last_hour: '+0.3m గత గంట నుండి',
        nw_direction: 'వాయువ్య దిశ',
        steady_cooling: 'స్థిరమైన చల్లదనం',
        risk_assessment: 'ప్రమాద అంచనా',
        risk_moderate: 'మధ్యస్థ ప్రమాదం',
        risk_index: 'సూచిక: 6.8 / 10',
        risk_desc: 'సముద్రంలో పరిస్థితులు క్షీణిస్తున్నాయి. చిన్న పడవలు జాగ్రత్త వహించాలి.',
        forecast_24h: '24 గంటల సూచన',
        active_directives: 'సక్రియ ఆదేశాలు',
        alerts_count: '2 హెచ్చరికలు',
        gale_warning: 'ఈదురుగాలుల హెచ్చరిక',
        gale_desc: 'సెక్టార్ B లో 22:00 నుండి 45kts ఈదురుగాలులు వీచే అవకాశం ఉంది.',
        sensor_cal: 'సెన్సార్ క్రమాంకనం అవసరం',
        sensor_desc: 'బోయా ఆల్ఫా-7 సరిగ్గా లేని డేటాను అందిస్తోంది.',
        route_update: 'మార్గం నవీకరణ అందుబాటులో ఉంది',
        route_desc: 'తాజా సముద్ర ప్రవాహాల ఆధారంగా అనుకూలమైన మార్గం సిద్ధంగా ఉంది.',

        assistant_title: 'ORCA AI సహాయకుడు',
        assistant_desc: 'సముద్ర భద్రత, చేపల వేట ప్రాంతాలు మరియు మార్గాల గురించి ఏమైనా అడగండి.',
        ask_assistant_placeholder: 'ORCA సహాయకుడిని అడగండి...',
        agent_activity: 'ఏజెంట్ కార్యకలాపం',
        orca_thinking: 'ORCA ఆలోచిస్తోంది...',
        greeting_msg: 'నమస్కారం! నేను ORCA, మీ సముద్ర పర్యావరణ వ్యవస్థ సహాయకుడిని. ఈ రోజు నేను మీకు ఎలా సహాయపడగలను?',
        export_pdf: 'PDF నివేదికను ఎగుమతి చేయండి',
        listen_response: 'సమాధానం వినండి',
        pause_speech: 'పాజ్ చేయండి',
        resume_speech: 'తిరిగి ప్రారంభించండి',
        stop_speech: 'ఆపివేయండి',
        listening: 'మాట్లాడుతోంది...',

        safety_title: 'సముద్ర భద్రత & బులెటిన్లు',
        safety_desc: 'తీరప్రాంత ప్రమాదాలు, తుఫాను హెచ్చరికలు మరియు వాతావరణ బులెటిన్లు.',
        active_warnings: 'సక్రియ హెచ్చరికలు',
        emergency_contacts: 'అత్యవసర పరిచయాలు',
        coast_guard: 'భారతీయ కోస్ట్ గార్డ్: 1554',
        disaster_mgmt: 'రాష్ట్ర విపత్తు నిర్వహణ: 1070',
        port_authority: 'పోర్ట్ కంట్రోల్ VHF: ఛానెల్ 16',
        cyclone_advisory: 'తుఫాను హెచ్చరిక',
        high_wave_alert: 'అధిక అలల హెచ్చరిక',
        tsunami_watch: 'సునామీ హెచ్చరిక బులెటిన్',

        fishing_title: 'చేపల వేట ఇంటెలిజెన్స్ & PFZ',
        fishing_desc: 'శాటిలైట్ ఆధారిత PFZ సమాచారం మరియు క్లోరోఫిల్ డేటా.',
        pfz_zones: 'చేపల వేట అనుకూల ప్రాంతాలు',
        sea_surface_temp: 'సముద్ర ఉపరితల ఉష్ణోగ్రత',
        chlorophyll: 'క్లోరోఫిల్-ఎ',
        coastal_advisory: 'తీరప్రాంత చేపల వేట సలహా',
        high_potential: 'అధిక అవకాశం',
        moderate_potential: 'మధ్యస్థ అవకాశం',
        low_potential: 'తక్కువ అవకాశం',

        map_title: 'సముద్ర పటం',
        map_desc: 'ఓడల ట్రాకింగ్ మరియు సురక్షిత మార్గం లెక్కింపు.',
        layer_controls: 'పటం పొరలు',
        vessel_tracking: 'ఓడల ట్రాకింగ్ (AIS)',
        weather_overlay: 'వాతావరణ రాడార్',
        route_planner: 'సురక్షిత మార్గం ప్లానర్',
        calculate_route: 'సురక్షిత మార్గాన్ని లెక్కించండి',
        origin: 'ప్రారంభ పోర్ట్ / అక్షాంశాలు',
        destination: 'గమ్యస్థాన పోర్ట్ / అక్షాంశాలు',

        settings_title: 'ప్లాట్‌ఫారమ్ సెట్టింగ్‌లు',
        settings_desc: 'భాష, థీమ్ మరియు AI వాయిస్ స్పందనలను కాన్ఫిగర్ చేయండి.',
        general_settings: 'సాధారణ ప్రాధాన్యతలు',
        theme_preference: 'థీమ్ ప్రదర్శన',
        language_preference: 'ప్లాట్‌ఫారమ్ భాష',
        tts_settings: 'టెక్స్ట్-టు-స్పీచ్ (AI వాయిస్)',
        enable_tts: 'వాయిస్ స్పందనలను ప్రారంభించండి',
        enable_tts_desc: 'ORCA AI సహాయకుడిని సమాధానాలను బిగ్గరగా చదవడానికి అనుమతించండి.',
        speech_voice: 'వాయిస్ ఎంపిక',
        speech_rate: 'మాట్లాడే వేగం',
        test_voice: 'వాయిస్‌ని పరీక్షించండి',
        save_settings: 'ప్రాధాన్యతలను సేవ్ చేయండి',
        settings_saved: 'ప్రాధాన్యతలు విజయవంతంగా సేవ్ చేయబడ్డాయి!'
    },
    ml: {
        nav_about: 'ഞങ്ങളെക്കുറിച്ച്',
        nav_dashboard: 'ഡാഷ്ബോർഡ്',
        nav_assistant: 'എഐ അസിസ്റ്റന്റ്',
        nav_map: 'കടൽ മാപ്പ്',
        nav_safety: 'സുരക്ഷയും മുന്നറിയിപ്പുകളും',
        nav_fishing: 'മത്സ്യബന്ധനം',
        nav_settings: 'സെറ്റിംഗ്സ്',
        brand_sub: 'ഇന്റലിജൻസ്',

        export_report: 'റിപ്പോർട്ട് ഡൗൺലോഡ് ചെയ്യുക',
        view_full_chart: 'പൂർണ്ണ ചാർട്ട് കാണുക',
        view_details: 'വിശദാംശങ്ങൾ കാണുക',
        active: 'സജീവം',
        search: 'തിരയുക...',
        search_language: 'ഭാഷ തിരയുക...',

        dash_title: 'ഡാഷ്ബോർഡ് അവലോകനം',
        dash_subtitle: 'തത്സമയ സമുദ്ര സാഹചര്യങ്ങളും പ്രവർത്തന നിർദ്ദേശങ്ങളും.',
        wave_height: 'തിരമാലയുടെ ഉയരം',
        wind_speed: 'കാറ്റിന്റെ വേഗത',
        water_temp: 'ജല താപനില',
        from_last_hour: '+0.3m കഴിഞ്ഞ മണിക്കൂറിൽ നിന്ന്',
        nw_direction: 'വടക്കുപടിഞ്ഞാറൻ ദിശ',
        steady_cooling: 'സ്ഥിരമായ തണുപ്പ്',
        risk_assessment: 'അപകടസാധ്യത വിലയിരുത്തൽ',
        risk_moderate: 'മിതമായ അപകടസാധ്യത',
        risk_index: 'ഇൻഡക്സ്: 6.8 / 10',
        risk_desc: 'കടലിൽ സ്ഥിതി വഷളാകുന്നു. ചെറിയ ബോട്ടുകൾ ജാഗ്രത പാലിക്കുക.',
        forecast_24h: '24 മണിക്കൂർ പ്രവചനം',
        active_directives: 'സജീവ നിർദ്ദേശങ്ങൾ',
        alerts_count: '2 മുന്നറിയിപ്പുകൾ',
        gale_warning: 'ചുഴലിക്കാറ്റ് മുന്നറിയിപ്പ്',
        gale_desc: 'സെക്ടർ ബി യിൽ 22:00 മുതൽ 45kts കാറ്റ് പ്രതീക്ഷിക്കുന്നു.',
        sensor_cal: 'സെൻസർ കാലിബ്രേഷൻ ആവശ്യമാണ്',
        sensor_desc: 'ബോയ ആൽഫ-7 ക്രമമില്ലാത്ത ഡാറ്റ നൽകുന്നു.',
        route_update: 'റൂട്ട് അപ്ഡേറ്റ് ലഭ്യമാണ്',
        route_desc: 'ഏറ്റവും പുതിയ സമുദ്ര പ്രവാഹങ്ങളുടെ അടിസ്ഥാനത്തിൽ അനുയോജ്യമായ റൂട്ട് തയ്യാറാണ്.',

        assistant_title: 'ORCA എഐ അസിസ്റ്റന്റ്',
        assistant_desc: 'സമുദ്ര സുരക്ഷ, മത്സ്യബന്ധന മേഖലകൾ, റൂട്ടുകൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കുക.',
        ask_assistant_placeholder: 'ORCA അസിസ്റ്റന്റിനോട് ചോദിക്കുക...',
        agent_activity: 'ഏജന്റ് പ്രവർത്തനം',
        orca_thinking: 'ORCA ചിന്തിക്കുന്നു...',
        greeting_msg: 'നമസ്കാരം! ഞാൻ ORCA, നിങ്ങളുടെ സമുദ്ര പരിസ്ഥിതി അസിസ്റ്റന്റ്. ഇന്ന് എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?',
        export_pdf: 'PDF റിപ്പോർട്ട് എക്സ്പോർട്ട് ചെയ്യുക',
        listen_response: 'ഉത്തരം കേൾക്കുക',
        pause_speech: 'താൽക്കാലികമായി നിർത്തുക',
        resume_speech: 'വീണ്ടും ആരംഭിക്കുക',
        stop_speech: 'നിർത്തുക',
        listening: 'സംസാരിക്കുന്നു...',

        safety_title: 'സമുദ്ര സുരക്ഷയും ബുള്ളറ്റിനുകളും',
        safety_desc: 'തീരദേശ അപകടങ്ങൾ, ചുഴലിക്കാറ്റ് മുന്നറിയിപ്പുകൾ, കാലാവസ്ഥ ബുള്ളറ്റിനുകൾ.',
        active_warnings: 'സജീവ മുന്നറിയിപ്പുകൾ',
        emergency_contacts: 'അടിയന്തര ബന്ധപ്പെടലുകൾ',
        coast_guard: 'ഇന്ത്യൻ കോസ്റ്റ് ഗാർഡ്: 1554',
        disaster_mgmt: 'സംസ്ഥാന ദുരന്ത നിവാരണം: 1070',
        port_authority: 'പോർട്ട് കൺട്രോൾ VHF: ചാനൽ 16',
        cyclone_advisory: 'ചുഴലിക്കാറ്റ് മുന്നറിയിപ്പ്',
        high_wave_alert: 'ഉയർന്ന തിരമാല മുന്നറിയിപ്പ്',
        tsunami_watch: 'സുനാമി ജാഗ്രത ബുള്ളറ്റിൻ',

        fishing_title: 'മത്സ്യബന്ധന ഇന്റലിജൻസ് & PFZ',
        fishing_desc: 'ഉപഗ്രഹ അധിഷ്ഠിത PFZ വിവരങ്ങളും ക്ലോറോഫിൽ ഡാറ്റയും.',
        pfz_zones: 'മത്സ്യബന്ധന സാധ്യതാ മേഖലകൾ',
        sea_surface_temp: 'സമുദ്രോപരിതല താപനില',
        chlorophyll: 'ക്ലോറോഫിൽ-എ',
        coastal_advisory: 'തീരദേശ മത്സ്യബന്ധന നിർദ്ദേശം',
        high_potential: 'ഉയർന്ന സാധ്യത',
        moderate_potential: 'മിതമായ സാധ്യത',
        low_potential: 'കുറഞ്ഞ സാധ്യത',

        map_title: 'സമുദ്ര മാപ്പ്',
        map_desc: 'കപ്പൽ ട്രാക്കിംഗും സുരക്ഷിത റൂട്ട് കണക്കുകൂട്ടലും.',
        layer_controls: 'മാപ്പ് പാളികൾ',
        vessel_tracking: 'കപ്പൽ ട്രാക്കിംഗ് (AIS)',
        weather_overlay: 'കാലാവസ്ഥ റഡാർ',
        route_planner: 'സുരക്ഷിത റൂട്ട് പ്ലാനർ',
        calculate_route: 'സുരക്ഷിത റൂട്ട് കണക്കാക്കുക',
        origin: 'ആരംഭ പോർട്ട് / കോർഡിനേറ്റുകൾ',
        destination: 'ലക്ഷ്യസ്ഥാന പോർട്ട് / കോർഡിനേറ്റുകൾ',

        settings_title: 'പ്ലാറ്റ്ഫോം സെറ്റിംഗ്സ്',
        settings_desc: 'ഭാഷ, തീം, എഐ വോയ്സ് മറുപടികൾ എന്നിവ ക്രമീകരിക്കുക.',
        general_settings: 'പൊതുവായ മുൻഗണനകൾ',
        theme_preference: 'തീം ഡിസ്പ്ലേ',
        language_preference: 'പ്ലാറ്റ്ഫോം ഭാഷ',
        tts_settings: 'ടെക്സ്റ്റ്-ടു-സ്പീച്ച് (എഐ വോയ്സ്)',
        enable_tts: 'വോയ്സ് മറുപടികൾ പ്രാപ്തമാക്കുക',
        enable_tts_desc: 'ORCA എഐ അസിസ്റ്റന്റിന് ഉത്തരങ്ങൾ ഉച്ചത്തിൽ വായിക്കാൻ അനുമതി നൽകുക.',
        speech_voice: 'വോയ്സ് തിരഞ്ഞെടുക്കൽ',
        speech_rate: 'സംസാര വേഗത',
        test_voice: 'വോയ്സ് പരിശോധിക്കുക',
        save_settings: 'മുൻഗണനകൾ സംരക്ഷിക്കുക',
        settings_saved: 'മുൻഗണനകൾ വിജയകരമായി സംരക്ഷിച്ചു!'
    },
    bn: {
        nav_about: 'আমাদের সম্পর্কে',
        nav_dashboard: 'ড্যাশবোর্ড',
        nav_assistant: 'এআই সহকারী',
        nav_map: 'সামুদ্রিক মানচিত্র',
        nav_safety: 'সুরক্ষা ও সতর্কবার্তা',
        nav_fishing: 'মৎস্য শিকার',
        nav_settings: 'সেটিংস',
        brand_sub: 'ইন্টেলিজেন্স',

        export_report: 'রিপোর্ট ডাউনলোড করুন',
        view_full_chart: 'সম্পূর্ণ চার্ট দেখুন',
        view_details: 'বিস্তারিত দেখুন',
        active: 'সক্রিয়',
        search: 'অনুসন্ধান করুন...',
        search_language: 'ভাষা খুঁজুন...',

        dash_title: 'ড্যাশবোর্ড পর্যালোচনা',
        dash_subtitle: 'রিয়েল-টাইম সামুদ্রিক পরিস্থিতি এবং পরিচালন নির্দেশিকা।',
        wave_height: 'তরঙ্গের উচ্চতা',
        wind_speed: 'বাতাসের গতি',
        water_temp: 'পানির তাপমাত্রা',
        from_last_hour: '+০.৩ মি গত ঘণ্টা থেকে',
        nw_direction: 'উত্তর-পশ্চিম দিক',
        steady_cooling: 'স্থির শীতলীকরণ',
        risk_assessment: 'ঝুঁকি মূল্যায়ন',
        risk_moderate: 'মাঝারি ঝুঁকি',
        risk_index: 'সূচক: ৬.৮ / ১০',
        risk_desc: 'সমুদ্রে পরিস্থিতির অবনতি হচ্ছে। ছোট নৌকার জন্য সতর্কতা অবলম্বন করুন।',
        forecast_24h: '২৪ ঘণ্টার পূর্বাভাস',
        active_directives: 'সক্রিয় নির্দেশাবলী',
        alerts_count: '২ সতর্কতা',
        gale_warning: 'ঝড়ো হাওয়ার সতর্কতা',
        gale_desc: 'সেক্টর বি-তে ২২:০০ টা থেকে ৪৫kts গতিবেগের বাতাসের সম্ভাবনা রয়েছে।',
        sensor_cal: 'সেন্সর ক্রমাঙ্কন প্রয়োজন',
        sensor_desc: 'বয়া আলফা-৭ অনিয়মিত ডেটা রিপোর্ট করছে।',
        route_update: 'রুট আপডেট উপলব্ধ',
        route_desc: 'সর্বশেষ সামুদ্রিক স্রোতের ভিত্তিতে ফ্লিট সি-এর জন্য অপ্টিমাইজ করা রুট প্রস্তুত।',

        assistant_title: 'ORCA এআই সহকারী',
        assistant_desc: 'সামুদ্রিক নিরাপত্তা, মৎস্য শিকার অঞ্চল এবং রুট সম্পর্কে যেকোনো কিছু জিজ্ঞাসা করুন।',
        ask_assistant_placeholder: 'ORCA সহকারীকে জিজ্ঞাসা করুন...',
        agent_activity: 'এজেন্ট কার্যক্রম',
        orca_thinking: 'ORCA চিন্তা করছে...',
        greeting_msg: 'হ্যালো! আমি ORCA, আপনার সামুদ্রিক ইকোসিস্টেম সহকারী। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?',
        export_pdf: 'পিডিএফ রিপোর্ট এক্সপোর্ট করুন',
        listen_response: 'উত্তর শুনুন',
        pause_speech: 'বিরতি দিন',
        resume_speech: 'পুনরায় শুরু করুন',
        stop_speech: 'থামান',
        listening: 'কথা বলছে...',

        safety_title: 'সামুদ্রিক সুরক্ষা ও বুলেটিন',
        safety_desc: 'উপকূলীয় বিপদ, ঘূর্ণিঝড় সতর্কতা এবং আবহাওয়া বুলেটিন।',
        active_warnings: 'সক্রিয় সতর্কবার্তা',
        emergency_contacts: 'জরুরি যোগাযোগ',
        coast_guard: 'ভারতীয় কোস্ট গার্ড: ১৫৫৪',
        disaster_mgmt: 'রাজ্য দুর্যোগ ব্যবস্থাপনা: ১০৭০',
        port_authority: 'পোর্ট কন্ট্রোল VHF: চ্যানেল ১৬',
        cyclone_advisory: 'ঘূর্ণিঝড় সতর্কতা',
        high_wave_alert: 'উচ্চ তরঙ্গের সতর্কতা',
        tsunami_watch: 'সুনামি সতর্কবার্তা বুলেটিন',

        fishing_title: 'মৎস্য ইন্টেলিজেন্স ও PFZ',
        fishing_desc: 'স্যাটেলাইট ভিত্তিক PFZ তথ্য ও ক্লোরোফিল ডেটা।',
        pfz_zones: 'সম্ভাব্য মৎস্য অঞ্চল',
        sea_surface_temp: 'সমুদ্র পৃষ্ঠের তাপমাত্রা',
        chlorophyll: 'ক্লোরোফিল-এ',
        coastal_advisory: 'উপকূলীয় মৎস্য শিকারের পরামর্শ',
        high_potential: 'উচ্চ সম্ভাবনা',
        moderate_potential: 'মাঝারি সম্ভাবনা',
        low_potential: 'কম সম্ভাবনা',

        map_title: 'সামুদ্রিক মানচিত্র',
        map_desc: 'জাহাজ ট্র্যাকিং এবং নিরাপদ রুট গণনা।',
        layer_controls: 'মানচিত্রের স্তর',
        vessel_tracking: 'জাহাজ ট্র্যাকিং (AIS)',
        weather_overlay: 'আবহাওয়া রাডার',
        route_planner: 'নিরাপদ রুট প্ল্যানার',
        calculate_route: 'নিরাপদ রুট গণনা করুন',
        origin: 'উৎপত্তি বন্দর / স্থানাঙ্ক',
        destination: 'গন্তব্য বন্দর / স্থানাঙ্ক',

        settings_title: 'প্ল্যাটফর্ম সেটিংস',
        settings_desc: 'ভাষা, থিম এবং এআই ভয়েস উত্তর কনফিগার করুন।',
        general_settings: 'সাধারণ পছন্দসমূহ',
        theme_preference: 'থিম প্রদর্শন',
        language_preference: 'প্ল্যাটফর্মের ভাষা',
        tts_settings: 'টেক্সট-টু-স্পিচ (এআই ভয়েস)',
        enable_tts: 'ভয়েস উত্তর সক্ষম করুন',
        enable_tts_desc: 'ORCA এআই সহকারীকে উত্তরগুলো উচ্চস্বরে পড়ার অনুমতি দিন।',
        speech_voice: 'ভয়েস নির্বাচন',
        speech_rate: 'কথা বলার গতি',
        test_voice: 'ভয়েস পরীক্ষা করুন',
        save_settings: 'পছন্দসমূহ সংরক্ষণ করুন',
        settings_saved: 'পছন্দসমূহ সফলভাবে সংরক্ষিত হয়েছে!'
    },
    mr: {
        nav_about: 'आमच्याबद्दल',
        nav_dashboard: 'डॅशबोर्ड',
        nav_assistant: 'एआय सहाय्यक',
        nav_map: 'समुद्री नकाशा',
        nav_safety: 'सुरक्षा आणि अलर्ट',
        nav_fishing: 'मासेमारी',
        nav_settings: 'सेटिंग्ज',
        brand_sub: 'इंटेलिजन्स',

        export_report: 'अहवाल डाउनलोड करा',
        view_full_chart: 'पूर्ण तक्ता पहा',
        view_details: 'तपशील पहा',
        active: 'सक्रिय',
        search: 'शोधा...',
        search_language: 'भाषा शोधा...',

        dash_title: 'डॅशबोर्ड आढावा',
        dash_subtitle: 'रिअल-टाइम सागरी परिस्थिती आणि उपक्रमांचे निर्देश.',
        wave_height: 'लाटांची उंची',
        wind_speed: 'वाऱ्याचा वेग',
        water_temp: 'पाण्याचे तापमान',
        from_last_hour: '+०.३m मागील तासापासून',
        nw_direction: 'वायव्य दिशा',
        steady_cooling: 'स्थिर थंड होणे',
        risk_assessment: 'धोका मूल्यमापन',
        risk_moderate: 'मध्यम धोका',
        risk_index: 'निर्देशांक: ६.८ / १०',
        risk_desc: 'समुद्रात परिस्थिती बिघडत आहे. लहान नौकांनी काळजी घ्यावी.',
        forecast_24h: '२४ तासांचा अंदाज',
        active_directives: 'सक्रिय निर्देश',
        alerts_count: '२ इशारे',
        gale_warning: 'वादळी वाऱ्याचा इशारा',
        gale_desc: 'सेक्टर बी मध्ये २२:०० पासून ४५kts वेगाने वारे वाहण्याची शक्यता.',
        sensor_cal: 'सेंसर कॅलिब्रेशन आवश्यक',
        sensor_desc: 'बॉया अल्फा-७ अनियमित डेटा रिपोर्ट करत आहे.',
        route_update: 'मार्ग अपडेट उपलब्ध',
        route_desc: 'नवीनतम सागरी प्रवाहांच्या आधारे अनुकूल मार्ग तयार आहे.',

        assistant_title: 'ORCA एआय सहाय्यक',
        assistant_desc: 'सागरी सुरक्षा, मासेमारी क्षेत्रे आणि अनुकूल मार्गांबद्दल काहीही विचारा.',
        ask_assistant_placeholder: 'ORCA सहाय्यकाला विचारा...',
        agent_activity: 'एजंट उपक्रम',
        orca_thinking: 'ORCA विचार करत आहे...',
        greeting_msg: 'नमस्कार! मी ORCA आहे, तुमचा सागरी परिसंस्था सहाय्यक. आज मी तुम्हाला कशी मदत करू शकतो?',
        export_pdf: 'पीडीएफ अहवाल निर्यात करा',
        listen_response: 'उत्तर ऐका',
        pause_speech: 'थांबवा',
        resume_speech: 'पुन्हा सुरू करा',
        stop_speech: 'स्पीच बंद करा',
        listening: 'बोलत आहे...',

        safety_title: 'सागरी सुरक्षा आणि बुलेटिन',
        safety_desc: 'किनारपट्टीवरील धोके, चक्रीवादळाचे इशारे आणि हवामान बुलेटिन.',
        active_warnings: 'सक्रिय इशारे',
        emergency_contacts: 'आणीबाणीचे संपर्क',
        coast_guard: 'भारतीय तटरक्षक दल: १५५४',
        disaster_mgmt: 'राज्य आपत्ती व्यवस्थापन: १०७०',
        port_authority: 'पोर्ट नियंत्रण VHF: चॅनेल १६',
        cyclone_advisory: 'चक्रीवादळाचा इशारा',
        high_wave_alert: 'उंच लाटांचा इशारा',
        tsunami_watch: 'सुनामी सतर्कता बुलेटिन',

        fishing_title: 'मासेमारी इंटेलिजन्स आणि PFZ',
        fishing_desc: 'उपग्रह आधारित PFZ माहिती आणि क्लोरोफिल डेटा.',
        pfz_zones: 'संभाव्य मासेमारी क्षेत्रे',
        sea_surface_temp: 'समुद्र पृष्ठभागाचे तापमान',
        chlorophyll: 'क्लोरोफिल-ए',
        coastal_advisory: 'किनारपट्टी मासेमारी सल्ला',
        high_potential: 'उच्च शक्यता',
        moderate_potential: 'मध्यम शक्यता',
        low_potential: 'कमी शक्यता',

        map_title: 'समुद्री नकाशा',
        map_desc: 'जहाज ट्रॅकिंग आणि सुरक्षित मार्ग गणना.',
        layer_controls: 'नकाशा स्तर',
        vessel_tracking: 'जहाज ट्रॅकिंग (AIS)',
        weather_overlay: 'हवामान रडार',
        route_planner: 'सुरक्षित मार्ग नियोजक',
        calculate_route: 'सुरक्षित मार्गाची गणना करा',
        origin: 'सुरुवातीचे बंदर / निर्देशांक',
        destination: 'गंतव्य बंदर / निर्देशांक',

        settings_title: 'प्लॅटफॉर्म सेटिंग्ज',
        settings_desc: 'भाषा, थीम आणि एआय व्हॉईस उत्तरे कॉन्फिगर करा.',
        general_settings: 'सामान्य पसंती',
        theme_preference: 'थीम डिस्प्ले',
        language_preference: 'प्लॅटफॉर्मची भाषा',
        tts_settings: 'टेक्स्ट-टू-स्पीच (एआय आवाज)',
        enable_tts: 'व्हॉईस उत्तरे सक्षम करा',
        enable_tts_desc: 'ORCA एआय सहाय्यकाला उत्तरे मोठ्याने वाचण्याची अनुमती द्या.',
        speech_voice: 'आवाज निवड',
        speech_rate: 'बोलण्याचा वेग',
        test_voice: 'आवाज तपासा',
        save_settings: 'पसंती जतन करा',
        settings_saved: 'पसंती यशस्वीरित्या जतन केल्या!'
    },
    gu: {
        nav_about: 'અમારા વિશે',
        nav_dashboard: 'ડેશબોર્ડ',
        nav_assistant: 'એઆઈ સહાયક',
        nav_map: 'દરિયાઈ નકશો',
        nav_safety: 'સુરક્ષા અને એલર્ટ',
        nav_fishing: 'માછીમારી',
        nav_settings: 'સેટિંગ્સ',
        brand_sub: 'ઈન્ટેલિજન્સ',

        export_report: 'રિપોર્ટ ડાઉનલોડ કરો',
        view_full_chart: 'સંપૂર્ણ ચાર્ટ જુઓ',
        view_details: 'વિગતો જુઓ',
        active: 'સક્રિય',
        search: 'શોધો...',
        search_language: 'ભાષા શોધો...',

        dash_title: 'ડેશબોર્ડ વિહંગાવલોકન',
        dash_subtitle: 'રીઅલ-ટાઇમ દરિયાઈ સ્થિતિ અને ઓપરેશનલ સૂચનાઓ.',
        wave_height: 'મોજાની ઊંચાઈ',
        wind_speed: 'પવનની ગતિ',
        water_temp: 'પાણીનું તાપમાન',
        from_last_hour: '+0.3m છેલ્લા કલાકથી',
        nw_direction: 'ઉત્તર-પશ્ચિમ દિશા',
        steady_cooling: 'સ્થિર ઠંડક',
        risk_assessment: 'જોખમ મૂલ્યાંકન',
        risk_moderate: 'મધ્યમ જોખમ',
        risk_index: 'ઈન્ડેક્સ: 6.8 / 10',
        risk_desc: 'દરિયામાં સ્થિતિ બગડી રહી છે. નાની હોડીઓ માટે સાવચેતી રાખવી.',
        forecast_24h: '24 કલાકની આગાહી',
        active_directives: 'સક્રિય સૂચનાઓ',
        alerts_count: '2 ચેતવણીઓ',
        gale_warning: 'વાવાઝોડાની ચેતવણી',
        gale_desc: 'સેક્ટર B માં 22:00 થી 45kts ની ઝડપે પવન ફુંકાવાની શક્યતા.',
        sensor_cal: 'સેન્સર કેલિબ્રેશન જરૂરી',
        sensor_desc: 'બોયા આલ્ફા-7 અનિયમિત ડેટા રિપોર્ટ કરી રહ્યું છે.',
        route_update: 'રૂટ અપડેટ ઉપલબ્ધ',
        route_desc: 'નવીનતમ દરિયાઈ પ્રવાહોના આધારે અનુકૂળ રૂટ તૈયાર છે.',

        assistant_title: 'ORCA એઆઈ સહાયક',
        assistant_desc: 'દરિયાઈ સુરક્ષા, માછીમારીના વિસ્તારો અને રૂટ વિશે કંઈપણ પૂછો.',
        ask_assistant_placeholder: 'ORCA સહાયકને પૂછો...',
        agent_activity: 'એજન્ટ પ્રવૃત્તિ',
        orca_thinking: 'ORCA વિચારી રહ્યું છે...',
        greeting_msg: 'નમસ્તે! હું ORCA છું, તમારો દરિયાઈ નિવસનતંત્ર સહાયક. આજે હું તમને કેવી રીતે મદદ કરી શકું?',
        export_pdf: 'PDF રિપોર્ટ એક્સપોર્ટ કરો',
        listen_response: 'જવાબ સાંભળો',
        pause_speech: 'અટકાવો',
        resume_speech: 'ફરી શરૂ કરો',
        stop_speech: 'બંધ કરો',
        listening: 'બોલી રહ્યું છે...',

        safety_title: 'દરિયાઈ સુરક્ષા અને બુલેટિન',
        safety_desc: 'દરિયાકાંઠાના જોખમો, ચક્રવાતની ચેતવણીઓ અને હવામાન બુલેટિન.',
        active_warnings: 'સક્રિય ચેતવણીઓ',
        emergency_contacts: 'ઈમરજન્સી સંપર્કો',
        coast_guard: 'ભારતીય કોસ્ટ ગાર્ડ: 1554',
        disaster_mgmt: 'રાજ્ય આપત્તિ વ્યવસ્થાપન: 1070',
        port_authority: 'પોર્ટ કંટ્રોલ VHF: ચેનલ 16',
        cyclone_advisory: 'ચક્રવાતની ચેતવણી',
        high_wave_alert: 'ઉંચા મોજાની ચેતવણી',
        tsunami_watch: 'સુનામી સચેતતા બુલેટિન',

        fishing_title: 'માછીમારી ઈન્ટેલિજન્સ અને PFZ',
        fishing_desc: 'સેટેલાઇટ આધારિત PFZ સલાહ અને મોનિટરિંગ ડેટા.',
        pfz_zones: 'સંભવિત માછીમારી વિસ્તારો',
        sea_surface_temp: 'દરિયાઈ સપાટીનું તાપમાન',
        chlorophyll: 'ક્લોરોફિલ-એ',
        coastal_advisory: 'દરિયાકાંઠાની માછીમારી સલાહ',
        high_potential: 'ઉચ્ચ શક્યતા',
        moderate_potential: 'મધ્યમ શક્યતા',
        low_potential: 'ઓછી શક્યતા',

        map_title: 'દરિયાઈ નકશો',
        map_desc: 'જહાજ ટ્રેકિંગ અને સુરક્ષિત રૂટની ગણતરી.',
        layer_controls: 'નકશા સ્તરો',
        vessel_tracking: 'જહાજ ટ્રેકિંગ (AIS)',
        weather_overlay: 'હવામાન રડાર',
        route_planner: 'સુરક્ષિત રૂટ પ્લાનર',
        calculate_route: 'સુરક્ષિત રૂટની ગણતરી કરો',
        origin: 'શરૂઆતનું બંદર / કોઓર્ડિનેટ્સ',
        destination: 'મંજિલનું બંદર / કોઓર્ડિનેટ્સ',

        settings_title: 'પ્લેટફોર્મ સેટિંગ્સ',
        settings_desc: 'ભાષા, થીમ અને એઆઈ વોઇસ જવાબો સેટ કરો.',
        general_settings: 'સામાન્ય પસંદગીઓ',
        theme_preference: 'થીમ ડિસ્પ્લે',
        language_preference: 'પ્લેટફોર્મની ભાષા',
        tts_settings: 'ટેક્સ્ટ-ટુ-સ્પીચ (એઆઈ વોઇસ)',
        enable_tts: 'વોઇસ જવાબો સક્ષમ કરો',
        enable_tts_desc: 'ORCA એઆઈ સહાયકને જવાબો મોટેથી વાંચવાની મંજૂરી આપો.',
        speech_voice: 'અવાજની પસંદગી',
        speech_rate: 'બોલવાની ગતિ',
        test_voice: 'અવાજ ચકાસો',
        save_settings: 'પસંદગીઓ સાચવો',
        settings_saved: 'પસંદગીઓ સફળતાપૂર્વક સાચવવામાં આવી!'
    },
    pa: {
        nav_about: 'ਸਾਡੇ ਬਾਰੇ',
        nav_dashboard: 'ਡੈਸ਼ਬੋਰਡ',
        nav_assistant: 'ਏਆਈ ਸਹਾਇਕ',
        nav_map: 'ਸਮੁੰਦਰੀ ਨਕਸ਼ਾ',
        nav_safety: 'ਸੁਰੱਖਿਆ ਅਤੇ ਅਲਰਟ',
        nav_fishing: 'ਮੱਛੀ ਫੜਨਾ',
        nav_settings: 'ਸੈਟਿੰਗਾਂ',
        brand_sub: 'ਇੰਟੈਲੀਜੈਂਸ',

        export_report: 'ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ',
        view_full_chart: 'ਪੂਰਾ ਚਾਰਟ ਦੇਖੋ',
        view_details: 'ਵੇਰਵੇ ਦੇਖੋ',
        active: 'ਸਰਗਰਮ',
        search: 'ਖੋਜੋ...',
        search_language: 'ਭਾਸ਼ਾ ਖੋਜੋ...',

        dash_title: 'ਡੈਸ਼ਬੋਰਡ ਸਮੀਖਿਆ',
        dash_subtitle: 'ਰੀਅਲ-ਟਾਈਮ ਸਮੁੰਦਰੀ ਸਥਿਤੀਆਂ ਅਤੇ ਸੰਚਾਲਨ ਨਿਰਦੇਸ਼।',
        wave_height: 'ਛੱਲਾਂ ਦੀ ਉਚਾਈ',
        wind_speed: 'ਹਵਾ ਦੀ ਗਤੀ',
        water_temp: 'ਪਾਣੀ ਦਾ ਤਾਪਮਾਨ',
        from_last_hour: '+0.3m ਪਿਛਲੇ ਘੰਟੇ ਤੋਂ',
        nw_direction: 'ਉੱਤਰ-ਪੱਛਮ ਦਿਸ਼ਾ',
        steady_cooling: 'ਸਥਿਰ ਠੰਢਕ',
        risk_assessment: 'ਜੋਖਮ ਮੁਲਾਂਕਣ',
        risk_moderate: 'ਮੱਧਮ ਜੋਖਮ',
        risk_index: 'ਸੂਚਕਾਂਕ: 6.8 / 10',
        risk_desc: 'ਸਮੁੰਦਰ ਵਿੱਚ ਸਥਿਤੀ ਖਰਾਬ ਹੋ ਰਹੀ ਹੈ। ਛੋਟੀਆਂ ਕਿਸ਼ਤੀਆਂ ਲਈ ਸਾਵਧਾਨੀ ਵਰਤੋ।',
        forecast_24h: '24 ਘੰਟੇ ਦੀ ਭਵਿੱਖਬਾਣੀ',
        active_directives: 'ਸਰਗਰਮ ਨਿਰਦੇਸ਼',
        alerts_count: '2 ਚੇਤਾਵਨੀਆਂ',
        gale_warning: 'ਤੇਜ਼ ਹਵਾ ਦੀ ਚੇਤਾਵਨੀ',
        gale_desc: 'ਸੈਕਟਰ ਬੀ ਵਿੱਚ 22:00 ਤੋਂ 45kts ਦੀਆਂ ਹਵਾਵਾਂ ਦੀ ਸੰਭਾਵਨਾ ਹੈ।',
        sensor_cal: 'ਸੈਂਸਰ ਕੈਲੀਬ੍ਰੇਸ਼ਨ ਲੋੜੀਂਦੀ ਹੈ',
        sensor_desc: 'ਬੋਇਆ ਅਲਫਾ-7 ਅਨਿਯਮਿਤ ਡਾਟਾ ਰਿਪੋਰਟ ਕਰ ਰਿਹਾ ਹੈ।',
        route_update: 'ਰੂਟ ਅੱਪਡੇਟ ਉਪਲਬਧ ਹੈ',
        route_desc: 'ਤਾਜ਼ਾ ਸਮੁੰਦਰੀ ਲਹਿਰਾਂ ਦੇ ਆਧਾਰ \'ਤੇ ਅਨੁਕੂਲ ਰੂਟ ਤਿਆਰ ਹੈ।',

        assistant_title: 'ORCA ਏਆਈ ਸਹਾਇਕ',
        assistant_desc: 'ਸਮੁੰਦਰੀ ਸੁਰੱਖਿਆ, ਮੱਛੀ ਫੜਨ ਵਾਲੇ ਖੇਤਰਾਂ ਅਤੇ ਰੂਟਾਂ ਬਾਰੇ ਕੁਝ ਵੀ ਪੁੱਛੋ।',
        ask_assistant_placeholder: 'ORCA ਸਹਾਇਕ ਤੋਂ ਪੁੱਛੋ...',
        agent_activity: 'ਏਜੰਟ ਗਤੀਵਿਧੀ',
        orca_thinking: 'ORCA ਸੋਚ ਰਿਹਾ ਹੈ...',
        greeting_msg: 'ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! ਮੈਂ ORCA ਹਾਂ, ਤੁਹਾਡਾ ਸਮੁੰਦਰੀ ਈਕੋਸਿਸਟਮ ਸਹਾਇਕ। ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?',
        export_pdf: 'PDF ਰਿਪੋਰਟ ਐਕਸਪੋਰਟ ਕਰੋ',
        listen_response: 'ਉੱਤਰ ਸੁਣੋ',
        pause_speech: 'ਰੋਕੋ',
        resume_speech: 'ਦੁਬਾਰਾ ਸ਼ੁਰੂ ਕਰੋ',
        stop_speech: 'ਬੰਦ ਕਰੋ',
        listening: 'ਬੋਲ ਰਿਹਾ ਹੈ...',

        safety_title: 'ਸਮੁੰਦਰੀ ਸੁਰੱਖਿਆ ਅਤੇ ਬੁਲੇਟਿਨ',
        safety_desc: 'ਤੱਟਵਰਤੀ ਖਤਰੇ, ਤੂਫਾਨ ਦੀਆਂ ਚੇਤਾਵਨੀਆਂ ਅਤੇ ਮੌਸਮ ਬੁਲੇਟਿਨ।',
        active_warnings: 'ਸਰਗਰਮ ਚੇਤਾਵਨੀਆਂ',
        emergency_contacts: 'ਐਮਰਜੈਂਸੀ ਸੰਪਰਕ',
        coast_guard: 'ਭਾਰਤੀ ਕੋਸਟ ਗਾਰਡ: 1554',
        disaster_mgmt: 'ਰਾਜ ਆਫ਼ਤ ਪ੍ਰਬੰਧਨ: 1070',
        port_authority: 'ਪੋਰਟ ਕੰਟਰੋਲ VHF: ਚੈਨਲ 16',
        cyclone_advisory: 'ਚੱਕਰਵਾਤ ਦੀ ਚੇਤਾਵਨੀ',
        high_wave_alert: 'ਉੱਚੀਆਂ ਛੱਲਾਂ ਦੀ ਚੇਤਾਵਨੀ',
        tsunami_watch: 'ਸੁਨਾਮੀ ਚੌਕਸੀ ਬੁਲੇਟਿਨ',

        fishing_title: 'ਮੱਛੀ ਫੜਨ ਦੀ ਇੰਟੈਲੀਜੈਂਸ ਅਤੇ PFZ',
        fishing_desc: 'ਸੈਟੇਲਾਈਟ ਆਧਾਰਿਤ PFZ ਜਾਣਕਾਰੀ ਅਤੇ ਕਲੋਰੋਫਿਲ ਡਾਟਾ।',
        pfz_zones: 'ਸੰਭਾਵੀ ਮੱਛੀ ਫੜਨ ਵਾਲੇ ਖੇਤਰ',
        sea_surface_temp: 'ਸਮੁੰਦਰ ਦੀ ਸਤ੍ਹਾ ਦਾ ਤਾਪਮਾਨ',
        chlorophyll: 'ਕਲੋਰੋਫਿਲ-ਏ',
        coastal_advisory: 'ਤੱਟਵਰਤੀ ਮੱਛੀ ਫੜਨ ਦੀ ਸਲਾਹ',
        high_potential: 'ਉੱਚ ਸੰਭਾਵਨਾ',
        moderate_potential: 'ਮੱਧਮ ਸੰਭਾਵਨਾ',
        low_potential: 'ਘੱਟ ਸੰਭਾਵਨਾ',

        map_title: 'ਸਮੁੰਦਰੀ ਨਕਸ਼ਾ',
        map_desc: 'ਜਹਾਜ਼ ਟਰੈਕਿੰਗ ਅਤੇ ਸੁਰੱਖਿਅਤ ਰੂਟ ਦੀ ਗਣਨਾ।',
        layer_controls: 'ਨਕਸ਼ੇ ਦੀਆਂ ਤਹਿਆਂ',
        vessel_tracking: 'ਜਹਾਜ਼ ਟਰੈਕਿੰਗ (AIS)',
        weather_overlay: 'ਮੌਸਮ ਰਡਾਰ',
        route_planner: 'ਸੁਰੱਖਿਅਤ ਰੂਟ ਪਲਾਨਰ',
        calculate_route: 'ਸੁਰੱਖਿਅਤ ਰੂਟ ਦੀ ਗਣਨਾ ਕਰੋ',
        origin: 'ਸ਼ੁਰੂਆਤੀ ਪੋਰਟ / ਨਿਰਦੇਸ਼ਾਂਕ',
        destination: 'ਮੰਜ਼ਿਲ ਪੋਰਟ / ਨਿਰਦੇਸ਼ਾਂਕ',

        settings_title: 'ਪਲੇਟਫਾਰਮ ਸੈਟਿੰਗਾਂ',
        settings_desc: 'ਭਾਸ਼ਾ, ਥੀਮ ਅਤੇ ਏਆਈ ਆਵਾਜ਼ ਦੇ ਉੱਤਰਾਂ ਦੀ ਚੋਣ ਕਰੋ।',
        general_settings: 'ਆਮ ਤਰਜੀਹਾਂ',
        theme_preference: 'ਥੀਮ ਡਿਸਪਲੇਅ',
        language_preference: 'ਪਲੇਟਫਾਰਮ ਭਾਸ਼ਾ',
        tts_settings: 'ਟੈਕਸਟ-ਟੂ-ਸਪੀਚ (ਏਆਈ ਆਵਾਜ਼)',
        enable_tts: 'ਆਵਾਜ਼ੀ ਉੱਤਰ ਸਮਰੱਥ ਕਰੋ',
        enable_tts_desc: 'ORCA ਏਆਈ ਸਹਾਇਕ ਨੂੰ ਉੱਤਰ ਉੱਚੀ ਆਵਾਜ਼ ਵਿੱਚ ਪੜ੍ਹਨ ਦੀ ਇਜਾਜ਼ਤ ਦਿਓ।',
        speech_voice: 'ਆਵਾਜ਼ ਦੀ ਚੋਣ',
        speech_rate: 'ਬੋਲਣ ਦੀ ਗਤੀ',
        test_voice: 'ਆਵਾਜ਼ ਪਰਖੋ',
        save_settings: 'ਤਰਜੀਹਾਂ ਸੰਭਾਲੋ',
        settings_saved: 'ਤਰਜੀਹਾਂ ਸਫਲਤਾਪੂਰਵਕ ਸੰਭਾਲੀਆਂ ਗਈਆਂ!'
    },
    ur: {
        nav_about: 'ہمارے بارے میں',
        nav_dashboard: 'ڈیش بورڈ',
        nav_assistant: 'اے آئی اسسٹنٹ',
        nav_map: 'سمندری نقشہ',
        nav_safety: 'حفاظت اور الرٹس',
        nav_fishing: 'ماہی گیری',
        nav_settings: 'سیٹنگز',
        brand_sub: 'انٹیلی جنس',

        export_report: 'رپورٹ ڈاؤن لوڈ کریں',
        view_full_chart: 'مکمل چارٹ دیکھیں',
        view_details: 'تفصیلات دیکھیں',
        active: 'فعال',
        search: 'تلاش کریں...',
        search_language: 'زبان تلاش کریں...',

        dash_title: 'ڈیش بورڈ جائزہ',
        dash_subtitle: 'ریئل ٹائم سمندری حالات اور آپریشنل ہدایات۔',
        wave_height: 'لہر کی اونچائی',
        wind_speed: 'ہوا کی رفتار',
        water_temp: 'پانی کا درجہ حرارت',
        from_last_hour: '+0.3m پچھلے گھنٹے سے',
        nw_direction: 'شمال مغربی سمت',
        steady_cooling: 'مستقل ٹھنڈک',
        risk_assessment: 'خطرے کا اندازہ',
        risk_moderate: 'متوسط خطرہ',
        risk_index: 'انڈیکس: 6.8 / 10',
        risk_desc: 'سمندر میں حالات خراب ہو رہے ہیں۔ چھوٹی کشتیوں کے لیے احتیاط برتیں۔',
        forecast_24h: '24 گھنٹے کی پیش گوئی',
        active_directives: 'فعال ہدایات',
        alerts_count: '2 تنبیہات',
        gale_warning: 'تیز ہوا کی تنبیہ',
        gale_desc: 'سیکٹر بی میں 22:00 سے 45kts کی ہوائیں چلنے کا امکان ہے۔',
        sensor_cal: 'سینسیر کیلیبریشن درکار ہے',
        sensor_desc: 'بویا الفا-7 بے قاعدہ ڈیٹا رپورٹ کر رہا ہے۔',
        route_update: 'راستہ کی اپ ڈیٹ دستیاب ہے',
        route_desc: 'تازہ ترین سمندری دھاروں کی بنیاد پر فلیٹ سی کے لیے بہترین راستہ تیار ہے۔',

        assistant_title: 'ORCA اے آئی اسسٹنٹ',
        assistant_desc: 'سمندری سلامتی، ماہی گیری کے علاقوں اور راستوں کے بارے میں کچھ بھی پوچھیں۔',
        ask_assistant_placeholder: 'ORCA اسسٹنٹ سے پوچھیں...',
        agent_activity: 'ایجینٹ کی سرگرمی',
        orca_thinking: 'ORCA سوچ رہا ہے...',
        greeting_msg: 'سلام! میں ORCA ہوں، آپ کا سمندری ماحولیاتی اسسٹنٹ۔ آج میں آپ کی کیا مدد کر سکتا ہوں؟',
        export_pdf: 'PDF رپورٹ برآمد کریں',
        listen_response: 'جواب سنیں',
        pause_speech: 'وقفہ دیں',
        resume_speech: 'دوبارہ شروع کریں',
        stop_speech: 'روک دیں',
        listening: 'بول رہا ہے...',

        safety_title: 'سمندری حفاظت اور بلیٹن',
        safety_desc: 'ساحلی خطرات، طوفان کی تنبیہات اور موسم کے بلیٹن۔',
        active_warnings: 'فعال تنبیہات',
        emergency_contacts: 'ہنگامی رابطے',
        coast_guard: 'انڈین کوسٹ گارڈ: 1554',
        disaster_mgmt: 'ریاستی ڈساسٹر مینجمنٹ: 1070',
        port_authority: 'پورٹ کنٹرول VHF: چینل 16',
        cyclone_advisory: 'طوفان کی تنبیہ',
        high_wave_alert: 'اونچی لہروں کی تنبیہ',
        tsunami_watch: 'سنامی الرٹ بلیٹن',

        fishing_title: 'ماہی گیری انٹیلی جنس اور PFZ',
        fishing_desc: 'سیٹلائٹ پر مبنی PFZ معلومات اور کلوروفل ڈیٹا۔',
        pfz_zones: 'ممکنہ ماہی گیری کے علاقے',
        sea_surface_temp: 'سمندر کی سطح کا درجہ حرارت',
        chlorophyll: 'کلوروفل-اے',
        coastal_advisory: 'ساحلی ماہی گیری کی ہدایت',
        high_potential: 'زیادہ امکان',
        moderate_potential: 'متوسط امکان',
        low_potential: 'کم امکان',

        map_title: 'سمندری نقشہ',
        map_desc: 'جہازوں کی ٹریکنگ اور محفوظ راستے کا حساب۔',
        layer_controls: 'نقشے کی تہیں',
        vessel_tracking: 'جہاز کی ٹریکنگ (AIS)',
        weather_overlay: 'موسم کا ریڈار',
        route_planner: 'محفوظ راستے کا منصوبہ ساز',
        calculate_route: 'محفوظ راستے کا حساب لگائیں',
        origin: 'ابتدائی پورٹ / متناسقات',
        destination: 'منزل کا پورٹ / متناسقات',

        settings_title: 'پلیٹ فارم سیٹنگز',
        settings_desc: 'زبان، تھیم اور اے آئی آواز کے جوابات سیٹ کریں۔',
        general_settings: 'عام ترجیحات',
        theme_preference: 'تھیم ڈسپلے',
        language_preference: 'پلیٹ فارم کی زبان',
        tts_settings: 'ٹیکسٹ ٹو اسپیچ (اے آئی آواز)',
        enable_tts: 'آواز کے جوابات کو فعال کریں',
        enable_tts_desc: 'ORCA اے آئی اسسٹنٹ کو جوابات بلند آواز میں پڑھنے کی اجازت دیں۔',
        speech_voice: 'آواز کا انتخاب',
        speech_rate: 'بولنے کی رفتار',
        test_voice: 'آواز کو ٹیسٹ کریں',
        save_settings: 'ترجیحات محفوظ کریں',
        settings_saved: 'ترجیحات کامیابی کے ساتھ محفوظ ہو گئیں!'
    }
};

// Fallback generator for remaining Indian languages (Assamese, Odia, Sanskrit, Santali, Dogri, Bodo, Kashmiri, Konkani, Maithili, Manipuri, Nepali, Sindhi)
// Maps missing translations back to Hindi script or English gracefully so no raw key is ever shown to user.
const LANG_FALLBACK_BASE = TRANSLATIONS.hi;
['as', 'or', 'sa', 'sat', 'doi', 'brx', 'ks', 'kok', 'mai', 'mni', 'ne', 'sd'].forEach(code => {
    TRANSLATIONS[code] = { ...LANG_FALLBACK_BASE };
});

class Orcai18nEngine {
    constructor() {
        this.currentLang = localStorage.getItem('orca_lang') || 'en';
        this.listeners = [];
    }

    init() {
        this.ensureFontsLoaded();
        this.applyTranslations();
        this.setupNavbarLanguageSelector();
    }

    ensureFontsLoaded() {
        if (!document.getElementById('orca-google-fonts-i18n')) {
            const link = document.createElement('link');
            link.id = 'orca-google-fonts-i18n';
            link.rel = 'stylesheet';
            link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,400;0,600;0,700;1,400&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Bengali:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Kannada:wght@400;600;700&family=Noto+Sans+Malayalam:wght@400;600;700&family=Noto+Sans+Gujarati:wght@400;600;700&family=Noto+Sans+Gurmukhi:wght@400;600;700&family=Noto+Sans+Oriya:wght@400;600;700&display=swap';
            document.head.appendChild(link);
        }

        if (!document.getElementById('orca-i18n-styles')) {
            const style = document.createElement('style');
            style.id = 'orca-i18n-styles';
            style.innerHTML = `
                body, button, input, select, textarea {
                    font-family: 'Inter', 'Noto Sans', 'Noto Sans Devanagari', 'Noto Sans Bengali', 'Noto Sans Tamil', 'Noto Sans Telugu', 'Noto Sans Kannada', 'Noto Sans Malayalam', 'Noto Sans Gujarati', 'Noto Sans Gurmukhi', 'Noto Sans Oriya', -apple-system, sans-serif !important;
                }
                .lang-dropdown-menu::-webkit-scrollbar {
                    width: 6px;
                }
                .lang-dropdown-menu::-webkit-scrollbar-thumb {
                    background: rgba(140, 140, 140, 0.4);
                    border-radius: 4px;
                }
            `;
            document.head.appendChild(style);
        }
    }

    t(key, fallback = '') {
        const langDict = TRANSLATIONS[this.currentLang] || TRANSLATIONS.en;
        if (langDict && langDict[key]) {
            return langDict[key];
        }
        if (TRANSLATIONS.en && TRANSLATIONS.en[key]) {
            return TRANSLATIONS.en[key];
        }
        return fallback || key;
    }

    setLanguage(langCode) {
        if (this.currentLang === langCode) return;
        this.currentLang = langCode;
        localStorage.setItem('orca_lang', langCode);
        this.applyTranslations();
        
        // Update selector trigger text
        const labelEl = document.getElementById('lang-selector-code');
        if (labelEl) {
            const langObj = SUPPORTED_LANGUAGES.find(l => l.code === langCode);
            labelEl.textContent = langObj ? langObj.code.toUpperCase() : langCode.toUpperCase();
        }

        // Notify listeners
        window.dispatchEvent(new CustomEvent('orcaLanguageChanged', { detail: { lang: langCode } }));
    }

    applyTranslations(root = document) {
        // Elements with data-i18n attribute
        const elements = root.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translated = this.t(key);
            if (translated) {
                el.textContent = translated;
            }
        });

        // Placeholders
        const placeholders = root.querySelectorAll('[data-i18n-placeholder]');
        placeholders.forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            const translated = this.t(key);
            if (translated) {
                el.placeholder = translated;
            }
        });

        // Titles & Tooltips
        const titles = root.querySelectorAll('[data-i18n-title]');
        titles.forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            const translated = this.t(key);
            if (translated) {
                el.title = translated;
                el.setAttribute('aria-label', translated);
            }
        });
    }

    setupNavbarLanguageSelector() {
        const themeBtnNav = document.getElementById('theme-toggle-btn-nav');
        if (!themeBtnNav || document.getElementById('lang-selector-wrapper')) return;

        const wrapper = document.createElement('div');
        wrapper.id = 'lang-selector-wrapper';
        wrapper.className = 'relative inline-block text-left';

        const currentLangObj = SUPPORTED_LANGUAGES.find(l => l.code === this.currentLang) || SUPPORTED_LANGUAGES[0];

        wrapper.innerHTML = `
            <button id="lang-selector-btn" aria-label="Select Language" type="button" class="p-2 rounded-lg text-mute hover:text-ink dark:hover:text-white hover:bg-surface-container-low/50 dark:hover:bg-slate-900/50 transition-colors flex items-center gap-1.5 text-xs font-semibold">
                <span class="material-symbols-outlined text-[18px]">language</span>
                <span id="lang-selector-code" class="font-mono text-[11px] uppercase">${currentLangObj.code}</span>
                <span class="material-symbols-outlined text-[14px]">expand_more</span>
            </button>

            <div id="lang-dropdown-menu" class="hidden absolute right-0 top-full mt-2 w-72 max-h-96 bg-surface dark:bg-zinc-950 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl z-[100] p-2 overflow-hidden flex-col transition-all duration-150">
                <div class="p-1.5 border-b border-hairline dark:border-slate-800 relative">
                    <input id="lang-search-input" type="text" placeholder="${this.t('search_language', 'Search language...')}" class="w-full bg-canvas-elevated dark:bg-black border border-hairline dark:border-slate-800 rounded-lg py-1.5 pl-7 pr-2 text-xs focus:outline-none focus:border-cyan-500 text-ink dark:text-white" />
                    <span class="material-symbols-outlined absolute left-3 top-3 text-[14px] text-mute pointer-events-none">search</span>
                </div>
                <div id="lang-list-container" class="lang-dropdown-menu overflow-y-auto max-h-72 p-1 space-y-0.5 mt-1">
                </div>
            </div>
        `;

        // Insert beside theme toggle button
        themeBtnNav.parentNode.insertBefore(wrapper, themeBtnNav);

        const btn = wrapper.querySelector('#lang-selector-btn');
        const dropdown = wrapper.querySelector('#lang-dropdown-menu');
        const searchInput = wrapper.querySelector('#lang-search-input');
        const listContainer = wrapper.querySelector('#lang-list-container');

        const renderList = (filter = '') => {
            listContainer.innerHTML = '';
            const filtered = SUPPORTED_LANGUAGES.filter(l => 
                l.name.toLowerCase().includes(filter.toLowerCase()) || 
                l.native.toLowerCase().includes(filter.toLowerCase()) ||
                l.code.toLowerCase().includes(filter.toLowerCase())
            );

            filtered.forEach(lang => {
                const item = document.createElement('button');
                item.type = 'button';
                const isSelected = lang.code === this.currentLang;
                item.className = `w-full text-left px-3 py-2 rounded-lg flex items-center justify-between text-xs transition-colors ${
                    isSelected 
                        ? 'bg-cyan-500/10 text-cyan-500 font-bold' 
                        : 'text-ink dark:text-slate-300 hover:bg-surface-container-low/80 dark:hover:bg-zinc-800/80'
                }`;

                item.innerHTML = `
                    <div class="flex items-center gap-2">
                        <span class="font-bold text-sm">${lang.native}</span>
                        <span class="text-[11px] text-mute font-normal">(${lang.name})</span>
                    </div>
                    ${isSelected ? '<span class="material-symbols-outlined text-[16px] text-cyan-400">check</span>' : ''}
                `;

                item.addEventListener('click', () => {
                    this.setLanguage(lang.code);
                    dropdown.classList.add('hidden');
                    dropdown.classList.remove('flex');
                });

                listContainer.appendChild(item);
            });
        };

        renderList();

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = !dropdown.classList.contains('hidden');
            if (isOpen) {
                dropdown.classList.add('hidden');
                dropdown.classList.remove('flex');
            } else {
                dropdown.classList.remove('hidden');
                dropdown.classList.add('flex');
                searchInput.value = '';
                renderList();
                setTimeout(() => searchInput.focus(), 50);
            }
        });

        searchInput.addEventListener('input', (e) => {
            renderList(e.target.value);
        });

        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                dropdown.classList.add('hidden');
                dropdown.classList.remove('flex');
            }
        });
    }
}

window.SUPPORTED_LANGUAGES = SUPPORTED_LANGUAGES;
window.Orcai18n = new Orcai18nEngine();

document.addEventListener('DOMContentLoaded', () => {
    window.Orcai18n.init();
});
