import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta

# INIITALISATION DES VARIABLES GLOBALES
bdd = "tontine_gestion_v2.db"
frame = None
barre_menu = None
admin_actuel = None

# BASES DE DONNÉES
def initialiser_bdd():
    conn = sqlite3.connect(bdd)
    curseur = conn.cursor()
    curseur.execute('''CREATE TABLE IF NOT EXISTS admin 
                      (id INTEGER PRIMARY KEY, utilisateur TEXT, mot_de_passe TEXT)''')
    curseur.execute('''CREATE TABLE IF NOT EXISTS membres 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, date_inscription TIMESTAMP)''')
    curseur.execute('''CREATE TABLE IF NOT EXISTS parametres 
                      (cle TEXT PRIMARY KEY, valeur REAL)''')
    curseur.execute("INSERT OR IGNORE INTO parametres (cle, valeur) VALUES ('contribution', 10000.0)")
    conn.commit()
    conn.close()

# GESTION DE LA CONTRIBUTION UNITAIRE
def obtenir_contribution_unitaire():
    conn = sqlite3.connect(bdd)
    res = conn.execute("SELECT valeur FROM parametres WHERE cle='contribution'").fetchone()
    conn.close()
    return res[0] if res else 10000.0

# CALCUL DES PROCHAINS SAMEDIS

def obtenir_prochains_samedis(nombre):
    samedis = []
    maintenant = datetime.now()
    jours_restants = 5 - maintenant.weekday() 
    if jours_restants <= 0: jours_restants += 7
    prochain_samedi = maintenant + timedelta(days=jours_restants)
    for i in range(nombre):
        date_sam = prochain_samedi + timedelta(weeks=i)
        samedis.append(date_sam.strftime("%d/%m/%Y"))
    return samedis


# NAVIGATION ENTRE LES ÉCRANS
def vider_ecran():
    for widget in frame.winfo_children():
        widget.destroy()

def maj_menu(role="invite"):
    barre_menu.delete(0, "end")
    menu_fichier = tk.Menu(barre_menu, tearoff=0)
    barre_menu.add_cascade(label="Fichier", menu=menu_fichier)
    menu_fichier.add_command(label="Accueil", command=ecran_accueil)
    menu_fichier.add_separator()
    menu_fichier.add_command(label="Quitter", command=app.quit)

    if role == "admin":
        menu_admin = tk.Menu(barre_menu, tearoff=0)
        barre_menu.add_cascade(label="Administration", menu=menu_admin)
        menu_admin.add_command(label="Tableau de bord", command=ecran_tableau_bord)
        menu_admin.add_command(label="Gérer les membres", command=ecran_gestion_membres)
        menu_admin.add_command(label="Rotation", command=ecran_rotation)
        menu_admin.add_separator()
        menu_admin.add_command(label="Paramètres", command=fenetre_reglages)
    
    def version():
        messagebox.showinfo("Version", "Version actuelle de l'application : 2.10")
    barre_menu.add_command(label="A propos", command=version)

# ECRAN D'ACCEUIL
def ecran_accueil():
    vider_ecran()
    maj_menu("invite")
    
    conn = sqlite3.connect(bdd)
    existe_admin = conn.execute("SELECT * FROM admin").fetchone()
    conn.close()

    cadre = tk.Frame(frame, pady=60)
    cadre.pack()

    if not existe_admin:
        tk.Label(cadre, text="Création du compte Admin", font=("Arial", 16, "bold")).pack(pady=10)
        u_ent = tk.Entry(cadre, width=30); u_ent.insert(0, "Identifiant"); u_ent.pack(pady=5)
        p_ent = tk.Entry(cadre, show="*", width=30); p_ent.pack(pady=5)
        tk.Button(cadre, text="Enregistrer", bg="#2ecc71", 
                  command=lambda: creer_admin(u_ent.get(), p_ent.get())).pack(pady=10)
    else:
        tk.Label(cadre, text="Connexion Administrateur", font=("Arial", 16, "bold")).pack(pady=10)
        u_ent = tk.Entry(cadre, width=30); u_ent.pack(pady=5)
        p_ent = tk.Entry(cadre, show="*", width=30); p_ent.pack(pady=5)
        tk.Button(cadre, text="Se connecter", bg="#3498db", fg="white", 
                  command=lambda: connexion_admin(u_ent.get(), p_ent.get())).pack(pady=10)
        
        tk.Label(cadre, text="---").pack(pady=10)
        tk.Button(cadre, text="Espace Membre", command=ecran_membre).pack()

# TABLEAU DE BORD ADMIN
def ecran_tableau_bord():
    vider_ecran()
    contrib = obtenir_contribution_unitaire()
    tk.Label(frame, text=f"Tableau de bord - Admin", font=("Arial", 18, "bold")).pack(pady=10)
    
    conn = sqlite3.connect(bdd)
    membres = conn.execute("SELECT * FROM membres ORDER BY date_inscription ASC").fetchall()
    conn.close()

    nb = len(membres)
    cadre_resume = tk.LabelFrame(frame, text="Finances", padx=20, pady=10)
    cadre_resume.pack(fill="x", padx=20)
    tk.Label(cadre_resume, text=f"Membres : {nb}/12").pack(side="left")
    tk.Label(cadre_resume, text=f"Total Cagnotte : {int(nb*contrib)} FC", fg="green", font=("bold")).pack(side="right")

    colonnes = ("ID", "Nom", "Date")
    tableau = ttk.Treeview(frame, columns=colonnes, show="headings")
    for c in colonnes: tableau.heading(c, text=c)
    for m in membres: tableau.insert("", "end", values=m)
    tableau.pack(pady=20, padx=20, fill="both", expand=True)

