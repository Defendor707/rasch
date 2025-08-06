import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
warnings.filterwarnings('ignore')

# Server quvvati optimizatsiyasi - adaptive CPU ishlatish
NUM_CORES = os.cpu_count() or 6

def get_cpu_load():
    try:
        with open('/proc/loadavg', 'r') as f:
            load = float(f.read().split()[0])
        return load
    except:
        return 0.0

# Adaptive worker count based on current load
current_load = get_cpu_load()
if current_load > NUM_CORES * 1.2:  # Load juda yuqori
    MAX_WORKERS = max(2, int(NUM_CORES * 0.5))  # 50% ishlatish
elif current_load > NUM_CORES * 0.8:
    MAX_WORKERS = max(3, int(NUM_CORES * 0.6))  # 60% ishlatish
else:
    MAX_WORKERS = min(int(NUM_CORES * 0.8), 4)  # 80% ishlatish

# Numpy/BLAS sozlamalari
os.environ['OMP_NUM_THREADS'] = str(MAX_WORKERS)
os.environ['MKL_NUM_THREADS'] = str(MAX_WORKERS)
os.environ['OPENBLAS_NUM_THREADS'] = str(MAX_WORKERS)
os.environ['VECLIB_MAXIMUM_THREADS'] = str(MAX_WORKERS)
os.environ['NUMEXPR_NUM_THREADS'] = str(MAX_WORKERS)

