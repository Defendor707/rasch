import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# O'zbekiston Milliy Sertifikat standartlari bo'yicha baholash (2024) - yangilangan
GRADE_DESCRIPTIONS = {
    'A+': 'Ajoyib (70+ ball) - Oliy Imtiyozli',
    'A': 'Yaxshi (65-69.9 ball) - Oliy', 
    'B+': 'Qoniqarli (60-64.9 ball) - Yuqori Imtiyozli',
    'B': 'O\'rtacha (55-59.9 ball) - Yuqori',
    'C+': 'Past (50-54.9 ball) - O\'rta Imtiyozli',
    'C': 'Juda past (46-49.9 ball) - O\'rta',
    'NC': 'O\'tmagan (<46 ball) - Sertifikatsiz'
}

# Grade colors for visualization - yangilangan PDF ranglariga mos
GRADE_COLORS = {
    'A+': '#006400',  # Dark Green (A+ daraja)
    'A': '#28B463',   # Green (A daraja)
    'B+': '#1A237E',  # Dark Blue (B+ daraja)
    'B': '#3498DB',   # Blue (B daraja)
    'C+': '#8D6E63',  # Brown (C+ daraja)
    'C': '#F4D03F',   # Yellow (C daraja)
    'NC': '#E74C3C'   # Red (NC daraja)
}

def display_grade_distribution(grade_counts):
    """Baholar taqsimotini ko'rsatish"""
    total = sum(grade_counts.values())
    if total == 0:
        return "Ma'lumotlar mavjud emas"
    
    text = "📊 **Baholar Taqsimoti**\n\n"
    
    for grade, count in grade_counts.items():
        if count > 0:
            percentage = (count / total) * 100
            description = GRADE_DESCRIPTIONS.get(grade, '')
            text += f"• {grade}: {count} ta ({percentage:.1f}%) - {description}\n"
    
    return text

def calculate_statistics(results_df):
    """Asosiy statistikalarini hisoblash - yangilangan"""
    if results_df.empty:
        return "Ma'lumotlar mavjud emas"
    
    total_students = len(results_df)
    avg_score = results_df['Standard Score'].mean()
    std_score = results_df['Standard Score'].std()
    min_score = results_df['Standard Score'].min()
    max_score = results_df['Standard Score'].max()
    
    # Baholar bo'yicha hisoblash
    grade_counts = results_df['Grade'].value_counts()
    passing_grades = grade_counts.get('A+', 0) + grade_counts.get('A', 0) + \
                    grade_counts.get('B+', 0) + grade_counts.get('B', 0) + \
                    grade_counts.get('C+', 0) + grade_counts.get('C', 0)
    pass_rate = (passing_grades / total_students) * 100
    
    # OTM foizi hisoblash (65 ball va undan yuqori) - yangilangan
    otm_threshold = 65
    otm_students = len(results_df[results_df['Standard Score'] >= otm_threshold])
    otm_percentage = (otm_students / total_students) * 100
    
    # A+ va A baholar soni (70+ va 65-69.9)
    top_grades = grade_counts.get('A+', 0) + grade_counts.get('A', 0)
    top_percentage = (top_grades / total_students) * 100
    
    text = f"""
📈 **Asosiy Statistika**

👥 **Talabalar:**
• Jami: {total_students} ta
• O'tish: {passing_grades} ta ({pass_rate:.1f}%)
• O'tmagan: {total_students - passing_grades} ta ({(100-pass_rate):.1f}%)

📊 **Ballar:**
• O'rtacha: {avg_score:.1f}
• Standart og'ish: {std_score:.1f}
• Minimum: {min_score:.1f}
• Maksimum: {max_score:.1f}

🎯 **OTM Foizi (65+ ball):**
• {otm_students} ta talaba ({otm_percentage:.1f}%)

🏆 **A+ va A baholar:**
• {top_grades} ta talaba ({top_percentage:.1f}%)

🎯 **Baholar taqsimoti:**
"""
    
    for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'NC']:
        count = grade_counts.get(grade, 0)
        if count > 0:
            percentage = (count / total_students) * 100
            description = GRADE_DESCRIPTIONS.get(grade, '')
            text += f"• {grade}: {count} ta ({percentage:.1f}%) - {description}\n"
    
    return text