# ECRAN DE GESTION DES MEMBRES
def ecran_gestion_membres():
    vider_ecran()
    tk.Label(frame, text="Gestion des Membres", font=("Arial", 16)).pack(pady=10)
    
    f = tk.Frame(frame); f.pack(pady=10)
    tk.Label(f, text="Nom:").grid(row=0, column=0)
    nom_e = tk.Entry(f); nom_e.grid(row=0, column=1)
    
    #AJOUTER UN MEMBRE
    def add():
        conn = sqlite3.connect(bdd)
        if conn.execute("SELECT COUNT(*) FROM membres").fetchone()[0] < 12:
            conn.execute("INSERT INTO membres (nom, date_inscription) VALUES (?, ?)", (nom_e.get(), datetime.now()))
            conn.commit(); conn.close()
            messagebox.showinfo("Confirmation", f"Utilisateur {nom_e.get()} ajouté !")
            ecran_gestion_membres()
        else:
            messagebox.showwarning("Limite", "Maximum 12 membres atteint.")
            conn.close()
    
    tk.Button(f, text="Ajouter", bg="green", fg="white", command=add).grid(row=0, column=2, padx=5)

    tk.Label(frame, text="ID à supprimer:").pack(pady=(10,0))
    id_s = tk.Entry(frame); id_s.pack()

    #SUPPRIMER UN MEMBRE
    def suppr():
        conn = sqlite3.connect(bdd)
        conn.execute("DELETE FROM membres WHERE id=?", (id_s.get(),))
        conn.commit(); conn.close()
        messagebox.showinfo(f"L'utilisateur avec l'ID {id_s.get} a été supprimé avec succès")
        ecran_gestion_membres()
    tk.Button(frame, text="Supprimer", bg="red", fg="white", command=suppr).pack()

# ECRAN DE GESTION DES ROTATIONS
def ecran_rotation():
    vider_ecran()
    contrib = obtenir_contribution_unitaire()
    conn = sqlite3.connect(bdd)
    membres = conn.execute("SELECT nom FROM membres ORDER BY date_inscription ASC").fetchall()
    conn.close()
    
    if membres:
        dates = obtenir_prochains_samedis(len(membres))
        tableau = ttk.Treeview(frame, columns=("Date", "Nom", "Montant"), show="headings")
        tableau.heading("Date", text="Date de Sortie"); tableau.heading("Nom", text="Bénéficiaire"); tableau.heading("Montant", text="Somme (FC)")
        for i, m in enumerate(membres):
            tableau.insert("", "end", values=(dates[i], m[0], f"{int(len(membres)*contrib)} FC"))
        tableau.pack(fill="both", expand=True, padx=20)
    tk.Button(frame, text="Retour", command=ecran_tableau_bord).pack(pady=10)

# ECRAN MEMBRES
def ecran_membre():
    vider_ecran()
    tk.Label(frame, text="Espace Membre", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame, text="Entrez votre nom :").pack()
    nom_e = tk.Entry(frame); nom_e.pack()
    
    def check():
        conn = sqlite3.connect(bdd)
        m_list = [r[0] for r in conn.execute("SELECT nom FROM membres ORDER BY date_inscription ASC").fetchall()]
        conn.close()
        if nom_e.get() in m_list:
            idx = m_list.index(nom_e.get())
            date = obtenir_prochains_samedis(len(m_list))[idx]
            messagebox.showinfo("Infos", f"Votre tour : Samedi {date}\nMontant : {int(len(m_list)*obtenir_contribution_unitaire())} FC")
        else: messagebox.showerror("Erreur", "Nom introuvable")
        
    tk.Button(frame, text="Vérifier mon tour", command=check).pack(pady=20)
    tk.Button(frame, text="Retour", command=ecran_accueil).pack(pady=10)

# GESTION DE COMPTE ADMIN
def creer_admin(u, p):
    if u and p:
        conn = sqlite3.connect(bdd)
        conn.execute("INSERT INTO admin (utilisateur, mot_de_passe) VALUES (?, ?)", (u, p))
        conn.commit(); conn.close()
        messagebox.showinfo("Succès", "Compte créé !")
        ecran_accueil()

#Connexion Admin
def connexion_admin(u, p):
    global admin_actuel
    conn = sqlite3.connect(bdd)
    res = conn.execute("SELECT * FROM admin WHERE utilisateur=? AND mot_de_passe=?", (u, p)).fetchone()
    conn.close()
    if res:
        admin_actuel = u
        maj_menu("admin")
        ecran_tableau_bord()
    else:
        messagebox.showerror("Erreur", "Identifiants incorrects")

# ECRAN DE RÉGLAGES
def fenetre_reglages():
    fen = tk.Toplevel(app)
    fen.title("Réglages")
    fen.geometry("300x200")
    tk.Label(fen, text="Montant contribution (FC):").pack(pady=10)
    entree = tk.Entry(fen)
    entree.insert(0, str(int(obtenir_contribution_unitaire())))
    entree.pack()
    
    def sauver():
            val = float(entree.get())
            conn = sqlite3.connect(bdd)
            conn.execute("UPDATE parametres SET valeur=? WHERE cle='contribution'", (val,))
            conn.commit(); conn.close()
            messagebox.showinfo("Succès", "Mis à jour !")
            fen.destroy()
            ecran_tableau_bord()

    tk.Button(fen, text="Sauvegarder", command=sauver).pack(pady=20)


# LANCEMENT DE L'APPLICATION
initialiser_bdd()
    
app = tk.Tk()
app.title("Tontine RDC - FC")
app.geometry("600x430")
    
barre_menu = tk.Menu(app)
app.config(menu=barre_menu)
    
frame = tk.Frame(app)
frame.pack(fill="both", expand=True)
    
ecran_accueil()
    
app.mainloop()
