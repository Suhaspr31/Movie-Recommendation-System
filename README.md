# Movie Recommendation System

A full-stack movie recommendation system built with **React**, **Node.js**, **Express**, **MongoDB**, and **Apache Spark-derived logic**. Uses collaborative filtering with **ALS (Alternating Least Squares)** factors for highly personalized movie suggestions.

## 🚀 Recent Updates: Personalized Engine
The system now features a **Dynamic Recommendation Controller**:
- **Personalized Logic**: Instead of static ID mapping, the system now analyzes each user's specific rating history (high-rated movies >= 3.5 stars).
- **Virtual Profile Generation**: The Flask ML engine calculates a "virtual user vector" in the factor space by averaging the feature vectors of movies the user has liked.
- **Improved Diversity**: Fallback logic now provides variety for new users by shuffling recommendation pools.

## 🏗️ Architecture

### Backend Components
- **Data Processing (Python/Flask)**: Handles ML inference by computing vector similarities and generating dynamic user profiles using `pandas` and `numpy`.
- **API Server (Node.js/Express)**: Core business logic, JWT authentication, and the personalization proxy that bridges user data with the ML engine.
- **Database (MongoDB Atlas)**: Stores user profiles, rating history, and movie metadata.

### Frontend
- **React Application**: Modern, responsive UI for movie discovery, interactive rating, and personalized dashboards.

## 🛠️ Tech Stack
- **Frontend**: React, React Router, Axios, React Toastify, Lucide Icons
- **Backend API**: Node.js, Express.js, MongoDB, Mongoose, JWT
- **ML Engine**: Python 3.10+, Flask, Pandas, NumPy, Scikit-learn
- **Database**: MongoDB Atlas

## ✨ Key Features
- **Smart Personalization**: Suggestions evolve in real-time as you rate more movies.
- **Genre-Match System**: Filter recommendations to see only genres you love.
- **Advanced Rating UI**: Precision rating (0.5 to 5.0 stars) with visual feedback.
- **Scalable Factor Space**: Uses pre-trained ALS factors for high-performance inference.
- **Watch History**: Keep track of everything you've seen and liked.

## 🌍 Production Deployment Guide

To deploy this project for free, follow these specific instructions for each service:

### 1. Database (MongoDB Atlas)
- Ensure your MongoDB Atlas cluster is active.
- Important: **Whitelist IP `0.0.0.0/0`** in Atlas "Network Access" to allow cloud services (like Render) to connect.

### 2. ML Engine (Python)
**Platform: [Render.com](https://render.com) (Web Service)**
- **Root Directory**: `data-processing`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT pyspark_recommendation_engine:app`
- **Python Version**: Set to `3.10.12` (Important to avoid build errors)
- **Env Vars**: Set `PORT` to `10000` and `PYTHON_VERSION` to `3.10.12`.

### 3. Backend API (Node.js)
**Platform: [Render.com](https://render.com) (Web Service)**
- **Root Directory**: `backend`
- **Build Command**: `npm install`
- **Start Command**: `node server.js`
- **Env Vars**:
  - `MONGODB_URI`: (Your Atlas URL)
  - `JWT_SECRET`: (Your Secret Key)
  - `PYSPARK_API_URL`: (The URL of your deployed ML Engine)

### 4. Frontend (React)
**Platform: [Vercel.com](https://vercel.com) or [Netlify.com](https://netlify.com)**
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist` (or `build`)
- **Env Vars**:
  - `VITE_API_URL`: (The URL of your deployed Backend API + `/api`)

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```env
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
PYSPARK_API_URL=http://localhost:5001
PORT=5000
```

### Data Processing (`data-processing/.env`)
```env
FLASK_APP=pyspark_recommendation_engine.py
PORT=5001
```

## 📁 Project Structure
```text
movie-recommendation-system/
├── backend/                 # Node.js API server
│   ├── controllers/         # Recommendation & Auth Logic
│   ├── models/              # Mongoose Schemas (User, Movie, Rating)
│   └── server.js            # Entry Point
├── data-processing/        # Python ML engine
│   ├── models/              # ALS Factor Backup (CSV)
│   └── engine.py            # Similarity Engine
├── frontend/               # React UI
│   ├── src/pages/           # Discovery & Profile Views
│   └── src/services/        # API Integration Layer
└── README.md
```

## 📜 License
This project is licensed under the MIT License.
