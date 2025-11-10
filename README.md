# 💪 Health AI Tracker - Google Cloud + Gemini AI Powered

**Hackathon Winner Submission** | LightGBM + Google Gemini AI + Cloud Run + Google Sheets

![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Production%20Ready-blue?style=flat-square) 
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square) 
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red?style=flat-square)

## 🏆 Project Overview

A **full-stack AI fitness coach web app** that predicts recovery time using **LightGBM** and delivers personalized AI coaching via **Google Gemini API**—all running 100% serverless on **Google Cloud Run**.

**🔴 Live Demo:** [https://health-ai-875022510495.europe-central2.run.app](https://health-ai-875022510495.europe-central2.run.app)

**📊 GitHub Repo:** [https://github.com/varun539/Health-AI-Tracker---Google-Cloud-Gemini-AI-Powered](https://github.com/varun539/Health-AI-Tracker---Google-Cloud-Gemini-AI-Powered)

---

## 🚀 Google Cloud Stack (100% Serverless)

### **6 Google Cloud Products Used:**

| # | Product | Purpose | Why |
|---|---------|---------|-----|
| 1 | **Cloud Run** | Containerized Streamlit deployment | Serverless, auto-scaling, zero-ops |
| 2 | **Gemini API** | Real-time AI fitness coaching | Multi-modal LLM, low-latency JSON |
| 3 | **Google Sheets API** | Backend database | Serverless, instant analytics |
| 4 | **Artifact Registry** | Docker image storage | Secure, private container repo |
| 5 | **Cloud Build** | CI/CD automation | Auto-deploy from GitHub |
| 6 | **IAM & Service Accounts** | Credential management | Secure, role-based access control |

---

## 📊 Tech Stack

| Layer | Technology | Why Used |
|-------|-----------|----------|
| **Frontend** | Streamlit 1.28 | Rapid prototyping, beautiful UI, zero config |
| **ML Model** | LightGBM | Fast, accurate, <100ms inference |
| **AI Coach** | Google Gemini 1.5 Flash | Real-time AI, JSON-structured responses |
| **Backend DB** | Google Sheets API | Serverless, zero infrastructure, instant scaling |
| **Deployment** | Cloud Run | Auto-scale 0→1000+, pay-per-use, global CDN |
| **Container** | Docker | Cloud-native, reproducible, production-ready |

---

## ✨ Key Features

✅ **LightGBM Recovery Prediction**
- Input: 15+ health/fitness metrics (age, weight, BMI, BPM, workout type, etc.)
- Output: Personalized recovery timeline (hours)
- Performance: <100ms inference time

✅ **Google Gemini AI Coach**
- Real-time nutrition, workout, and recovery advice
- JSON-based prompts for structured responses
- Personalized for each user's profile

✅ **Google Sheets Auto-Logging**
- Every prediction instantly logged
- Built-in analytics dashboard
- No database setup needed

✅ **Serverless Auto-Scaling**
- Scales from 0 to 1000+ concurrent users
- Zero infrastructure management
- Pay-per-use cost model

✅ **Mobile-Responsive UI**
- Dark theme Streamlit UI
- Works on desktop, tablet, mobile
- Intuitive form layout

✅ **Production-Ready**
- Comprehensive error handling
- Gemini fallback for resilience
- Encrypted data in transit (HTTPS)

---

