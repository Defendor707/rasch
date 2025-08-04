import subprocess
import sys
import os

def run_telegram_bot():
    """Telegram botni ishga tushirish"""
    print("🚀 BBA Standartlariga mos Rasch Model Telegram Bot ishga tushirilmoqda...")
    print("📊 Fit statistikalar va Wright map funksiyalari qo'shildi")
    print("🎯 Conditional MLE estimation usuli ishlatiladi")
    subprocess.run([sys.executable, "telegram_bot.py"])

def test_rasch_model():
    """Rasch modelini test qilish"""
    print("🧪 Rasch modelini test qilish...")
    try:
        from rasch_model import RaschModel
        import numpy as np
        import matplotlib.pyplot as plt
        
        # Test ma'lumotlari yaratish
        np.random.seed(42)
        n_students, n_items = 50, 20
        test_data = np.random.binomial(1, 0.6, (n_students, n_items))
        
        # Rasch modelini yaratish
        rasch = RaschModel(test_data)
        success = rasch.fit()
        
        if success:
            print("✅ Rasch model muvaffaqiyatli ishladi!")
            print(f"📊 Talabalar: {rasch.n_students}, Savollar: {rasch.n_items}")
            print(f"🎯 Fit foizi: {rasch.fit_quality['fit_percentage']:.1f}%")
            
            # Wright map yaratish
            fig = rasch.create_wright_map()
            if fig:
                print("🗺️ Wright map yaratildi!")
                plt.close(fig)
            
            return True
        else:
            print("❌ Rasch model xatosi!")
            return False
            
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        return False

if __name__ == "__main__":
    print("🎓 O'zbekiston BBA Standartlariga mos Rasch Model Bot")
    print("=" * 60)
    
    # Test qilish
    if test_rasch_model():
        print("\n✅ Barcha testlar muvaffaqiyatli!")
        print("🚀 Bot ishga tushirilmoqda...")
        run_telegram_bot()
    else:
        print("\n❌ Test xatosi! Iltimos, xatoliklarni tekshiring.")
        sys.exit(1)