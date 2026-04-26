import numpy as np

# =========================================
# SISTEM FUZZY — TINGKAT RISIKO KEBAKARAN HUTAN
# Metode: Mamdani
# Defuzzifikasi: Centroid
# =========================================

def trimf(x, a, b, c):
    """Fungsi keanggotaan segitiga (triangular)"""
    if x <= a or x >= c:
        return 0.0
    if x <= b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

def trapmf(x, a, b, c, d):
    """Fungsi keanggotaan trapesium (trapezoidal)"""
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (d - x) / (d - c)


# ------------------------------------------
# MEMBERSHIP FUNCTIONS — INPUT
# ------------------------------------------

def mf_suhu(suhu):
    """Suhu udara [20 - 50 °C]"""
    return {
        'rendah': trapmf(suhu, 20, 20, 28, 33),
        'sedang': trimf(suhu, 28, 35, 42),
        'tinggi': trapmf(suhu, 38, 43, 50, 50),
    }

def mf_kelembaban(kel):
    """Kelembaban udara [0 - 100 %]"""
    return {
        'rendah': trapmf(kel, 0, 0, 30, 50),
        'sedang': trimf(kel, 30, 55, 70),
        'tinggi': trapmf(kel, 60, 75, 100, 100),
    }

def mf_angin(angin):
    """Kecepatan angin [0 - 100 km/h]"""
    return {
        'lemah'  : trapmf(angin, 0, 0, 20, 35),
        'sedang' : trimf(angin, 20, 40, 60),
        'kencang': trapmf(angin, 50, 65, 100, 100),
    }

def mf_hujan(hujan):
    """Curah hujan [0 - 100 mm/hari]"""
    return {
        'tidak' : trapmf(hujan, 0, 0, 10, 25),
        'ringan': trimf(hujan, 10, 30, 50),
        'lebat' : trapmf(hujan, 40, 60, 100, 100),
    }


# ------------------------------------------
# ATURAN FUZZY (RULES)
# Operator: AND = min
# ------------------------------------------

def evaluate_rules(s, k, a, h):
    """
    s = nilai MF suhu
    k = nilai MF kelembaban
    a = nilai MF angin
    h = nilai MF curah hujan
    """
    rules = [
        # Format: (bobot, output)
        (min(s['rendah'], k['tinggi'], a['lemah'],   h['lebat']),  'rendah'),
        (min(s['rendah'], k['tinggi'], a['lemah'],   h['ringan']), 'rendah'),
        (min(s['rendah'], k['tinggi'], a['lemah'],   h['tidak']),  'sedang'),
        (min(s['rendah'], k['sedang'], a['lemah'],   h['ringan']), 'sedang'),
        (min(s['sedang'], k['sedang'], a['lemah'],   h['ringan']), 'sedang'),
        (min(s['sedang'], k['sedang'], a['sedang'],  h['tidak']),  'sedang'),
        (min(s['sedang'], k['rendah'], a['sedang'],  h['tidak']),  'tinggi'),
        (min(s['tinggi'], k['rendah'], a['sedang'],  h['tidak']),  'tinggi'),
        (min(s['tinggi'], k['rendah'], a['kencang'], h['tidak']),  'kritis'),
        (min(s['tinggi'], k['rendah'], a['sedang'],  h['ringan']), 'sedang'),
        (min(s['sedang'], k['rendah'], a['kencang'], h['tidak']),  'tinggi'),
        (min(s['tinggi'], k['sedang'], a['kencang'], h['tidak']),  'kritis'),
        (min(s['tinggi'], k['rendah'], a['kencang'], h['ringan']), 'tinggi'),
        (min(s['sedang'], k['rendah'], a['lemah'],   h['tidak']),  'sedang'),
    ]

    # Agregasi: max per output
    agg = {'rendah': 0.0, 'sedang': 0.0, 'tinggi': 0.0, 'kritis': 0.0}
    for bobot, output in rules:
        agg[output] = max(agg[output], bobot)

    return agg


# ------------------------------------------
# DEFUZZIFIKASI — CENTROID
# ------------------------------------------

def defuzzifikasi(agg):
    """
    Menggunakan metode centroid (weighted average)
    dengan nilai representatif tiap output:
      rendah = 12, sedang = 38, tinggi = 63, kritis = 88
    """
    centers = {'rendah': 12, 'sedang': 38, 'tinggi': 63, 'kritis': 88}
    num = sum(agg[k] * centers[k] for k in agg)
    den = sum(agg.values())
    return round(num / den, 2) if den > 0 else 0.0


# ------------------------------------------
# INTERPRETASI HASIL
# ------------------------------------------

def interpretasi(skor):
    if skor < 25:
        return 'RENDAH', 'Kondisi aman, tidak ada ancaman signifikan'
    elif skor < 50:
        return 'SEDANG', 'Waspadai perubahan cuaca, pantau kondisi lapangan'
    elif skor < 72:
        return 'TINGGI', 'Bahaya meningkat, hindari aktivitas pembakaran'
    else:
        return 'KRITIS', 'Siaga penuh! Risiko kebakaran sangat tinggi'


# ------------------------------------------
# FUNGSI UTAMA
# ------------------------------------------

def hitung_risiko(suhu, kelembaban, kecepatan_angin, curah_hujan):
    """
    Parameter:
      suhu            : float, 20-50 (°C)
      kelembaban      : float, 0-100 (%)
      kecepatan_angin : float, 0-100 (km/h)
      curah_hujan     : float, 0-100 (mm/hari)

    Return:
      dict berisi skor, label, deskripsi, dan nilai MF
    """
    s = mf_suhu(suhu)
    k = mf_kelembaban(kelembaban)
    a = mf_angin(kecepatan_angin)
    h = mf_hujan(curah_hujan)

    agg  = evaluate_rules(s, k, a, h)
    skor = defuzzifikasi(agg)
    label, deskripsi = interpretasi(skor)

    return {
        'input': {
            'suhu': suhu,
            'kelembaban': kelembaban,
            'kecepatan_angin': kecepatan_angin,
            'curah_hujan': curah_hujan,
        },
        'membership': {'suhu': s, 'kelembaban': k, 'angin': a, 'hujan': h},
        'agregasi': agg,
        'skor': skor,
        'label': label,
        'deskripsi': deskripsi,
    }


# ------------------------------------------
# CONTOH PENGGUNAAN
# ------------------------------------------

if __name__ == '__main__':
    contoh_kasus = [
        (25, 80, 10, 60),   # Kondisi aman
        (35, 40, 30, 10),   # Sedang
        (42, 20, 55, 5),    # Tinggi
        (47, 15, 75, 2),    # Kritis
    ]

    for suhu, kel, angin, hujan in contoh_kasus:
        hasil = hitung_risiko(suhu, kel, angin, hujan)
        print("=" * 50)
        print(f"INPUT  : Suhu={suhu}°C | Kelembaban={kel}% | Angin={angin}km/h | Hujan={hujan}mm")
        print(f"SKOR   : {hasil['skor']}")
        print(f"RISIKO : {hasil['label']} — {hasil['deskripsi']}")
        print(f"AGREGASI: { {k: round(v,3) for k,v in hasil['agregasi'].items()} }")
