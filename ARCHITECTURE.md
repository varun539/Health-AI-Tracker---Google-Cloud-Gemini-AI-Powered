User Request (Browser/Mobile)
↓
[Google Cloud Run - Streamlit App]
├─→ [LightGBM Model] → Recovery Prediction (<100ms)
├─→ [Google Gemini API] → AI Coaching (1-3s)
└─→ [Google Sheets API] → Data Logging (<50ms)

All auto-scaled, encrypted (HTTPS), monitored

text

---

## Google Cloud Products

| Product | Role | Why |
|---------|------|-----|
| **Cloud Run** | Serverless container deployment | Zero-ops, auto-scale, pay-per-use |
| **Gemini API** | Real-time LLM for fitness advice | Fast, reliable, JSON-structured output |
| **Sheets API** | Serverless backend database | No infrastructure, instant analytics |
| **Artifact Registry** | Private Docker image storage | Secure, version-controlled builds |
| **Cloud Build** | Automated CI/CD from GitHub | Auto-deploy on git push |
| **IAM/Service Accounts** | Secure credential management | Granular permissions, no hardcoded keys |

---

## Data Flow

1. **User Input** → Streamlit form (name, age, workout, metrics)
2. **ML Prediction** → LightGBM model calculates recovery time
3. **AI Coaching** → Gemini API generates personalized advice (JSON)
4. **Data Logging** → Google Sheets API stores entry
5. **Display** → Streamlit renders results + coaching

---

## Performance Metrics

- **Latency:** <2 seconds total (parallel calls)
- **Throughput:** 0→1000+ concurrent users (auto-scaled)
- **Availability:** 99.9% uptime (Cloud Run SLA)
- **Cost:** ~$0.02 per prediction (pay-per-use)

---