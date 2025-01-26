import streamlit as st
import pickle
import numpy as np

# Load model dan scaler
with open('logistic_model.pkl', 'rb') as f:
    model = pickle.load(f)
    
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

def get_insight_rekomendasi(prediction, bmi, lifestyle_data):
    insight = []
    rekomendasi = []
    
    # Hitung BMI 
    height_m = float(lifestyle_data['Height'])
    weight_kg = float(lifestyle_data['Weight'])
    bmi = weight_kg / (height_m * height_m)
    
    # Insight dan rekomendasi berdasarkan kategori obesitas
    if prediction == "Insufficient Weight":
        insight.extend([
            "Berat badan Anda berada di bawah normal",
            f"BMI Anda adalah {bmi:.1f} (Normal: 18.5-24.9)",
            "Kekurangan berat badan dapat mempengaruhi sistem kekebalan tubuh"
        ])
        rekomendasi.extend([
            "Tingkatkan asupan kalori harian dengan makanan bergizi",
            "Konsumsi protein berkualitas tinggi",
            "Lakukan latihan kekuatan untuk membangun massa otot"
        ])
    
    elif prediction == "Normal Weight":
        insight.extend([
            "Berat badan anda ideal",
            f"BMI Anda adalah {bmi:.1f} (Normal: 18.5-24.9)",
            "Pertahankan pola hidup sehat Anda"
        ])
        rekomendasi.extend([
            "Jaga pola makan seimbang",
            "Tetap aktif dengan olahraga rutin",
            "Pertahankan konsumsi air yang cukup"
        ])
    
    elif "Overweight" in prediction or "Obesity" in prediction:
        insight.extend([
            f"BMI Anda adalah {bmi:.1f} (Normal: 18.5-24.9)",
            "Kelebihan berat badan dapat meningkatkan risiko penyakit kardiovaskular",
            "Pola hidup dan pola makan mempengaruhi berat badan Anda"
        ])
        rekomendasi.extend([
            "Kurangi konsumsi makanan tinggi kalori dan lemak",
            "Tingkatkan aktivitas fisik minimal 30 menit per hari",
            "Konsultasikan dengan ahli gizi untuk program penurunan berat badan"
        ])
    
    # insight berdasarkan gaya hidup
    if float(lifestyle_data['FCVC']) < 2:
        rekomendasi.append("Tingkatkan konsumsi sayur dan buah")
    
    if float(lifestyle_data['CH2O']) < 2:
        rekomendasi.append("Tingkatkan konsumsi air putih (minimal 2L per hari)")
    
    if float(lifestyle_data['FAF']) < 2:
        rekomendasi.append("Tingkatkan frekuensi aktivitas fisik")
    
    if lifestyle_data['SMOKE'] == 'yes':
        insight.append("Merokok dapat mempengaruhi metabolisme tubuh")
        rekomendasi.append("Pertimbangkan untuk berhenti merokok")
    
    if float(lifestyle_data['TUE']) > 1:
        rekomendasi.append("Kurangi waktu penggunaan teknologi dan tingkatkan aktivitas fisik")
    
    return insight, rekomendasi

