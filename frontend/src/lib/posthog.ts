import posthog from 'posthog-js'

// Initialize PostHog for iHhashi analytics
posthog.init(
  import.meta.env.VITE_POSTHOG_KEY || 'zo_sk_SVySGLRXL-3EbOD1kRlWH3NXW5RRGofMdrVFW_YKneo',
  {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com',
    // Enable session recording for UX insights
    session_recording: {
      maskAllInputs: false,
      maskInputOptions: {
        password: true, // Always mask password fields
      },
    },
    // Capture page views automatically
    capture_pageview: true,
    // Persist user sessions
    persistence: 'localStorage',
  }
)

export default posthog
