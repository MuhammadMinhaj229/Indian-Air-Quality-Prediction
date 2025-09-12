# 🌍 Indian Air Quality Prediction

🚀 A machine learning powered system to **predict Air Quality Index (AQI)** across Indian cities, using real-time data pipelines and historical datasets. This project integrates **data preprocessing, feature engineering, regression/classification models, and a FastAPI backend**, with a simple **frontend UI** for user interaction.

---

## 📌 Project Overview

Air pollution is one of the biggest environmental concerns in India. This project aims to:

* Predict **AQI levels** using regression and classification ML models.
* Provide **health advisories** based on predicted AQI categories.
* Enable **real-time predictions** using raw CSV datasets or OpenAQ API.
* Expose an **API (FastAPI)** that can be connected to a **frontend (React + Tailwind)** for users.

---

## 🛠️ Tech Stack

### **Backend (FastAPI)**

* Python 3.10+
* FastAPI 🚀 (REST API framework)
* Uvicorn (ASGI server)
* Joblib (model persistence)
* Pandas & NumPy (data processing)
* scikit-learn (ML regression + classification models)
* Requests (OpenAQ API integration)

### **Machine Learning**

* Trained **Random Forest Regression** and **Random Forest Classification** models.
* Trained/tested in **Google Colab** on CSV datasets.
* Feature engineering with pollutants like **SO₂, NO₂, PM10, PM2.5**.

### **Frontend (UI)**

* Vite + React ⚛️
* TypeScript
* Tailwind CSS 🎨
* Axios (API calls to backend)

### **Deployment**

* Backend: **Render / Docker-ready**
* Model storage: **Git LFS** for large `.joblib` files
* Frontend: **Vercel / Netlify** (easy deployment)

---

## 📂 Project Structure

```
Indian-Air-Quality-Prediction/
│── backend/
│   ├── main.py                # FastAPI app
│   ├── quick_test.py          # Local test script
│   ├── feature_engineering.py # Data transformation
│   ├── requirements.txt       # Backend dependencies
│   ├── model/
│   │   ├── model_rf.joblib    # Regression model
│   │   ├── model_clf_rf.joblib# Classification model
│   │   └── metadata.json      # Model metadata
│── frontend/
│   ├── src/                   # React + Tailwind code
│   ├── package.json
│   ├── vite.config.ts
│── data.csv (raw dataset - ignored in repo)
│── README.md
```

---

## ⚙️ How It Works

1. **Data Preprocessing**

   * Dataset cleaned & transformed into features: `si (SO₂ index), ni (NO₂ index), rpi (PM index)`

2. **Model Training**

   * Trained & optimized classification + regression models using Colab.
   * Saved models as `.joblib` files.

3. **Backend (FastAPI)**

   * `/predict` → Accepts pollutant values, returns AQI prediction + advisory.
   * `/predict_by_openaq` → Fetches live data from OpenAQ API.
   * `/meta` → Returns feature metadata.

4. **Frontend (React + Tailwind)**

   * Simple UI with input fields for pollutants.
   * Calls backend API → displays predicted AQI and health advisory.

---

## 🔮 Features

✅ Predict AQI using ML models
✅ Dual outputs: **Regression AQI value** & **Classification label**
✅ Health advisory messages for users
✅ Live OpenAQ API integration (city-based predictions)
✅ Ready for **Docker & Render deployment**

---

## 🚀 Getting Started

### Clone the repo

```bash
git clone https://github.com/MuhammadMinhaj229/Indian-Air-Quality-Prediction.git
cd Indian-Air-Quality-Prediction
```

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

API available at: 👉 [http://localhost:8080/docs](http://localhost:8080/docs)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

UI available at: 👉 [(http://127.0.0.1:3000/frontend/index.html)]

---

## 📊 Example Prediction

Request:

```json
POST /predict
{
  "features": {
    "si": 12.5,
    "ni": 34.2,
    "rpi": 56.8
  }
}
```

Response:

```json
{
  "aqi_regression": 78.42,
  "aqi_reg_category": "Moderate",
  "aqi_classification_label": "Moderate",
  "advisory": "Sensitive individuals should limit prolonged outdoor exertion."
}
```

---

## 🎯 Future Work

* Improve accuracy using **deep learning models**.
* Extend to **state & district level forecasting**.
* Integrate with **IoT sensors for real-time AQI monitoring**.
* Build a **progressive web app (PWA)** for mobile users.

---

## 👨‍💻 Author

**Muhammad Minhaj**

* 🎓 B.Tech CSE (Data Science)
* 🌱 Passionate about ML, AI, and impactful projects
* 🔗 [GitHub](https://github.com/MuhammadMinhaj229)
