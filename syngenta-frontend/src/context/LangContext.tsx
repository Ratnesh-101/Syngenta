import { createContext, useContext, useState } from 'react'

type Lang = 'en' | 'hi'

interface LangContextValue {
  lang: Lang
  toggle: () => void
  t: (key: string) => string
}

const LangContext = createContext<LangContextValue>({
  lang: 'en',
  toggle: () => {},
  t: (k) => k,
})

export function LangProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => {
    return (localStorage.getItem('lang') as Lang) ?? 'en'
  })

  const toggle = () => {
    const next = lang === 'en' ? 'hi' : 'en'
    localStorage.setItem('lang', next)
    setLang(next)
  }

  const t = (key: string): string => {
    const dict = lang === 'hi' ? hi : en
    return dict[key] ?? key
  }

  return (
    <LangContext.Provider value={{ lang, toggle, t }}>
      {children}
    </LangContext.Provider>
  )
}

export function useLang() {
  return useContext(LangContext)
}

// ─── English strings ──────────────────────────────────────────────────────────
const en: Record<string, string> = {
  // Auth
  'auth.title':           'Field Force Intelligence',
  'auth.subtitle':        'Syngenta — Bikaner Territory',
  'auth.tab.password':    'Email / Password',
  'auth.tab.otp':         'Phone OTP',
  'auth.email':           'Email or Phone',
  'auth.password':        'Password',
  'auth.signin':          'Sign in',
  'auth.signing_in':      'Signing in...',
  'auth.phone':           'Phone Number',
  'auth.send_otp':        'Send OTP',
  'auth.sending_otp':     'Sending OTP...',
  'auth.enter_otp':       'Enter OTP',
  'auth.verify_otp':      'Verify OTP',
  'auth.verifying':       'Verifying...',
  'auth.register':        'Register with password',
  'auth.new_account':     'New account?',
  'auth.demo':            'Demo credentials',

  // Register
  'register.title':       'Create Account',
  'register.name':        'Full Name',
  'register.email':       'Email',
  'register.phone':       'Phone (optional)',
  'register.password':    'Password',
  'register.confirm':     'Confirm Password',
  'register.submit':      'Create Account',
  'register.creating':    'Creating account...',
  'register.login':       'Sign in',
  'register.have_account':'Already have an account?',

  // Nav
  'nav.priorities':       'Priorities',
  'nav.alerts':           'Alerts',
  'nav.devices':          'Devices',
  'nav.overview':         'Overview',
  'nav.reps':             'Reps',
  'nav.signout':          'Sign out',

  // Today / Priorities
  'today.greeting':       'Good morning',
  'today.growers_ranked': 'growers ranked by visit priority score',
  'today.loading':        'Loading your priorities...',
  'today.none':           'No priorities for today.',
  'today.high_priority':  'High Priority',
  'today.alerts':         'Alerts',
  'today.total':          'Total',
  'today.retry':          'Retry',
  'today.all_done':       'All caught up!',
  'today.no_growers':     'No growers to visit today.',

  // Grower detail
  'grower.ai_brief':      'AI Visit Brief',
  'grower.actions':       'Recommended Actions',
  'grower.log_outcome':   'Log Visit Outcome',
  'grower.log_another':   'Log Another Outcome',
  'grower.logged':        'Outcome logged',
  'grower.will_sync':     'Will sync automatically when connected.',
  'grower.go_back':       'Go Back',

  // Outcome form
  'outcome.logging_for':  'Logging outcome for',
  'outcome.rating':       'Visit Rating',
  'outcome.outcome':      'Outcome',
  'outcome.actions':      'Actions Taken',
  'outcome.notes':        'Notes',
  'outcome.notes_ph':     'Add visit notes, observations...',
  'outcome.save':         'Save Outcome',
  'outcome.saving':       'Saving...',
  'outcome.cancel':       'Cancel',
  'outcome.sale':         'Sale Completed',
  'outcome.follow_up':    'Follow-up Needed',
  'outcome.no_interest':  'No Interest',
  'outcome.complaint':    'Complaint Raised',
  'outcome.rating_err':   'Please select a rating.',
  'outcome.rate_1':       'Very poor',
  'outcome.rate_2':       'Poor',
  'outcome.rate_3':       'Average',
  'outcome.rate_4':       'Good',
  'outcome.rate_5':       'Excellent',

  // Anomalies
  'anomaly.title':        'Anomaly Alerts',
  'anomaly.detected':     'anomalies detected across your territory',
  'anomaly.scanning':     'Scanning for anomalies...',
  'anomaly.none':         'No anomalies detected',
  'anomaly.all':          'All',
  'anomaly.high':         'High',
  'anomaly.medium':       'Medium',
  'anomaly.low':          'Low',
  'anomaly.no_filter':    'No anomalies for this filter.',

  // Devices
  'devices.title':        'Your Devices',
  'devices.subtitle':     "Devices logged into your account. Revoke any you don't recognize.",
  'devices.current_id':   'Current device ID',
  'devices.this_device':  'This device',
  'devices.revoke':       'Revoke',
  'devices.revoke_confirm': 'Revoke this device? It will be signed out.',

  // Manager overview
  'manager.overview':     'Territory Overview',
  'manager.health':       'Territory Health',
  'manager.healthy':      'Healthy',
  'manager.moderate':     'Moderate',
  'manager.at_risk':      'At Risk',
  'manager.total_reps':   'Total Reps',
  'manager.growers':      'Growers',
  'manager.outcomes_30d': 'Outcomes (30d)',
  'manager.avg_rating':   'Avg Rating',
  'manager.high_priority':'High Priority',
  'manager.top_priorities':'Top Priorities Across Territory',
  'manager.view_all':     'View all reps →',

  // Reps list
  'reps.title':           'Field Representatives',
  'reps.in_territory':    'reps in your territory',
  'reps.excellent':       'Excellent',
  'reps.total':           'Total',
  'reps.at_risk':         'At Risk',
  'reps.sort_by':         'Sort by',
  'reps.outcomes':        'Outcomes',
  'reps.rating':          'Rating',
  'reps.name':            'Name',
  'reps.growers':         'Growers',
  'reps.outcomes_30d':    'Outcomes (30d)',
  'reps.avg_rating':      'Avg Rating',
  'reps.none':            'No reps found.',
  'reps.perf_excellent':  'Excellent',
  'reps.perf_good':       'Good',
  'reps.perf_attention':  'Needs Attention',

  // Rep detail tabs
  'rep.priorities':       'Priorities',
  'rep.outcomes':         'Outcomes',
  'rep.anomalies':        'Anomalies',
  'rep.no_priorities':    'No priorities assigned.',
  'rep.no_outcomes':      'No recent outcomes.',
  'rep.no_anomalies':     'No anomalies for this rep.',

  // Sync
  'sync.pending':         'pending',
  'sync.now':             'Sync now',

  // Time
  'time.just_now':        'Just now',
  'time.ago':             'ago',
  'time.active_now':      'Active now',
}

