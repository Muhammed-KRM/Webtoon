# Webtoon AI Translator - Kurulum ve Başlatma Rehberi

Sistemi tam anlamıyla (Redis, Celery, Docker ile) çalıştırmak için aşağıdaki adımları takip edin.

## Yöntem 1: Otomatik Kurulum (Önerilen)

Sizin için hazırladığım script, gerekli araçları **winget** (Windows Paket Yöneticisi) kullanarak indirir.

1.  Proje klasöründeki `INSTALL_TOOLS.bat` dosyasına **sağ tıklayın** ve **"Yönetici olarak çalıştır"** diyin.
2.  Çıkan mavi/siyah ekranda kurulumun başlamasını bekleyin.
3.  **Docker Desktop** kurulum penceresi açıldığında "Ok" veya "Install" butonuna tıklayın.
4.  Kurulum bitince bilgisayarınızı **YENİDEN BAŞLATIN**.

## Yöntem 2: Manuel İndirme ve Kurulum

Eğer script çalışmazsa, elle şu adımları yapın:

### 1. Docker Desktop Kurulumu

1.  [Docker Desktop İndir](https://www.docker.com/products/docker-desktop/) adresine gidin.
2.  "Download for Windows" butonuna tıklayın.
3.  İnen `Docker Desktop Installer.exe` dosyasını çalıştırın.
4.  Kurulumda "Use WSL 2 instead of Hyper-V" seçeneği işaretli olsun.
5.  Kurulum bitince "Close and log out" veya "Restart" diyerek bilgisayarı yeniden başlatın.
6.  Bilgisayar açılınca Docker Desktop programını başlatın ve sözleşmeyi kabul edin (Accept). Sol altta "Engine running" (Yeşil) yazana kadar bekleyin.

### 2. VS Code Eklentileri (Opsiyonel ama Önerilir)

VS Code kullanıyorsanız şu eklentileri kurarak işinizi kolaylaştırın:

1.  VS Code'da sol taraftaki kareler ikonuna (Extensions) tıklayın.
2.  Arama çubuğuna **"Docker"** yazın (Microsoft olanı).
3.  **Install** butonuna basın.
4.  Bu eklenti sayesinde sol menüde bir Balina ikonu çıkacak, oradan container'larınızı yönetebilirsiniz.

---

## Sistemi Başlatma

Kurulumlar bittikten sonra:

1.  **Docker Desktop** uygulamasının açık olduğundan emin olun.
2.  Proje klasöründeki `START_DOCKER_APP.bat` dosyasına çift tıklayın.
3.  Bu script `docker-compose up` komutunu çalıştıracak ve tüm sistemi (Web Uygulaması + Redis + Celery) otomatik kuracaktır.
4.  Tarayıcıdan **http://localhost:8000** adresine gidin.

## Sorun Yaşarsanız

- **"Docker is not running" hatası:** Docker Desktop uygulamasını başlatmamışsınız demektir. Başlat menüsünden açın.
- **"WSL 2 installation is incomplete" hatası:** Docker ilk açılışta ekranda bir link verir, o linke tıklayıp ufak bir güncelleme dosyasını kurmanız gerekir.
- **Hala çalışmıyorsa:** `SETUP_AUTO.bat` ile sadece Python ortamını kurup, Redis olmadan (bazı özellikler eksik olarak) sistemi `START.bat` ile deneyebilirsiniz (az önceki testimizde yaptığımız gibi).
