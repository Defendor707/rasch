# 🎓 O'zbekiston BBA Standartlariga mos Rasch Model Telegram Bot

Bu bot O'zbekiston Respublikasining Bilim va Malakalarni Baholash Agentligi (BBA) standartlariga mos Rasch modeli orqali test natijalarini tahlil qiladi.

## 🚀 Asosiy Xususiyatlar

### 📊 **BBA Standartlariga Mos Rasch Modeli**
- **Model turi**: Dichotomous Rasch modeli (0/1 format)
- **Estimation usuli**: Conditional Maximum Likelihood Estimation (CMLE)
- **Qobiliyat oralig'i**: -3.5 dan +3.5 logit
- **Item qiyinligi oralig'i**: -3.7 dan +3.3 logit

### 📈 **Fit Statistikalar**
- **Infit statistikalar**: Variance bilan og'irlangan moslik
- **Outfit statistikalar**: Oddiy o'rtacha moslik
- **Fit baholash**: Yaxshi (0.8-1.2), Qabul qilinadigan (0.7-1.3)

### 🗺️ **Wright Map (Item-Person Xaritasi)**
- Talabalar qobiliyati taqsimoti
- Savollar qiyinligi taqsimoti
- Test information function
- BBA standartlariga mos visualizatsiya

## 🔧 O'rnatish

```bash
# Dependencies o'rnatish
pip install -r requirements.txt

# Yoki uv bilan
uv sync
```

## 🚀 Ishga tushirish

```bash
python main.py
```

## 📋 Foydalanish

### 1. Excel fayl tayyorlash
- Birinchi ustunda talaba ismi/ID
- Qolgan ustunlarda savol javoblari (1 = to'g'ri, 0 = noto'g'ri)
- .xlsx yoki .xls formatda

### 2. Bot bilan ishlash
1. `/start` - Botni ishga tushirish
2. Excel faylni yuklash
3. Natijalarni ko'rish:
   - 📊 Barcha natijalar va grafiklar
   - 📈 Fit statistikalar
   - 🗺️ Wright map
   - 💾 Excel/PDF yuklash

## 📊 Natijalar

### Asosiy ma'lumotlar:
- Talaba qobiliyati (θ)
- Standart ball
- Baholash (A+, A, B+, B, C+, C, NC)
- To'g'ri javoblar soni
- Foiz (%)

### Fit statistikalar:
- Infit va Outfit ko'rsatkichlari
- Moslik foizi
- Model sifatini baholash

### Wright map:
- Talabalar qobiliyati taqsimoti
- Savollar qiyinligi taqsimoti
- Test information function

## 🎯 BBA Standartlari

### Model parametrlari:
- **Qobiliyat oralig'i**: -3.5 to +3.5 logits
- **Item qiyinligi oralig'i**: -3.7 to +3.3 logits
- **Estimation usuli**: Conditional MLE (CMLE)
- **Fit mezonlari**: Infit/Outfit 0.7-1.3 oralig'ida

### Baholash tizimi:
- **A+**: 85-100% (Ajoyib)
- **A**: 75-84% (Yaxshi)
- **B+**: 65-74% (Qoniqarli)
- **B**: 55-64% (O'rtacha)
- **C+**: 45-54% (Past)
- **C**: 35-44% (Juda past)
- **NC**: <35% (O'tmagan)

## 🔍 Texnik Xususiyatlar

### Rasch Model:
- Conditional Maximum Likelihood Estimation
- Newton-Raphson optimizatsiya
- Ekstremal holatlarni boshqarish
- Parallel processing

### Fit Statistikalar:
- Infit: Variance bilan og'irlangan
- Outfit: Oddiy o'rtacha
- Fit baholash: BBA standartlari bo'yicha

### Visualizatsiya:
- Wright map (item-person xaritasi)
- Fit statistikalar grafiklari
- Baholar taqsimoti
- Test information function

## 📁 Fayl tuzilishi

```
├── main.py              # Asosiy ishga tushirish fayli
├── telegram_bot.py      # Telegram bot asosiy kodi
├── rasch_model.py       # BBA standartlariga mos Rasch modeli
├── data_processor.py    # Ma'lumotlarni qayta ishlash
├── utils.py            # Yordamchi funksiyalar
├── bot_database.py     # Ma'lumotlar bazasi
├── users.py            # Foydalanuvchilar boshqaruvi
├── pyproject.toml      # Dependencies
└── README.md           # Ushbu fayl
```

## 🛠️ Dependencies

- `pytelegrambotapi` - Telegram bot API
- `pandas` - Ma'lumotlar tahlili
- `numpy` - Hisoblash
- `scipy` - Ilmiy hisoblash
- `matplotlib` - Grafiklar
- `seaborn` - Statistika grafiklari
- `reportlab` - PDF yaratish
- `openpyxl` - Excel fayllar
- `xlsxwriter` - Excel formatlash

## 📞 Yordam

Agar savollaringiz bo'lsa:
- Telegram: @rasch_counter
- Email: support@rasch-bot.uz

## 📄 Litsenziya

Bu loyiha O'zbekiston BBA standartlariga mos ravishda ishlab chiqilgan.

---

**🎓 O'zbekiston BBA Standartlariga mos Rasch Model Bot**
*Aniq va ishonchli test natijalarini tahlil qilish* 