def main():
    st.title('Prediksi Tingkat Obesitas')
    
    # Form input
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox('Jenis Kelamin', ['Male', 'Female'], format_func=lambda x: 'Laki-laki' if x == 'Male' else 'Perempuan')
            age = st.number_input('Usia', min_value=0, step=1)
            height = st.number_input('Tinggi Badan (meter)', min_value=0.0, step=0.01, format="%.2f")
            weight = st.number_input('Berat Badan (kg)', min_value=0.0, step=0.1)
            family_history = st.selectbox('Apakah ada anggota keluarga yang mengalami obesitas?', ['yes', 'no'], format_func=lambda x: 'Ya' if x == 'yes' else 'Tidak')
            favc = st.selectbox('Apakah Anda sering mengonsumsi makanan tinggi kalori?', ['yes', 'no'], format_func=lambda x: 'Ya' if x == 'yes' else 'Tidak')
            fcvc = st.number_input('Seberapa sering Anda mengonsumsi sayuran? (1-3)', min_value=1, max_value=3, step=1)
            ncp = st.number_input('Berapa kali makan dalam sehari?', min_value=1, max_value=4, step=1)
        
        with col2:
            caec = st.selectbox('Apakah Anda makan lagi di antara waktu makan anda?', 
                              ['Sometimes', 'Always', 'Never'],
                              format_func=lambda x: 'Kadang-kadang' if x == 'Sometimes' else ('Selalu' if x == 'Always' else 'Tidak Pernah'))
            smoke = st.selectbox('Apakah Anda merokok?', ['yes', 'no'], format_func=lambda x: 'Ya' if x == 'yes' else 'Tidak')
            ch2o = st.number_input('Berapa liter air yang Anda minum per hari?', min_value=1.0, max_value=3.0, step=0.1)
            scc = st.selectbox('Apakah Anda memantau kalori harian?', ['yes', 'no'], format_func=lambda x: 'Ya' if x == 'yes' else 'Tidak')
            faf = st.number_input('Berapa hari dalam seminggu Anda berolahraga?', min_value=0, max_value=7, step=1)
            tue = st.number_input('Berapa jam per hari Anda menggunakan perangkat elektronik?', min_value=0, max_value=24, step=1)
            calc = st.selectbox('Seberapa sering Anda mengonsumsi alkohol?',
                              ['Sometimes', 'Always', 'Never'],
                              format_func=lambda x: 'Kadang-kadang' if x == 'Sometimes' else ('Selalu' if x == 'Always' else 'Tidak Pernah'))
            mtrans = st.selectbox('Transportasi yang biasa Anda gunakan?',
                                ['Public_Transportation', 'Walking', 'Automobile', 'Motorbike', 'Bike'],
                                format_func=lambda x: {
                                    'Public_Transportation': 'Transportasi Umum',
                                    'Walking': 'Jalan Kaki',
                                    'Automobile': 'Mobil',
                                    'Motorbike': 'Motor',
                                    'Bike': 'Sepeda'
                                }[x])

        submitted = st.form_submit_button("Prediksi Obesitas")

    if submitted:
        try:
            # Kumpulkan data
            data = {
                'Gender': gender,
                'Age': age,
                'Height': height,
                'Weight': weight,
                'family_history': family_history,
                'FAVC': favc,
                'FCVC': fcvc,
                'NCP': ncp,
                'CAEC': caec,
                'SMOKE': smoke,
                'CH2O': ch2o,
                'SCC': scc,
                'FAF': faf,
                'TUE': tue,
                'CALC': calc,
                'MTRANS': mtrans
            }

            # Ekstrak fitur
            features = [
                float(data['Gender'] == 'Male'),
                float(data['Age']),
                float(data['Height']),
                float(data['Weight']),
                float(data['family_history'] == 'yes'),
                float(data['FAVC'] == 'yes'),
                float(data['FCVC']),
                float(data['NCP']),
                float(data['CAEC'] == 'Always'),
                float(data['SMOKE'] == 'yes'),
                float(data['CH2O']),
                float(data['SCC'] == 'yes'),
                float(data['FAF']),
                float(data['TUE']),
                float(data['CALC'] == 'Always'),
                float(data['MTRANS'] == 'Public_Transportation')
            ]

            # Reshape dan transformasi fitur
            features = np.array(features).reshape(1, -1)
            features_scaled = scaler.transform(features)

            # Prediksi
            prediction = model.predict(features_scaled)

            # Mapping hasil prediksi
            obesity_levels = {
                0: "Insufficient Weight",
                1: "Normal Weight", 
                2: "Overweight Level I",
                3: "Overweight Level II",
                4: "Obesity Type I",
                5: "Obesity Type II",
                6: "Obesity Type III"
            }

            prediksi = obesity_levels[prediction[0]]
            bmi = float(data['Weight']) / (float(data['Height']) * float(data['Height']))

            # Dapatkan insight dan rekomendasi
            insight, rekomendasi = get_insight_rekomendasi(prediksi, bmi, data)

            # Tampilkan hasil
            st.success(f"Prediksi Kategori: {prediksi}")
            st.info(f"BMI: {bmi:.1f}")

            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Insight")
                for ins in insight:
                    st.write("•", ins)

            with col2:
                st.subheader("Rekomendasi")
                for rek in rekomendasi:
                    st.write("•", rek)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == '__main__':
    main() 