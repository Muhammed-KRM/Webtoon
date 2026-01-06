# GitHub'a Yükleme Adımları

## ✅ **Manuel Adımlar (Komutlar Çalışmazsa)**

Eğer komutlar çalışmazsa, şu adımları manuel olarak takip edin:

### 1. GitHub'da Repo Oluştur
1. https://github.com/Muhammed-KRM adresine git
2. "New repository" butonuna tıkla
3. Repository name: `webtoon-ai-translator`
4. Description: `Webtoon AI Translator - Professional machine translation platform`
5. Public seç
6. "Create repository" butonuna tıkla

### 2. Git Komutları
```bash
# Git init (eğer yapılmadıysa)
git init

# Git config
git config user.name "Muhammed-KRM"
git config user.email "ustunmuhammed09@gmail.com"

# Dosyaları ekle
git add .

# Commit
git commit -m "Initial commit: Webtoon AI Translator - Complete backend with all features"

# Remote ekle
git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git

# Branch'i main yap
git branch -M main

# Push et
git push -u origin main
```

### 3. Credential Sorunu
Eğer push sırasında şifre sorarsa:
- Username: `Muhammed-KRM`
- Password: GitHub Personal Access Token kullan (şifre değil!)

**Personal Access Token Oluştur:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. Note: "webtoon-ai-translator"
4. Scopes: `repo` seç
5. "Generate token" → Token'ı kopyala
6. Push sırasında şifre yerine bu token'ı kullan

---

## 🚀 **Otomatik Script (PowerShell)**

Aşağıdaki script'i çalıştırabilirsin:

```powershell
# Git init
git init
git config user.name "Muhammed-KRM"
git config user.email "ustunmuhammed09@gmail.com"

# Add files
git add .

# Commit
git commit -m "Initial commit: Webtoon AI Translator - Complete backend with all features"

# Remote add (GitHub'da repo oluşturduktan sonra)
git remote add origin https://github.com/Muhammed-KRM/webtoon-ai-translator.git

# Branch
git branch -M main

# Push
git push -u origin main
```

---

**Not:** GitHub'da repo oluşturma için web arayüzünü kullanman gerekebilir. API ile oluşturmak için Personal Access Token gerekir.

