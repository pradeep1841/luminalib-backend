# 📚 LuminaLib Backend

A scalable backend system for managing digital libraries with authentication, book ingestion, AI-powered summarization, and recommendations.

---

## 🚀 Features

* 🔐 JWT Authentication (Signup, Login, Profile)
* 📚 Book Upload & Management (CRUD)
* 🔄 Borrow & Return System
* ⭐ Review System (only after borrow)
* 🤖 AI-based Book Summarization (Background Tasks)
* 🧠 Recommendation Engine (based on user activity)
* 🐳 Dockerized (API + PostgreSQL)
* ⚙️ Environment-based configuration (.env)

---

## 🛠️ Tech Stack

* FastAPI
* PostgreSQL
* SQLAlchemy
* Docker & Docker Compose
* Python

---

## 🚀 Run the Project

```bash
docker-compose up --build
```

👉 Open:
http://localhost:8000/docs

---

## 🔐 Authentication Flow

1. Signup → `/auth/signup`
2. Login → `/auth/login`
3. Copy token
4. Authorize → Bearer TOKEN

---

## 📂 Project Structure

app/
├── api/
├── models/
├── core/
├── services/
└── main.py

---

## ⚙️ Environment Variables

Create `.env` file:

DATABASE_URL=postgresql://user:pass@db:5432/luminalib
SECRET_KEY=mysecretkey
ALGORITHM=HS256

---

## 🎯 Key Highlights

* Clean architecture with separation of concerns
* Stateless authentication using JWT
* Async background processing
* Docker-based deployment

---

## 🚀 Future Improvements

* Integrate real LLM (Ollama/OpenAI)
* Advanced recommendation system
* Review sentiment aggregation
