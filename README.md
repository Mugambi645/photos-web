# 📷 Photos-Web

Photos-Web is a Django-based web application for uploading, tagging, and managing images. It supports automatic image tagging using machine learning, and can be deployed locally, with Docker, or on Kubernetes.
Additionally, it features an enhanced photo search powered by the Unsplash API for finding and importing high-quality images.


---

## 🚀 Features

* User authentication
* Image upload or taking own photos and gallery view
* Liking and unliking images
* Powerful image search enhanced with unsplash API
* Automatic image tagging
* Admin dashboard
* Dockerized for easy deployment
* Kubernetes-ready

---

## 🛠️ Setup Instructions

### 🔧 Prerequisites

* Python 3.10+
* Docker
* Kubernetes (e.g., Minikube)
* Git

---

### ⚙️ Local Development


1. **Clone the repository**:

   ```bash
   git clone https://github.com/Mugambi645/photos-web.git
   cd photos-web
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

---

## 🔍 Usage of Enhanced Photo Search (Unsplash API)

Photos-Web integrates with the [Unsplash API](https://unsplash.com/developers) to allow users to search for and import high-quality photos directly into their galleries.

### Configuration

1. Sign up at [Unsplash Developers](https://unsplash.com/developers) and create an application to get an access key.
2. Add the access key to your `.env` file:

```
UNSPLASH_ACCESS_KEY=your_access_key_here
```

### How It Works

* Use the search bar in the app interface to enter a keyword.
* The backend queries the Unsplash API for results.
* Selected images can be imported into the user gallery.

---


### 🐳 Docker Usage

1. **Build and tag the image**:

   ```bash
   docker build -t mugambi645/photos-web:latest .
   ```

2. **Run the container**:

   ```bash
   docker run -p 8000:8000 mugambi645/photos-web:latest
   ```

3. **Push to Docker Hub** (if needed):

   ```bash
   docker push mugambi645/photos-web:latest
   ```

---

### ☘️ Kubernetes Deployment

1. **Start Minikube** (if not already running):

   ```bash
   minikube start
   ```

2. **Apply Kubernetes configs**:

   ```bash
   kubectl apply -f kubernetes/deployment.yaml
   kubectl apply -f kubernetes/service.yaml
   ```

3. **Get the service URL**:

   ```bash
   minikube service photos-web-service
   ```

> ⚠️ **Note**: Ensure `ALLOWED_HOSTS` includes the Minikube IP (e.g. `192.168.49.2`).

---

## 📁 Folder Structure

```
photos-web/
├── gallery/               # Image upload and tagging app
├── account/               # User accounts and auth
├── media/                 # Uploaded media files
├── static/                # Static files
├── templates/             # HTML templates
├── manage.py
├── requirements.txt
├── Dockerfile
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
└── README.md
```

---

## ✅ Improvements To Be Made

Here are some enhancements planned or recommended for future versions:

### 🔧 Functional Improvements

* [ ] Add photo search and filters
* [ ] Add captions or descriptions to uploaded images
* [ ] Allow batch uploads
* [ ] Add pagination to the gallery view
* [ ] Support image albums or categories

### 🧠 Machine Learning

* [ ] Replace current image tagging model with a more finetuned model
* [ ] Add confidence scores to tags
* [ ] Run tagging asynchronously using Celery and Redis

### 🔒 Security & Config

* [ ] Add HTTPS support for production
* [ ] Use environment variables for secret keys
* [ ] Add rate limiting and input validation

### 🧪 Testing & CI/CD

* [ ] Write unit and integration tests
* [ ] Add GitHub Actions for CI/CD
* [ ] Set up automated Docker builds and pushes

---

## 📜 License

MIT License. See `LICENSE` file for details.

---

## ✨ Author

**Mugambi Patrick**
GitHub: [@Mugambi645](https://github.com/Mugambi645)