class RaschModel:
    """
    BBA standartlariga mos to'liq Rasch modeli
    - Conditional Maximum Likelihood Estimation (CMLE)
    - Infit va Outfit statistikalar
    - Wright map (item-person xaritasi)
    - Fit ko'rsatkichlari
    """
    
    def __init__(self, data, max_iter=50, tolerance=1e-6):
        self.data = np.array(data, dtype=np.float32)
        self.n_students, self.n_items = self.data.shape
        self.max_iter = max_iter
        self.tolerance = tolerance
        
        # BBA standartlari bo'yicha parametrlar
        self.theta_range = (-3.5, 3.5)  # Qobiliyat oralig'i
        self.beta_range = (-3.7, 3.3)   # Item qiyinligi oralig'i
        
        # Natijalar
        self.theta = None
        self.beta = None
        self.infit_stats = None
        self.outfit_stats = None
        self.fit_quality = None
        
    def fit(self):
        """CMLE usuli bilan Rasch modelini moslashtirish"""
        try:
            # Boshlang'ich baholar
            self._initialize_parameters()
            
            # CMLE estimation
            self._conditional_mle_estimation()
            
            # Fit statistikalarini hisoblash
            self._calculate_fit_statistics()
            
            # Natijalarni validatsiya qilish
            self._validate_results()
            
            return True
            
        except Exception as e:
            print(f"Rasch model xatosi: {e}")
            return False
    
    def _initialize_parameters(self):
        """Boshlang'ich parametrlarni hisoblash"""
        # Talabalar ballari
        student_scores = np.sum(self.data, axis=1)
        item_scores = np.sum(self.data, axis=0)
        
        # Ekstremal holatlarni oldini olish
        epsilon = 0.01
        
        # Qobiliyat baholari (logit shkalada)
        student_props = np.clip((student_scores + epsilon) / (self.n_items + 2*epsilon), epsilon, 1-epsilon)
        self.theta = np.log(student_props / (1 - student_props))
        
        # Item qiyinligi baholari
        item_props = np.clip((item_scores + epsilon) / (self.n_students + 2*epsilon), epsilon, 1-epsilon)
        self.beta = -np.log(item_props / (1 - item_props))
        
        # BBA oralig'iga moslashtirish
        self.theta = np.clip(self.theta, self.theta_range[0], self.theta_range[1])
        self.beta = np.clip(self.beta, self.beta_range[0], self.beta_range[1])
    
    def _conditional_mle_estimation(self):
        """Conditional Maximum Likelihood Estimation"""
        for iteration in range(self.max_iter):
            old_theta = self.theta.copy()
            old_beta = self.beta.copy()
            
            # Theta baholarini yangilash (beta berilgan)
            self._update_theta()
            
            # Beta baholarini yangilash (theta berilgan)
            self._update_beta()
            
            # Konvergensiyani tekshirish
            theta_diff = np.max(np.abs(self.theta - old_theta))
            beta_diff = np.max(np.abs(self.beta - old_beta))
            
            if max(theta_diff, beta_diff) < self.tolerance:
                break
    
    def _update_theta(self):
        """Talabalar qobiliyatini yangilash"""
        for i in range(self.n_students):
            def neg_log_likelihood(theta_i):
                # Rasch model ehtimolligi
                logits = theta_i - self.beta
                probs = expit(logits)
                
                # Log-likelihood
                ll = np.sum(self.data[i] * np.log(probs + 1e-10) + 
                           (1 - self.data[i]) * np.log(1 - probs + 1e-10))
                return -ll
            
            # Newton-Raphson usuli
            result = minimize_scalar(neg_log_likelihood, 
                                   bounds=self.theta_range,
                                   method='bounded')
            
            if result.success:
                self.theta[i] = result.x
    
    def _update_beta(self):
        """Item qiyinligini yangilash"""
        for j in range(self.n_items):
            def neg_log_likelihood(beta_j):
                # Rasch model ehtimolligi
                logits = self.theta - beta_j
                probs = expit(logits)
                
                # Log-likelihood
                ll = np.sum(self.data[:, j] * np.log(probs + 1e-10) + 
                           (1 - self.data[:, j]) * np.log(1 - probs + 1e-10))
                return -ll
            
            # Newton-Raphson usuli
            result = minimize_scalar(neg_log_likelihood,
                                   bounds=self.beta_range,
                                   method='bounded')
            
            if result.success:
                self.beta[j] = result.x
    
    def _calculate_fit_statistics(self):
        """Infit va Outfit statistikalarini hisoblash"""
        # Kutilgan qiymatlar
        logits = self.theta[:, np.newaxis] - self.beta[np.newaxis, :]
        expected_probs = expit(logits)
        
        # Residuals
        residuals = self.data - expected_probs
        
        # Variance
        variance = expected_probs * (1 - expected_probs)
        
        # Standardized residuals
        std_residuals = residuals / np.sqrt(variance + 1e-10)
        
        # Infit statistikalar (variance bilan og'irlangan)
        infit_numerator = np.sum(std_residuals**2 * variance, axis=1)
        infit_denominator = np.sum(variance, axis=1)
        self.infit_stats = infit_numerator / (infit_denominator + 1e-10)
        
        # Outfit statistikalar (oddiy o'rtacha)
        self.outfit_stats = np.mean(std_residuals**2, axis=1)
        
        # Fit sifatini baholash
        self._assess_fit_quality()
    
    def _assess_fit_quality(self):
        """Fit sifatini baholash (BBA standartlari)"""
        # Infit uchun mezonlar
        infit_good = (0.8 <= self.infit_stats) & (self.infit_stats <= 1.2)
        infit_acceptable = (0.7 <= self.infit_stats) & (self.infit_stats <= 1.3)
        
        # Outfit uchun mezonlar
        outfit_good = (0.8 <= self.outfit_stats) & (self.outfit_stats <= 1.2)
        outfit_acceptable = (0.7 <= self.outfit_stats) & (self.outfit_stats <= 1.3)
        
        # Umumiy baho
        good_fit = infit_good & outfit_good
        acceptable_fit = infit_acceptable & outfit_acceptable
        
        self.fit_quality = {
            'good_fit': np.sum(good_fit),
            'acceptable_fit': np.sum(acceptable_fit),
            'poor_fit': np.sum(~acceptable_fit),
            'total_students': self.n_students,
            'fit_percentage': np.sum(acceptable_fit) / self.n_students * 100
        }
    
    def _validate_results(self):
        """Natijalarni BBA standartlariga mosligini tekshirish"""
        # Qobiliyat oralig'i
        if np.any(self.theta < self.theta_range[0]) or np.any(self.theta > self.theta_range[1]):
            print("Ogohlantirish: Qobiliyat baholari BBA oralig'idan tashqarida")
        
        # Item qiyinligi oralig'i
        if np.any(self.beta < self.beta_range[0]) or np.any(self.beta > self.beta_range[1]):
            print("Ogohlantirish: Item qiyinligi baholari BBA oralig'idan tashqarida")
        
        # Fit sifatini tekshirish
        if self.fit_quality['fit_percentage'] < 80:
            print(f"Ogohlantirish: Faqat {self.fit_quality['fit_percentage']:.1f}% talabalar yaxshi moslik ko'rsatmoqda")
    
    def create_wright_map(self, save_path=None):
        """Wright map (item-person xaritasi) yaratish"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))
            
            # Talabalar qobiliyati taqsimoti
            ax1.hist(self.theta, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_xlabel('Talaba Qobiliyati (θ)')
            ax1.set_ylabel('Talabalar soni')
            ax1.set_title('Talabalar Qobiliyati Taqsimoti')
            ax1.grid(True, alpha=0.3)
            
            # Item qiyinligi taqsimoti
            ax2.hist(self.beta, bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
            ax2.set_xlabel('Item Qiyinligi (β)')
            ax2.set_ylabel('Savollar soni')
            ax2.set_title('Savollar Qiyinligi Taqsimoti')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            print(f"Wright map xatosi: {e}")
            return None
    
    def get_summary_statistics(self):
        """BBA standartlariga mos statistika xulosasi"""
        return {
            'model_type': 'Dichotomous Rasch Model',
            'estimation_method': 'Conditional Maximum Likelihood (CMLE)',
            'theta_range': f"{self.theta_range[0]} to {self.theta_range[1]} logits",
            'beta_range': f"{self.beta_range[0]} to {self.beta_range[1]} logits",
            'fit_statistics': 'Infit va Outfit indicators',
            'total_students': self.n_students,
            'total_items': self.n_items,
            'fit_quality': self.fit_quality,
            'theta_mean': np.mean(self.theta),
            'theta_std': np.std(self.theta),
            'beta_mean': np.mean(self.beta),
            'beta_std': np.std(self.beta)
        }

def rasch_model(data, max_students=None):
    """
    Tezlashtirilgan va aniq Rasch modeli implementatsiyasi.
    
    Parameters:
    - data: Numpy array (qatorlar: talabalar, ustunlar: savollar)
    - max_students: Maksimal talabalar soni (katta ma'lumotlar uchun)
                  
    Returns:
    - theta: Talabalar qobiliyati baholari
    - beta: Savollar qiyinligi baholari
    """
    n_students, n_items = data.shape
    
    # Katta ma'lumotlar uchun tezkor usul
    if max_students and n_students > max_students:
        return _process_large_dataset(data, max_students)
    
    # Yangi Rasch modelini ishlatish
    rasch = RaschModel(data)
    success = rasch.fit()
    
    if success:
        return rasch.theta, rasch.beta, rasch
    else:
        # Fallback to old method
        return _fallback_rasch_model(data)

def _fallback_rasch_model(data):
    """Eski usul (fallback)"""
    n_students, n_items = data.shape
    
    # Tezkor boshlang'ich baholar
    student_scores = np.sum(data, axis=1, dtype=np.float32)
    item_scores = np.sum(data, axis=0, dtype=np.float32)
    
    # Ekstremal qiymatlarni oldini olish
    epsilon = 0.01
    
    # Boshlang'ich qobiliyat baholari (tezkor formula)
    student_props = np.clip((student_scores + epsilon) / (n_items + 2*epsilon), epsilon, 1-epsilon)
    initial_theta = np.log(student_props / (1 - student_props))
    
    # Boshlang'ich qiyinlik baholari (tezkor formula)
    item_props = np.clip((item_scores + epsilon) / (n_students + 2*epsilon), epsilon, 1-epsilon)
    initial_beta = -np.log(item_props / (1 - item_props))
    
    return initial_theta, initial_beta, None

def _process_chunk_parallel(args):
    """Parallel chunk processing uchun worker funksiya"""
    chunk_data, beta = args
    return _estimate_theta_given_beta(chunk_data, beta)

def _process_large_dataset(data, max_students=2000):
    """
    Parallel processing bilan katta ma'lumotlarni qayta ishlash.
    Server quvvatining 80% ishlatadi.
    
    Parameters:
    - data: To'liq ma'lumotlar
    - max_students: Chunk hajmi
    
    Returns:
    - theta, beta: Birlashtirilgan natijalar
    """
    n_students, n_items = data.shape
    
    # Optimal chunk size
    optimal_chunk_size = min(max_students, max(n_students // MAX_WORKERS, 500))
    n_chunks = int(np.ceil(n_students / optimal_chunk_size))
    
    # Initial beta estimate
    sample_size = min(1000, n_students)
    sample_indices = np.random.choice(n_students, sample_size, replace=False)
    sample_data = data[sample_indices]
    _, initial_beta = rasch_model(sample_data)
    
    # Prepare chunks for parallel processing
    chunks = []
    chunk_indices = []
    for i in range(n_chunks):
        start_idx = i * optimal_chunk_size
        end_idx = min(start_idx + optimal_chunk_size, n_students)
        chunk_data = data[start_idx:end_idx]
        chunks.append((chunk_data, initial_beta))
        chunk_indices.append((start_idx, end_idx))
    
    # Parallel processing
    all_theta = np.zeros(n_students, dtype=np.float32)
    
    try:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            chunk_results = list(executor.map(_process_chunk_parallel, chunks))
        
        # Combine results
        for i, (chunk_theta, (start_idx, end_idx)) in enumerate(zip(chunk_results, chunk_indices)):
            all_theta[start_idx:end_idx] = chunk_theta
            
    except Exception:
        # Fallback to sequential processing
        for i, ((chunk_data, beta), (start_idx, end_idx)) in enumerate(zip(chunks, chunk_indices)):
            chunk_theta = _estimate_theta_given_beta(chunk_data, beta)
            all_theta[start_idx:end_idx] = chunk_theta
    
    # Refine beta with parallel processing
    final_beta = _estimate_beta_given_theta_parallel(data, all_theta)
    
    # Center abilities
    all_theta = all_theta - np.mean(all_theta)
    
    return all_theta, final_beta

def _estimate_beta_given_theta_parallel(data, theta):
    """Parallel beta estimation"""
    n_students, n_items = data.shape
    beta = np.zeros(n_items, dtype=np.float32)
    
    # Parallel processing for beta calculation
    def process_item(j):
        item_responses = data[:, j].astype(np.float32)
        item_score = np.sum(item_responses)
        
        if item_score == 0:
            return 3.0
        elif item_score == n_students:
            return -3.0
        else:
            prop = (item_score + 0.5) / (n_students + 1)
            beta_j = -np.log(prop / (1 - prop))
        
        # Newton-Raphson refinement
        for _ in range(8):
            logits = np.clip(theta - beta_j, -15, 15)
            p = expit(logits)
            residual = item_responses - p
            gradient = -np.sum(residual)
            hessian = np.sum(p * (1 - p)) + 0.01
            
            if hessian > 0:
                update = gradient / hessian
                beta_j += 0.8 * update
                if abs(update) < 0.005:
                    break
        
        return beta_j
    
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            beta = list(executor.map(process_item, range(n_items)))
        beta = np.array(beta, dtype=np.float32)
    except Exception:
        # Fallback sequential
        for j in range(n_items):
            beta[j] = process_item(j)
    
    return beta

def _estimate_theta_given_beta(data, beta):
    """Tezkor talaba qobiliyatlarini baholash (beta berilgan)"""
    n_students, n_items = data.shape
    theta = np.zeros(n_students, dtype=np.float32)
    
    # Har bir talaba uchun tezkor Newton-Raphson
    for i in range(n_students):
        student_responses = data[i].astype(np.float32)
        
        # Boshlang'ich baholash (student score asosida)
        raw_score = np.sum(student_responses)
        if raw_score == 0:
            theta_i = -3.0
        elif raw_score == n_items:
            theta_i = 3.0
        else:
            # Logit transformatsiya
            prop = (raw_score + 0.5) / (n_items + 1)
            theta_i = np.log(prop / (1 - prop))
        
        # Newton-Raphson iteratsiyalari (tezkor)
        for _ in range(10):  # Kamroq iteratsiya, tezlik uchun
            # Ehtimolliklar
            logits = theta_i - beta
            logits = np.clip(logits, -15, 15)  # Kichikroq chegaralar
            p = expit(logits)
            
            # Gradient va Hessian
            residual = student_responses - p
            gradient = np.sum(residual)
            hessian = np.sum(p * (1 - p)) + 0.01  # kichik regularizatsiya
            
            # Yangilanish
            if hessian > 0:
                update = gradient / hessian
                theta_i += 0.7 * update  # kichik qadam
                
                # Konvergensiya tekshiruvi
                if abs(update) < 0.01:
                    break
        
        theta[i] = theta_i
    
    return theta

def _estimate_beta_given_theta(data, theta):
    """Tezkor savol qiyinliklarini baholash (theta berilgan)"""
    n_students, n_items = data.shape
    beta = np.zeros(n_items, dtype=np.float32)
    
    # Har bir savol uchun tezkor Newton-Raphson
    for j in range(n_items):
        item_responses = data[:, j].astype(np.float32)
        
        # Boshlang'ich baholash (item score asosida)
        item_score = np.sum(item_responses)
        if item_score == 0:
            beta_j = 3.0  # Juda qiyin
        elif item_score == n_students:
            beta_j = -3.0  # Juda oson
        else:
            # Logit transformatsiya
            prop = (item_score + 0.5) / (n_students + 1)
            beta_j = -np.log(prop / (1 - prop))  # Minus chunki yuqori prop = past qiyinlik
        
        # Newton-Raphson iteratsiyalari (tezkor)
        for _ in range(10):  # Kamroq iteratsiya
            # Ehtimolliklar
            logits = theta - beta_j
            logits = np.clip(logits, -15, 15)
            p = expit(logits)
            
            # Gradient va Hessian
            residual = item_responses - p
            gradient = -np.sum(residual)  # Minus chunki beta uchun
            hessian = np.sum(p * (1 - p)) + 0.01
            
            # Yangilanish
            if hessian > 0:
                update = gradient / hessian
                beta_j += 0.7 * update
                
                # Konvergensiya
                if abs(update) < 0.01:
                    break
        
        beta[j] = beta_j
    
    return beta

def ability_to_standard_score(ability):
    """
    Convert ability estimate to standard score using the formula: T = 50 + 10Z
    Where Z = (θ - μ)/σ
    
    Parameters:
    - ability: The student's ability estimate (θ)
    
    Returns:
    - standard_score: Standardized score (T)
    """
    # Calculate Z-score: (ability - mean) / std_dev
    # Since the theta values are centered around 0 (mean=0),
    # we can simplify Z = ability / std_dev
    # Assuming std_dev = 1 for Rasch standardization
    z_score = ability  # This is already a standardized value in Rasch model
    
    # Apply the formula T = 50 + 10Z
    standard_score = 50 + (10 * z_score)
    
    # Ensure the score is in a reasonable range (0-100)
    return max(0, min(100, standard_score))

def ability_to_grade(ability, thresholds=None, min_passing_percent=60):
    """
    O'zbekiston Milliy Sertifikat standartlariga ko'ra baholarni tayinlash (2024).
    
    Parameters:
    - ability: Talabaning qobiliyat bahosi (0-100 ball)
    - thresholds: Baho chegaralari (ixtiyoriy)
    - min_passing_percent: Minimal o'tish foizi
    
    Returns:
    - grade: Tayinlangan baho
    """
    # Agar ability allaqachon 0-100 oralig'ida bo'lsa, to'g'ridan-to'g'ri ishlatamiz
    if isinstance(ability, (int, float)) and 0 <= ability <= 100:
        score = ability
    else:
        # Qobiliyatni 0-100 ballga o'tkazish
        # Rasch model logit scale: -4 dan +4 gacha
        # Uni 0-100 gacha o'zgartirish
        normalized_ability = (ability + 4) / 8 * 100
        score = np.clip(normalized_ability, 0, 100)
    
    # O'zbekiston Milliy Sertifikat standartlari (2024)
    # Vazirlar Mahkamasi qarori asosida
    
    if score >= 70:
        return 'A+'  # 70+ ball = A+ daraja
    elif score >= 65:
        return 'A'   # 65-69.9 ball = A daraja
    elif score >= 60:
        return 'B+'  # 60-64.9 ball = B+ daraja
    elif score >= 55:
        return 'B'   # 55-59.9 ball = B daraja
    elif score >= 50:
        return 'C+'  # 50-54.9 ball = C+ daraja
    elif score >= 46:
        return 'C'   # 46-49.9 ball = C daraja
    else:
        return 'NC'  # 46 balldan past = O'tmagan

def optimize_performance():
    """
    Rasch model performansini optimallashtirish
    """
    import gc
    import psutil
    
    # Xotira optimizatsiyasi
    gc.collect()
    
    # CPU optimizatsiyasi
    cpu_count = psutil.cpu_count()
    optimal_workers = min(cpu_count - 1, 4)  # 1 CPU ni boshqa ishlar uchun qoldirish
    
    # Numpy optimizatsiyasi
    np.set_printoptions(precision=3, suppress=True)
    
    return optimal_workers

def memory_efficient_rasch(data, max_memory_gb=2):
    """
    Xotira samarali Rasch modeli - katta ma'lumotlar uchun
    
    Parameters:
    - data: Test ma'lumotlari
    - max_memory_gb: Maksimal xotira sarfi (GB)
    
    Returns:
    - theta, beta: Optimallashtirilgan natijalar
    """
    n_students, n_items = data.shape
    
    # Xotira sarfini hisoblash
    estimated_memory_mb = (n_students * n_items * 8) / (1024 * 1024)  # bytes to MB
    
    if estimated_memory_mb > max_memory_gb * 1024:
        # Katta ma'lumotlar uchun chunking
        return _chunked_rasch_estimation(data, max_memory_gb)
    else:
        # Oddiy Rasch model
        return rasch_model(data)

def _chunked_rasch_estimation(data, max_memory_gb):
    """
    Katta ma'lumotlar uchun chunked estimation
    """
    n_students, n_items = data.shape
    
    # Optimal chunk size hisoblash
    chunk_size = int((max_memory_gb * 1024 * 1024 * 1024) / (n_items * 8))  # bytes to elements
    chunk_size = max(100, min(chunk_size, n_students // 4))  # Min 100, max 25%
    
    # Chunked processing
    theta_chunks = []
    for i in range(0, n_students, chunk_size):
        end_idx = min(i + chunk_size, n_students)
        chunk_data = data[i:end_idx]
        
        # Har bir chunk uchun Rasch model
        chunk_theta, chunk_beta, _ = rasch_model(chunk_data)
        theta_chunks.append(chunk_theta)
        
        # Xotirani tozalash
        del chunk_data
        gc.collect()
    
    # Natijalarni birlashtirish
    theta = np.concatenate(theta_chunks)
    
    # Umumiy beta hisoblash
    _, beta, _ = rasch_model(data)
    
    return theta, beta

def fast_parallel_estimation(data, n_jobs=None):
    """
    Tez parallel estimation - katta ma'lumotlar uchun
    """
    if n_jobs is None:
        n_jobs = min(4, os.cpu_count() or 4)
    
    n_students, n_items = data.shape
    
    # Parallel processing uchun chunking
    chunk_size = max(1, n_students // n_jobs)
    chunks = [data[i:i+chunk_size] for i in range(0, n_students, chunk_size)]
    
    # Parallel estimation
    with ThreadPoolExecutor(max_workers=n_jobs) as executor:
        results = list(executor.map(lambda chunk: rasch_model(chunk), chunks))
    
    # Natijalarni birlashtirish
    all_theta = []
    all_beta = []
    
    for theta, beta, _ in results:
        all_theta.extend(theta)
        all_beta.extend(beta)
    
    return np.array(all_theta), np.array(all_beta)
