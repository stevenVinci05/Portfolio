# Modifiche al Sistema Progetti

## Panoramica delle Modifiche

Ho modificato il sistema di gestione dei progetti per semplificare l'inserimento dei link e migliorare l'esperienza utente.

### Modifiche Principali

#### 1. **Semplificazione dei Campi Link**
- **Prima**: Due campi separati (`link` per demo e `github` per repository)
- **Ora**: Un solo campo `github_repo` per il repository GitHub

#### 2. **Nuovi Pulsanti nei Progetti**
- **Pulsante "Repository"**: Apre direttamente il repository GitHub
- **Pulsante "Vedi Codice"**: Apre una nuova pagina interna che mostra un'anteprima del codice

#### 3. **Nuova Pagina di Visualizzazione Codice**
- URL: `/project/<id>/code`
- Mostra una descrizione del progetto
- Visualizza file di codice di esempio con syntax highlighting
- Link al repository completo

### File Modificati

#### Modelli (`models.py`)
- Rimosso campo `link`
- Rimosso campo `github`
- Aggiunto campo `github_repo`
- Aggiornato metodo `to_dict()`

#### Applicazione (`app.py`)
- Aggiornate le route di creazione/modifica progetto
- Aggiunta nuova route `/project/<id>/code`
- Aggiornata logica di salvataggio progetti

#### Template
- **`templates/admin/project_form.html`**: Form semplificato con un solo campo repository
- **`templates/projects.html`**: Nuovi pulsanti per repository e codice
- **`templates/index.html`**: Aggiornati i pulsanti nella homepage
- **`templates/project_code.html`**: Nuovo template per visualizzazione codice

#### Stili (`static/css/style.css`)
- Aggiunti stili per la pagina di visualizzazione codice
- Stili per file header, code content, badges
- Responsive design per mobile

### Come Usare il Nuovo Sistema

#### 1. **Creazione/Modifica Progetto**
1. Vai alla sezione admin
2. Crea o modifica un progetto
3. Inserisci solo il link al repository GitHub nel campo "Repository GitHub"
4. Salva il progetto

#### 2. **Visualizzazione Progetti**
- **Pulsante "Repository"**: Apre il repository GitHub in una nuova tab
- **Pulsante "Vedi Codice"**: Apre la pagina interna con anteprima del codice

#### 3. **Pagina Codice**
- Mostra descrizione del progetto
- Visualizza file di codice di esempio
- Link al repository completo
- Syntax highlighting per Python, HTML, CSS

### Migrazione Database

Se hai dati esistenti, esegui lo script di migrazione:

```bash
python migrate_db.py
```

Lo script:
- Migra i dati dal vecchio formato al nuovo
- Usa il campo `github` se disponibile, altrimenti `link`
- Rimuove i vecchi campi dal database

### Vantaggi del Nuovo Sistema

1. **Semplificazione**: Un solo campo da compilare invece di due
2. **Esperienza Utente**: Due pulsanti chiari e distinti
3. **Visualizzazione Codice**: Anteprima interna del codice del progetto
4. **Consistenza**: Tutti i progetti seguono lo stesso formato
5. **Manutenibilità**: Codice più pulito e organizzato

### Note Tecniche

- Il template `project_code.html` mostra codice di esempio hardcoded
- Per progetti reali, potresti voler integrare con API GitHub per mostrare codice reale
- La syntax highlighting usa Prism.js
- Il design è completamente responsive 