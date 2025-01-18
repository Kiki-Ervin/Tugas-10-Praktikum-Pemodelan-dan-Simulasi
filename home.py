import matplotlib.pyplot as plt
from io import BytesIO
import base64
import math
from flask import Flask, render_template, request, session

app = Flask(__name__)

app.secret_key = 'your_secret_key'


@app.route('/')
def home_page():
    # Mengarahkan ke home.html saat aplikasi pertama kali dijalankan
    return render_template('home.html')

@app.route('/home')
def home_content():
    return """
    <div id="content-area">
    <p style="font-size: 18px; text-align: justify;">
        <h2>Pengenalan Distribusi Binomial</h2>
        <p>
            Distribusi probabilitas binomial adalah distribusi diskrit yang digunakan untuk memodelkan 
            jumlah keberhasilan dalam <span class="formula">n</span> percobaan independen, di mana setiap 
            percobaan memiliki dua hasil (berhasil atau gagal). 
            Probabilitas keberhasilan untuk setiap 
            percobaan adalah <span class="formula">p</span>, dan probabilitas kegagalan adalah 
            <span class="formula">1 − p</span>.
        </p>
        <p>Rumus utama untuk distribusi binomial:</p>
        <div class="formula">
            P(X = k) = C(n, k) × p<sup>k</sup> × (1 - p)<sup>n - k</sup>
        </div>
        <p>Di mana:</p>
        <ul>
            <li><strong>P(X = k)</strong> : Probabilitas mendapatkan <em>k</em> keberhasilan.</li>
            <li><strong>n</strong> : Jumlah total percobaan.</li>
            <li><strong>k</strong> : Jumlah keberhasilan yang diinginkan.</li>
            <li><strong>p</strong> : Probabilitas keberhasilan pada setiap percobaan.</li>
            <li><strong>(1 - p)</strong> : Probabilitas kegagalan pada setiap percobaan.</li>
            <li><strong>C(n, k)</strong> : Kombinasi, dihitung sebagai <em>n!</em> / (<em>k!(n - k)!</em>).</li>
        </ul>
    </p><strong>Studi Kasus :</strong></p>
    <p>Dalam sebuah kota besar, terdapat 50 driver ojek online yang aktif dalam satu jam. Berdasarkan data historis, probabilitas seorang driver mendapatkan setidaknya satu order dalam satu jam adalah 60% (<span class="parameter">p = 0.6</span>). Manajemen ingin mengetahui peluang bahwa setidaknya 30 driver mendapatkan order dalam satu jam.</p>

</p><strong>Parameter:</strong></p>
<ul>
    <li><span class="parameter">Jumlah percobaan(n)</span>     : 50 (jumlah driver yang aktif)</li>
    <li><span class="parameter">Probabilitas keberhasilan (p)</span> : 0.6 (kemungkinan seorang driver mendapatkan order)</li>
    <li><span class="parameter">Jumlah keberhasilan (k)</span>    : 30 (setidaknya 30 driver mendapatkan order)</li>
</ul>
</div>
    """

@app.route('/reset', methods=['POST'])
def reset():
    return render_template('index.html', n=0, p=0, k=0, result=None, error=None, steps=None)


@app.route('/probabilitas_binomial')
def prob_binomial():
    # Pastikan data yang diperlukan seperti n, p, dan k di-passing sesuai kebutuhan
    return render_template('index.html', n=0, p=0, k=0, result=None, error=None, steps=None)


#new
@app.route('/hitung_probabilitas', methods=['POST'])
def hitung_probabilitas():
    result = None
    steps = []
    error = None
    n = p = k = 0
    data_probabilitas = []  # Variabel untuk menyimpan hasil probabilitas

    if request.method == 'POST':
        try:
            # Mengambil nilai dari form input
            n = int(request.form['n'])
            p = float(request.form['p'])
            k = int(request.form['k'])

            # Validasi input
            if n < 0 or k < 0:
                raise ValueError("Nilai n dan k tidak boleh negatif.")
            if p < 0 or p > 1:
                raise ValueError("Probabilitas (p) harus berada di antara 0 dan 1.")
            if k > n:
                raise ValueError("Jumlah keberhasilan (k) tidak boleh lebih dari jumlah percobaan (n).")

            cumulative_prob = 0

            # Menghitung probabilitas untuk setiap nilai i dari 0 sampai k
            for i in range(k + 1):
                comb_value = math.factorial(n) / (math.factorial(i) * math.factorial(n - i))
                probability = comb_value * math.pow(p, i) * math.pow(1 - p, n - i)
                data_probabilitas.append(probability)  # Menyimpan probabilitas per i

                # Menambahkan langkah-langkah perhitungan
                steps.append(f"Hitung kombinasi C({n},{i}) = {comb_value:.6f}")
                steps.append(f"Hitung probabilitas P(X={i}) = C({n},{i}) * (p^{i}) * ((1 - p)^(n - {i}))")
                steps.append(f"Hasil probabilitas P(X={i}) = {probability:.6f}")

                # Menambahkan ke probabilitas kumulatif
                cumulative_prob += probability

            # Menambahkan langkah akhir
            steps.append("Jumlahkan semua probabilitas untuk mendapatkan probabilitas kumulatif.")
            result = f"Probabilitas kumulatif: P(X ≤ {k}) = {cumulative_prob:.6f}"

            # Menyimpan hasil ke dalam session
            session['data_probabilitas'] = data_probabilitas
            session['n'] = n
            session['p'] = p
            session['k'] = k

        except ValueError as ve:
            error = f"Kesalahan: {ve}"
        except Exception as e:
            error = f"Kesalahan tak terduga: {e}"

    return render_template('index.html', result=result, steps=steps, error=error, n=n, p=p, k=k)



#new
@app.route('/diagram_hasil')
def diagram_hasil():
    try:
        # Ambil data dari session
        data_probabilitas = session.get('data_probabilitas', [])
        n = session.get('n', 0)
        p = session.get('p', 0)
        k = session.get('k', 0)

        if not data_probabilitas:
            return "Tidak ada data probabilitas yang tersedia. Silakan hitung probabilitas terlebih dahulu."

        # Membuat diagram batang
        x_values = list(range(len(data_probabilitas)))

        # Membuat diagram batang
        plt.figure(figsize=(10, 5))
        plt.bar(x_values, data_probabilitas, color='skyblue')

        # Menambahkan garis putus-putus merah untuk menyoroti nilai k
        if k >= 0 and k < len(data_probabilitas):  # Pastikan k berada dalam rentang yang valid
            plt.axvline(x=k, color='red', linestyle='--', label=f'k={k}')

        plt.title(f"Diagram Probabilitas Binomial (n={n}, p={p})")
        plt.xlabel("Keberhasilan (k)")
        plt.ylabel("Probabilitas")
        plt.xticks(x_values)
        plt.legend()

        # Simpan diagram sebagai gambar
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        diagram_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Kirim gambar ke template
        return render_template('diagram_hasil.html', diagram_data=diagram_data)
    except Exception as e:
        return f"Kesalahan: {e}"


@app.route('/about_me')
def about_me_content():
    return """
    <p style="font-size: 18px; text-align: justify;"> <strong> Nama : </strong> Kiki Ervin </p>
    <strong> NIM : </strong> 301220053 <p
    </p> <strong> Kelas : </strong> 5A(Teknik Informatika) <p
    </P>
    <strong> Studi Kasus : </strong> Analisis Peluang Driver Ojol Mendapatkan Order
Menggunakan Distribusi Binomial

 """


if __name__ == '__main__':
    app.run(debug=True)
