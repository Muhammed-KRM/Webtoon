# 📤 GitHub'a Yükleme Talimatları

## 🚀 **Hızlı Başlangıç**

### Adım 1: GitHub'da Repo Oluştur

1. **GitHub'a git:** https://github.com/Muhammed-KRM
2. **"New repository"** butonuna tıkla
3. **Repository name:** `webtoon-ai-translator`
4. **Description:** `Webtoon AI Translator - Professional machine translation platform`
5. **Public** seç
6. **"Create repository"** butonuna tıkla

### Adım 2: Script'i Çalıştır

**Seçenek 1: Otomatik Script (Önerilen)**
```bash
GITHUB_DEPLOY.bat
```

**Seçenek 2: Manuel Komutlar**
```bash
# Git init
git init
git config user.name "Muhammed-KRM"
git config user.email "ustunmuhammed09@gmail.com"

# Dosyaları ekle
git add .

# Commit
git commit -m "Initial commit: Webtoon AI Translator - Complete backend with all features"

# Remote ekle
git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git

# Branch
git branch -M main

# Push
git push -u origin main
```

### Adım 3: Authentication

Push sırasında şifre sorarsa:
- **Username:** `Muhammed-KRM`
- **Password:** GitHub Personal Access Token (şifre değil!)

**Personal Access Token Oluştur:**
1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **"Generate new token"** → **"Generate new token (classic)"**
3. **Note:** `webtoon-ai-translator`
4. **Scopes:** `repo` seç
5. **"Generate token"** → Token'ı kopyala
6. Push sırasında şifre yerine bu token'ı kullan

---

## ✅ **Komutlar Başarıyla Çalıştırıldı**

Aşağıdaki komutlar zaten çalıştırıldı:
- ✅ `git init` - Git repo oluşturuldu
- ✅ `git config` - Kullanıcı bilgileri ayarlandı
- ✅ `git add .` - Dosyalar eklendi
- ✅ `git commit` - Commit oluşturuldu
- ✅ `git remote add origin` - Remote eklendi
- ✅ `git branch -M main` - Branch main yapıldı

**Sadece push kaldı!**

---

## 🔐 **Push İçin**

**Önce GitHub'da repo oluştur, sonra:**

```bash
git push -u origin main
```

Eğer authentication sorunu olursa, Personal Access Token kullan.

---

## 📋 **Repository Bilgileri**

- **Repository Name:** `webtoon-ai-translator`
- **URL:** https://github.com/Muhammed-KRM/webtoon-ai-translator
- **Owner:** Muhammed-KRM
- **Visibility:** Public

---

**Hazır! Sadece GitHub'da repo oluştur ve push et!** 🚀