// ─── Hindi strings ────────────────────────────────────────────────────────────
const hi: Record<string, string> = {
  // Auth
  'auth.title':           'फील्ड फोर्स इंटेलिजेंस',
  'auth.subtitle':        'सिंजेंटा — बीकानेर क्षेत्र',
  'auth.tab.password':    'ईमेल / पासवर्ड',
  'auth.tab.otp':         'फोन OTP',
  'auth.email':           'ईमेल या फोन',
  'auth.password':        'पासवर्ड',
  'auth.signin':          'साइन इन करें',
  'auth.signing_in':      'साइन इन हो रहा है...',
  'auth.phone':           'फोन नंबर',
  'auth.send_otp':        'OTP भेजें',
  'auth.sending_otp':     'OTP भेजा जा रहा है...',
  'auth.enter_otp':       'OTP दर्ज करें',
  'auth.verify_otp':      'OTP सत्यापित करें',
  'auth.verifying':       'सत्यापन हो रहा है...',
  'auth.register':        'पासवर्ड से रजिस्टर करें',
  'auth.new_account':     'नया खाता?',
  'auth.demo':            'डेमो क्रेडेंशियल',

  // Register
  'register.title':       'खाता बनाएं',
  'register.name':        'पूरा नाम',
  'register.email':       'ईमेल',
  'register.phone':       'फोन (वैकल्पिक)',
  'register.password':    'पासवर्ड',
  'register.confirm':     'पासवर्ड की पुष्टि करें',
  'register.submit':      'खाता बनाएं',
  'register.creating':    'खाता बन रहा है...',
  'register.login':       'साइन इन करें',
  'register.have_account':'पहले से खाता है?',

  // Nav
  'nav.priorities':       'प्राथमिकताएं',
  'nav.alerts':           'अलर्ट',
  'nav.devices':          'डिवाइस',
  'nav.overview':         'अवलोकन',
  'nav.reps':             'प्रतिनिधि',
  'nav.signout':          'साइन आउट',

  // Today / Priorities
  'today.greeting':       'नमस्ते',
  'today.growers_ranked': 'किसान विज़िट प्राथमिकता के अनुसार क्रमबद्ध',
  'today.loading':        'प्राथमिकताएं लोड हो रही हैं...',
  'today.none':           'आज कोई प्राथमिकता नहीं।',
  'today.high_priority':  'उच्च प्राथमिकता',
  'today.alerts':         'अलर्ट',
  'today.total':          'कुल',
  'today.retry':          'पुनः प्रयास',
  'today.all_done':       'सब ठीक है!',
  'today.no_growers':     'आज कोई किसान नहीं मिलना है।',

  // Grower detail
  'grower.ai_brief':      'AI विज़िट सारांश',
  'grower.actions':       'अनुशंसित कार्रवाइयां',
  'grower.log_outcome':   'विज़िट परिणाम दर्ज करें',
  'grower.log_another':   'और परिणाम दर्ज करें',
  'grower.logged':        'परिणाम दर्ज हो गया',
  'grower.will_sync':     'कनेक्ट होने पर स्वचालित रूप से सिंक होगा।',
  'grower.go_back':       'वापस जाएं',

  // Outcome form
  'outcome.logging_for':  'के लिए परिणाम दर्ज करना',
  'outcome.rating':       'विज़िट रेटिंग',
  'outcome.outcome':      'परिणाम',
  'outcome.actions':      'की गई कार्रवाइयां',
  'outcome.notes':        'नोट्स',
  'outcome.notes_ph':     'विज़िट नोट्स, टिप्पणियां...',
  'outcome.save':         'परिणाम सहेजें',
  'outcome.saving':       'सहेजा जा रहा है...',
  'outcome.cancel':       'रद्द करें',
  'outcome.sale':         'बिक्री पूर्ण',
  'outcome.follow_up':    'फॉलो-अप जरूरी',
  'outcome.no_interest':  'कोई रुचि नहीं',
  'outcome.complaint':    'शिकायत दर्ज',
  'outcome.rating_err':   'कृपया रेटिंग चुनें।',
  'outcome.rate_1':       'बहुत खराब',
  'outcome.rate_2':       'खराब',
  'outcome.rate_3':       'ठीक है',
  'outcome.rate_4':       'अच्छा',
  'outcome.rate_5':       'बहुत अच्छा',

  // Anomalies
  'anomaly.title':        'असामान्य अलर्ट',
  'anomaly.detected':     'आपके क्षेत्र में असामान्यताएं मिलीं',
  'anomaly.scanning':     'असामान्यताएं खोजी जा रही हैं...',
  'anomaly.none':         'कोई असामान्यता नहीं मिली',
  'anomaly.all':          'सभी',
  'anomaly.high':         'उच्च',
  'anomaly.medium':       'मध्यम',
  'anomaly.low':          'निम्न',
  'anomaly.no_filter':    'इस फ़िल्टर के लिए कोई अलर्ट नहीं।',

  // Devices
  'devices.title':        'आपके डिवाइस',
  'devices.subtitle':     'आपके खाते में लॉग इन डिवाइस। अपरिचित को रद्द करें।',
  'devices.current_id':   'वर्तमान डिवाइस ID',
  'devices.this_device':  'यह डिवाइस',
  'devices.revoke':       'रद्द करें',
  'devices.revoke_confirm': 'इस डिवाइस को रद्द करें? इसे साइन आउट कर दिया जाएगा।',

  // Manager overview
  'manager.overview':     'क्षेत्र अवलोकन',
  'manager.health':       'क्षेत्र स्वास्थ्य',
  'manager.healthy':      'स्वस्थ',
  'manager.moderate':     'सामान्य',
  'manager.at_risk':      'खतरे में',
  'manager.total_reps':   'कुल प्रतिनिधि',
  'manager.growers':      'किसान',
  'manager.outcomes_30d': 'परिणाम (30 दिन)',
  'manager.avg_rating':   'औसत रेटिंग',
  'manager.high_priority':'उच्च प्राथमिकता',
  'manager.top_priorities':'क्षेत्र की शीर्ष प्राथमिकताएं',
  'manager.view_all':     'सभी प्रतिनिधि देखें →',

  // Reps list
  'reps.title':           'फील्ड प्रतिनिधि',
  'reps.in_territory':    'आपके क्षेत्र में प्रतिनिधि',
  'reps.excellent':       'उत्कृष्ट',
  'reps.total':           'कुल',
  'reps.at_risk':         'ध्यान चाहिए',
  'reps.sort_by':         'क्रमबद्ध करें',
  'reps.outcomes':        'परिणाम',
  'reps.rating':          'रेटिंग',
  'reps.name':            'नाम',
  'reps.growers':         'किसान',
  'reps.outcomes_30d':    'परिणाम (30 दिन)',
  'reps.avg_rating':      'औसत रेटिंग',
  'reps.none':            'कोई प्रतिनिधि नहीं मिला।',
  'reps.perf_excellent':  'उत्कृष्ट',
  'reps.perf_good':       'अच्छा',
  'reps.perf_attention':  'ध्यान चाहिए',

  // Rep detail tabs
  'rep.priorities':       'प्राथमिकताएं',
  'rep.outcomes':         'परिणाम',
  'rep.anomalies':        'असामान्यताएं',
  'rep.no_priorities':    'कोई प्राथमिकता नहीं।',
  'rep.no_outcomes':      'कोई हालिया परिणाम नहीं।',
  'rep.no_anomalies':     'इस प्रतिनिधि के लिए कोई असामान्यता नहीं।',

  // Sync
  'sync.pending':         'बकाया',
  'sync.now':             'अभी सिंक करें',

  // Time
  'time.just_now':        'अभी',
  'time.ago':             'पहले',
  'time.active_now':      'अभी सक्रिय',
}