def create_fit_statistics_plot(rasch_model, save_path=None):
    """Fit statistikalar grafigini yaratish"""
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Infit statistikalar
        ax1.hist(rasch_model.infit_stats, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(x=1.0, color='red', linestyle='--', label='Ideal (1.0)')
        ax1.axvline(x=0.8, color='orange', linestyle=':', label='Yaxshi moslik')
        ax1.axvline(x=1.2, color='orange', linestyle=':', label='Yaxshi moslik')
        ax1.set_xlabel('Infit Statistikasi')
        ax1.set_ylabel('Talabalar soni')
        ax1.set_title('Infit Statistikalar Taqsimoti')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Outfit statistikalar
        ax2.hist(rasch_model.outfit_stats, bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
        ax2.axvline(x=1.0, color='red', linestyle='--', label='Ideal (1.0)')
        ax2.axvline(x=0.8, color='orange', linestyle=':', label='Yaxshi moslik')
        ax2.axvline(x=1.2, color='orange', linestyle=':', label='Yaxshi moslik')
        ax2.set_xlabel('Outfit Statistikasi')
        ax2.set_ylabel('Talabalar soni')
        ax2.set_title('Outfit Statistikalar Taqsimoti')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Infit vs Outfit scatter plot
        ax3.scatter(rasch_model.infit_stats, rasch_model.outfit_stats, alpha=0.6, color='green')
        ax3.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
        ax3.axvline(x=1.0, color='red', linestyle='--', alpha=0.5)
        ax3.set_xlabel('Infit Statistikasi')
        ax3.set_ylabel('Outfit Statistikasi')
        ax3.set_title('Infit vs Outfit Korelyatsiyasi')
        ax3.grid(True, alpha=0.3)
        
        # Fit sifatini baholash
        fit_quality = rasch_model.fit_quality
        labels = ['Yaxshi', 'Qabul qilinadigan', 'Yomon']
        sizes = [fit_quality['good_fit'], 
                fit_quality['acceptable_fit'] - fit_quality['good_fit'], 
                fit_quality['poor_fit']]
        colors = ['green', 'orange', 'red']
        
        ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax4.set_title('Fit Sifatini Baholash')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    except Exception as e:
        print(f"Fit statistikalar grafigi xatosi: {e}")
        return None

def create_detailed_wright_map(rasch_model, save_path=None):
    """Batafsil Wright map yaratish"""
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Talabalar qobiliyati taqsimoti
        ax1.hist(rasch_model.theta, bins=25, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(x=np.mean(rasch_model.theta), color='red', linestyle='--', 
                   label=f'O\'rtacha: {np.mean(rasch_model.theta):.3f}')
        ax1.set_xlabel('Talaba Qobiliyati (θ)')
        ax1.set_ylabel('Talabalar soni')
        ax1.set_title('Talabalar Qobiliyati Taqsimoti')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Item qiyinligi taqsimoti
        ax2.hist(rasch_model.beta, bins=25, alpha=0.7, color='lightcoral', edgecolor='black')
        ax2.axvline(x=np.mean(rasch_model.beta), color='red', linestyle='--',
                   label=f'O\'rtacha: {np.mean(rasch_model.beta):.3f}')
        ax2.set_xlabel('Item Qiyinligi (β)')
        ax2.set_ylabel('Savollar soni')
        ax2.set_title('Savollar Qiyinligi Taqsimoti')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Qobiliyat vs Item qiyinligi
        ax3.scatter(rasch_model.beta, [0]*len(rasch_model.beta), alpha=0.6, color='red', s=50, label='Savollar')
        ax3.scatter([0]*len(rasch_model.theta), rasch_model.theta, alpha=0.6, color='blue', s=30, label='Talabalar')
        ax3.set_xlabel('Item Qiyinligi (β)')
        ax3.set_ylabel('Talaba Qobiliyati (θ)')
        ax3.set_title('Wright Map: Talabalar vs Savollar')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Test information function
        theta_range = np.linspace(-4, 4, 100)
        information = []
        for theta in theta_range:
            logits = theta - rasch_model.beta
            probs = 1 / (1 + np.exp(-logits))
            info = np.sum(probs * (1 - probs))
            information.append(info)
        
        ax4.plot(theta_range, information, color='green', linewidth=2)
        ax4.set_xlabel('Talaba Qobiliyati (θ)')
        ax4.set_ylabel('Test Ma\'lumotlari')
        ax4.set_title('Test Information Function')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    except Exception as e:
        print(f"Wright map xatosi: {e}")
        return None

def generate_bba_report(rasch_model, results_df):
    """BBA standartlariga mos hisobot yaratish"""
    try:
        report = f"""
📋 **BBA Standartlari Hisoboti**

🎯 **Model Ma'lumotlari:**
• Model turi: Dichotomous Rasch Model
• Estimation usuli: Conditional Maximum Likelihood (CMLE)
• Qobiliyat oralig'i: {rasch_model.theta_range[0]} to {rasch_model.theta_range[1]} logits
• Item qiyinligi oralig'i: {rasch_model.beta_range[0]} to {rasch_model.beta_range[1]} logits

📊 **Fit Statistikalar:**
• Yaxshi moslik: {rasch_model.fit_quality['good_fit']} talaba
• Qabul qilinadigan: {rasch_model.fit_quality['acceptable_fit']} talaba
• Yomon moslik: {rasch_model.fit_quality['poor_fit']} talaba
• Umumiy moslik foizi: {rasch_model.fit_quality['fit_percentage']:.1f}%

📈 **Statistik Ma'lumotlar:**
• Jami talabalar: {rasch_model.n_students}
• Jami savollar: {rasch_model.n_items}
• O'rtacha qobiliyat: {np.mean(rasch_model.theta):.3f} ± {np.std(rasch_model.theta):.3f}
• O'rtacha item qiyinligi: {np.mean(rasch_model.beta):.3f} ± {np.std(rasch_model.beta):.3f}

🔍 **Tahlil Natijalari:**
• Infit o'rtacha: {np.mean(rasch_model.infit_stats):.3f}
• Outfit o'rtacha: {np.mean(rasch_model.outfit_stats):.3f}
• Infit standart og'ish: {np.std(rasch_model.infit_stats):.3f}
• Outfit standart og'ish: {np.std(rasch_model.outfit_stats):.3f}

✅ **BBA Standartlariga Moslik:**
"""
        
        # BBA standartlarini tekshirish
        if rasch_model.fit_quality['fit_percentage'] >= 80:
            report += "• ✅ Fit sifatini baholash: Yaxshi\n"
        elif rasch_model.fit_quality['fit_percentage'] >= 70:
            report += "• ⚠️ Fit sifatini baholash: Qabul qilinadigan\n"
        else:
            report += "• ❌ Fit sifatini baholash: Yomon\n"
        
        if np.all((rasch_model.theta >= rasch_model.theta_range[0]) & (rasch_model.theta <= rasch_model.theta_range[1])):
            report += "• ✅ Qobiliyat oralig'i: BBA standartlariga mos\n"
        else:
            report += "• ⚠️ Qobiliyat oralig'i: BBA standartlaridan tashqari\n"
        
        if np.all((rasch_model.beta >= rasch_model.beta_range[0]) & (rasch_model.beta <= rasch_model.beta_range[1])):
            report += "• ✅ Item qiyinligi oralig'i: BBA standartlariga mos\n"
        else:
            report += "• ⚠️ Item qiyinligi oralig'i: BBA standartlaridan tashqari\n"
        
        return report
        
    except Exception as e:
        print(f"BBA hisoboti xatosi: {e}")
        return "Hisobot yaratishda xatolik yuz berdi."
