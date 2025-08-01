# 🚀 Guida alla Pubblicazione del Portfolio

## 📋 Opzioni Disponibili

### 1. **GitHub Pages (GRATUITO)**
**Vantaggi:** Gratuito, facile da usare, integrato con GitHub
**Svantaggi:** Solo frontend statico (no Flask backend)

#### Come fare:
1. **Crea un repository su GitHub**
2. **Rendi il sito statico** (rimuovi Flask)
3. **Carica i file HTML/CSS/JS**
4. **Attiva GitHub Pages**

#### Modifiche necessarie:
- Rimuovi `app.py` e `models.py`
- Usa solo HTML/CSS/JS
- I progetti diventeranno statici

---

### 2. **Render.com (GRATUITO)**
**Vantaggi:** Supporta Flask, gratuito, facile deployment
**Svantaggi:** Limiti su piano gratuito

#### Come fare:
1. **Crea account su Render.com**
2. **Connetti il repository GitHub**
3. **Configura il deployment automatico**

#### File necessari:
```
requirements.txt
app.py
Procfile (per Render)
```

---

### 3. **Railway.app (GRATUITO)**
**Vantaggi:** Supporta Flask, deployment veloce
**Svantaggi:** Limiti su piano gratuito

#### Come fare:
1. **Crea account su Railway**
2. **Connetti GitHub**
3. **Deploy automatico**

---

### 4. **Heroku (A PAGAMENTO)**
**Vantaggi:** Molto stabile, supporto completo
**Svantaggi:** Non più gratuito

---

## 🛠️ Preparazione per il Deployment

### **Opzione 1: GitHub Pages (Statico)**

#### Passi:
1. **Crea repository su GitHub**
2. **Rendi il sito statico**
3. **Carica i file**
4. **Attiva GitHub Pages**

#### Modifiche necessarie:
- Rimuovi Flask backend
- Converti progetti in JSON statico
- Usa solo HTML/CSS/JS

### **Opzione 2: Render.com (Con Flask)**

#### File da creare:

**1. Procfile:**
```
web: gunicorn app:app
```

**2. Aggiorna requirements.txt:**
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
email-validator==2.2.0
gunicorn==21.2.0
```

**3. Modifica app.py:**
```python
if __name__ == '__main__':
    create_admin()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

---

## 📝 Guida Step-by-Step

### **Per Render.com:**

1. **Crea account su [Render.com](https://render.com)**
2. **Clicca "New Web Service"**
3. **Connetti il tuo repository GitHub**
4. **Configura:**
   - **Name:** portfolio-steven
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. **Clicca "Create Web Service"**

### **Per Railway.app:**

1. **Vai su [Railway.app](https://railway.app)**
2. **Clicca "Start a New Project"**
3. **Seleziona "Deploy from GitHub repo"**
4. **Connetti il repository**
5. **Railway rileverà automaticamente Flask**

---

## 🔧 Configurazioni Necessarie

### **1. Crea Procfile:**
```
web: gunicorn app:app
```

### **2. Aggiorna requirements.txt:**
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
email-validator==2.2.0
gunicorn==21.2.0
Werkzeug==2.3.7
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.3
```

### **3. Modifica app.py:**
```python
if __name__ == '__main__':
    create_admin()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## 🌐 Domini Personalizzati

### **Render.com:**
1. **Vai nelle impostazioni del progetto**
2. **Sezione "Custom Domains"**
3. **Aggiungi il tuo dominio**
4. **Configura DNS**

### **Railway.app:**
1. **Settings del progetto**
2. **Custom Domains**
3. **Aggiungi dominio**

---

## 🔒 Sicurezza

### **Cambia la SECRET_KEY:**
```python
app.secret_key = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-this')
```

### **Cambia password admin:**
```python
admin.set_password('your-super-secure-password')
```

---

## 📊 Monitoraggio

### **Render.com:**
- Logs automatici
- Monitoraggio uptime
- Alert automatici

### **Railway.app:**
- Logs in tempo reale
- Metriche di performance
- Alert configurabili

---

## 💡 Consigli

1. **Inizia con Render.com** - È il più semplice
2. **Testa localmente** prima del deploy
3. **Backup del database** regolarmente
4. **Monitora i log** per errori
5. **Configura domini personalizzati** dopo il deploy

---

## 🆘 Troubleshooting

### **Errori comuni:**
- **Porta non trovata:** Usa `os.environ.get('PORT', 5000)`
- **Database non trovato:** Il database si ricrea automaticamente
- **Moduli mancanti:** Controlla `requirements.txt`

### **Log utili:**
```bash
# Render.com
render logs --service portfolio-steven

# Railway.app
railway logs
``` 