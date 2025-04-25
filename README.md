# 🧠 Multimodal AI Assistant

This project is a full-stack AI assistant application featuring:

- ✅ **Python FastAPI backend** for services like Text-to-Speech (TTS), Speech-to-Text (STT), and more.
- ✅ **React frontend** for user interaction.
- ✅ Modular structure and clean dependency management.

---

## 📁 Project Structure

```
root/
├── backend/                     # Python FastAPI services
├── frontend/                    # React frontend
├── .gitignore                   # Root ignore file
├── requirements.txt             # CPU dependencies
└── README.md                    # Project documentation
```

---

## 🔧 Installing Backend Dependencies 

Ensure you're in the **root directory** before running the following.

### 📦 For CPU-only (recommended for general users)

```bash
pip install -r requirements.txt
```

### ⚡ For Using GPU for faster experience with CUDA 11.8

```bash
pip install torch==2.6.0+cu118 torchvision==0.21.0+cu118 torchaudio==2.6.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

> ✅ GPU version requires NVIDIA drivers + CUDA 11.8 installed.

---

## 🌐 Installing Frontend Dependencies 

Navigate to the `frontend` directory and install:

```bash
cd frontend
npm install
```

---

## 🚀 Deployment or Uploading to GitHub

To upload this project to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

---

## 💡 Tips

- Do **not upload** the `.venv/` folder or large model folders.
- You may create a `scripts/` folder to add shell scripts for downloading pre-trained models if needed.
- You can update `requirements.txt` anytime with:

```bash
pip freeze > requirements.txt
```

✅ Be sure to remove CUDA-specific suffixes (`+cu118`) if sharing CPU-safe versions.

---

## 📬 Questions?

Feel free to open an issue or reach out if you encounter any problems. Enjoy building with AI! 🤖✨

---

## 📄 License

This project is dual-licensed under the terms of the MIT License and the Apache License 2.0.
You may choose either license to govern your use of this software.

See the [LICENSE](./LICENSE) file for details.
