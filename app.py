import streamlit as st
import sqlite3, pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px

DB='eventflow.db'

def conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c=conn(); cur=c.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT, email TEXT, source TEXT, created_at TEXT, notes TEXT);
    CREATE TABLE IF NOT EXISTS demandes(id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, event_type TEXT, event_date TEXT, budget REAL, guests INTEGER, status TEXT, lost_reason TEXT, created_at TEXT, notes TEXT);
    CREATE TABLE IF NOT EXISTS devis(id INTEGER PRIMARY KEY AUTOINCREMENT, demande_id INTEGER, amount REAL, sent_date TEXT, expiry_date TEXT, status TEXT, notes TEXT);
    CREATE TABLE IF NOT EXISTS relances(id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, demande_id INTEGER, title TEXT, due_date TEXT, channel TEXT, status TEXT, result TEXT);
    CREATE TABLE IF NOT EXISTS interactions(id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, demande_id INTEGER, kind TEXT, date TEXT, summary TEXT);
    CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT, demande_id INTEGER, event_date TEXT, satisfaction INTEGER, comment TEXT);
    ''')
    c.commit()
    if cur.execute('SELECT COUNT(*) FROM clients').fetchone()[0]==0:
        clients=[('Salma El Amrani','0612345678','salma@example.com','Instagram','2026-10-10','Préférence WhatsApp'),('Youssef Benali','0623456789','youssef@example.com','Recommandation','2026-10-12',''),('Nadia Tazi','0634567890','nadia@example.com','Facebook','2026-10-15',''),('Omar & Lina','0645678901','contact@example.com','Site web','2026-10-18','Couple'),('Kenza Alaoui','0656789012','kenza@example.com','Instagram','2026-10-20','')]
        cur.executemany('INSERT INTO clients(name,phone,email,source,created_at,notes) VALUES(?,?,?,?,?,?)',clients)
        demands=[(1,'Fiançailles','2027-03-20',35000,120,'Devis envoyé','', '2026-10-10',''),(1,'Anniversaire','2027-11-08',18000,60,'Nouveau','', '2026-11-01','Demande future'),(2,'Mariage','2027-06-12',95000,250,'Confirmé','', '2026-10-12',''),(3,'Anniversaire','2026-12-20',22000,80,'En négociation','', '2026-10-15',''),(4,'Mariage','2027-09-04',120000,300,'Perdu','Budget insuffisant','2026-10-18',''),(5,'Fiançailles','2027-02-14',40000,140,'Qualifié','', '2026-10-20','')]
        cur.executemany('INSERT INTO demandes(client_id,event_type,event_date,budget,guests,status,lost_reason,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)',demands)
        quotes=[(1,35000,'2026-11-15','2026-11-30','En attente','Offre initiale'),(3,95000,'2026-10-20','2026-11-20','Accepté',''),(4,22000,'2026-11-02','2026-11-22','En attente','')]
        cur.executemany('INSERT INTO devis(demande_id,amount,sent_date,expiry_date,status,notes) VALUES(?,?,?,?,?,?)',quotes)
        follow=[(1,1,'Relancer après envoi du devis','2026-11-24','WhatsApp','À faire',''),(3,3,'Confirmer les détails','2026-11-26','Téléphone','À faire',''),(3,4,'Proposition ajustée','2026-11-22','Email','En retard','')]
        cur.executemany('INSERT INTO relances(client_id,demande_id,title,due_date,channel,status,result) VALUES(?,?,?,?,?,?,?)',follow)
        acts=[(1,1,'WhatsApp','2026-11-15','Devis initial partagé'),(2,3,'Rendez-vous','2026-10-20','Validation du brief'),(3,4,'Téléphone','2026-11-02','Discussion sur les options')]
        cur.executemany('INSERT INTO interactions(client_id,demande_id,kind,date,summary) VALUES(?,?,?,?,?)',acts)
        cur.execute('INSERT INTO feedback(demande_id,event_date,satisfaction,comment) VALUES(?,?,?,?)',(3,'2026-06-15',5,'Très bonne expérience, équipe attentive.'))
        c.commit()
    c.close()

st.set_page_config(page_title='EventFlow CRM',page_icon='✨',layout='wide')
init_db()

def read(q): return pd.read_sql_query(q,conn())
def execute(q,args=()):
    c=conn(); c.execute(q,args); c.commit(); c.close()
def opts_clients():
    df=read('SELECT id,name FROM clients ORDER BY name'); return {f"{r['name']} (#{r['id']})":int(r['id']) for _,r in df.iterrows()}
def opts_demands():
    df=read('SELECT d.id,c.name,d.event_type,d.event_date FROM demandes d LEFT JOIN clients c ON c.id=d.client_id ORDER BY d.id DESC'); return {f"#{r.id} · {r.name} · {r.event_type} ({r.event_date})":int(r.id) for _,r in df.iterrows()}

# Styling — EventFlow Luxury Editorial
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
:root{--wine:#590d20;--wine2:#781b31;--gold:#b58a53;--cream:#f5eee4;--paper:#fffaf4;--ink:#34251f;--muted:#8c776c;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)} .stApp{background:linear-gradient(135deg,#f4ece2 0%,#fbf7f1 48%,#f2e7dc 100%)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#4d0819 0%,#650e24 55%,#360612 100%);border-right:1px solid #b28b5c} [data-testid="stSidebar"] *{color:#f8eee2!important}
.brand{font-family:'Playfair Display',serif;font-size:36px;font-weight:600;color:#e4c38d;letter-spacing:.3px}.subbrand{color:#e0c9ae;font-size:11px;letter-spacing:2.4px;text-transform:uppercase}
.metric{background:linear-gradient(145deg,#fffaf4,#f1e3d3);border:1px solid #dfc8a9;padding:20px;border-radius:18px;box-shadow:0 8px 24px #5c132010;min-height:125px}.metric-label{color:#8d7566;font-size:13px;letter-spacing:.3px}.metric-value{font-family:'Playfair Display',serif;font-size:32px;font-weight:600;color:#5a1022;margin-top:5px}.metric-note{color:#a37b4d;font-size:12px;margin-top:7px}
.section-title,h1,h2,h3{font-family:'Playfair Display',serif!important;color:#4e1020!important} h1{font-size:2.5rem!important} h2{font-size:1.65rem!important} h3{font-size:1.25rem!important}
[data-testid="stForm"],div[data-testid="stExpander"]{background:#fffaf4;border:1px solid #e7d6c2;border-radius:16px}[data-testid="stDataFrame"]{border:1px solid #e7d6c2;border-radius:14px;overflow:hidden}
.stButton button,.stDownloadButton button{background:#651126;color:#fff;border:1px solid #b28b5c;border-radius:12px}.stButton button:hover,.stDownloadButton button:hover{background:#841e37;color:white;border-color:#d5b47f}
[data-testid="stMetric"]{background:#fffaf4;border:1px solid #e6d4bf;border-radius:14px;padding:14px}hr{border-color:#d8b991}
</style>''',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:14px 0 10px"><div style="font-size:28px;color:#d9b77d">✦</div><div class="brand">EventFlow</div><div class="subbrand">Luxury · Events · Relations</div><div style="color:#d9b77d;font-size:11px;margin-top:8px">✧ ───────── ✧</div></div>',unsafe_allow_html=True)
    st.markdown('---')
    page=st.radio('NAVIGATION',['Dashboard','Clients','Demandes','Devis','Relances','Interactions','Fidélisation','Rapports'],label_visibility='collapsed')
    st.markdown('---')
    st.caption('MARRAKECH · CRM ÉVÉNEMENTIEL')
    st.caption('Prototype académique — données fictives')

# Data helpers
clients_df=read('SELECT * FROM clients')
df=read('SELECT d.*,c.name AS client_name FROM demandes d LEFT JOIN clients c ON c.id=d.client_id')
quotes=read('SELECT q.*,d.event_type,c.name AS client_name FROM devis q LEFT JOIN demandes d ON d.id=q.demande_id LEFT JOIN clients c ON c.id=d.client_id')
follow=read('SELECT r.*,c.name AS client_name,d.event_type FROM relances r LEFT JOIN clients c ON c.id=r.client_id LEFT JOIN demandes d ON d.id=r.demande_id')

if page=='Dashboard':
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:38px;color:#4e1020;margin-bottom:0'>Bonjour, Admin ✦</div><div style='font-style:italic;color:#9a6b51;font-size:17px;margin-bottom:12px'>Vue d’ensemble de votre activité commerciale</div>",unsafe_allow_html=True)
    total_clients=len(clients_df); total_dem=len(df); open_dem=len(df[df.status.isin(['Nouveau','Qualifié','Devis envoyé','En négociation'])]); won=len(df[df.status=='Confirmé']); overdue=len(follow[(follow.status!='Effectuée')&(follow.due_date<pd.Timestamp.today().strftime('%Y-%m-%d'))])
    conv=(won/total_dem*100) if total_dem else 0
    cols=st.columns(5)
    metrics=[('Clients',total_clients,'Portefeuille client'),('Demandes',total_dem,'Toutes les demandes'),('En cours',open_dem,'Pipeline commercial'),('Confirmées',won,'Événements gagnés'),('Conversion',f'{conv:.1f}%','Demandes confirmées')]
    for col,(label,value,note) in zip(cols,metrics): col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)
    st.write('')
    left,right=st.columns([1.3,1])
    with left:
        st.subheader('Pipeline commercial')
        if len(df):
            stages=['Nouveau','Qualifié','Devis envoyé','En négociation','Confirmé','Perdu']
            counts=df.status.value_counts().reindex(stages,fill_value=0).reset_index(); counts.columns=['Statut','Nombre']
            st.plotly_chart(px.bar(counts,x='Statut',y='Nombre',color='Statut',text='Nombre',template='plotly_white',color_discrete_sequence=['#6a1025','#b58a53','#9b5361','#d9b77d','#7c293d','#b7a08a']),use_container_width=True)
    with right:
        st.subheader('Demandes par type')
        if len(df): st.plotly_chart(px.pie(df,names='event_type',hole=.55,template='plotly_white',color_discrete_sequence=['#650e24','#b58a53','#a65b6a','#dfc49d','#8c776c','#d8a68a']),use_container_width=True)
    st.subheader('Relances à surveiller')
    if len(follow):
        alerts=follow[follow.status!='Effectuée'].copy().sort_values('due_date')
        st.dataframe(alerts[['client_name','event_type','title','due_date','channel','status']],hide_index=True,use_container_width=True)
    st.subheader('Demandes récentes')
    st.dataframe(df[['client_name','event_type','event_date','budget','status']].tail(8),hide_index=True,use_container_width=True)

elif page=='Clients':
    st.title('Clients'); st.caption('Centralisez les profils et l’historique de votre clientèle.')
    with st.expander('＋ Ajouter un client',expanded=False):
        with st.form('addclient'):
            a,b=st.columns(2); name=a.text_input('Nom complet *'); phone=b.text_input('Téléphone'); email=a.text_input('Email'); source=b.selectbox('Source',['Instagram','WhatsApp','Facebook','Site web','Recommandation','Autre']); notes=st.text_area('Notes')
            if st.form_submit_button('Enregistrer le client'):
                if name.strip(): execute('INSERT INTO clients(name,phone,email,source,created_at,notes) VALUES(?,?,?,?,?,?)',(name,phone,email,source,date.today().isoformat(),notes)); st.success('Client ajouté.'); st.rerun()
    search=st.text_input('⌕ Rechercher un client',placeholder='Nom, téléphone, email...')
    data=read('SELECT * FROM clients ORDER BY id DESC')
    if search: data=data[data.astype(str).apply(lambda row: row.str.contains(search,case=False).any(),axis=1)]
    st.dataframe(data,hide_index=True,use_container_width=True)
    with st.expander('Modifier ou supprimer un client'):
        ids=opts_clients(); chosen=st.selectbox('Client',list(ids.keys())); cid=ids[chosen]; selected=read(f'SELECT * FROM clients WHERE id={cid}').iloc[0]
        with st.form('editclient'):
            nm=st.text_input('Nom',selected['name']); ph=st.text_input('Téléphone',selected['phone'] or ''); em=st.text_input('Email',selected['email'] or ''); src=st.text_input('Source',selected['source'] or ''); nt=st.text_area('Notes',selected['notes'] or '')
            x,y=st.columns(2); save=x.form_submit_button('Mettre à jour'); delete=y.form_submit_button('Supprimer')
            if save: execute('UPDATE clients SET name=?,phone=?,email=?,source=?,notes=? WHERE id=?',(nm,ph,em,src,nt,cid)); st.success('Profil mis à jour'); st.rerun()
            if delete: execute('DELETE FROM clients WHERE id=?',(cid,)); st.warning('Client supprimé'); st.rerun()

elif page=='Demandes':
    st.title('Demandes'); st.caption('Suivez chaque opportunité de la qualification à la décision.')
    with st.expander('＋ Créer une demande',expanded=False):
        with st.form('adddem'):
            cids=opts_clients(); a,b,c=st.columns(3); cl=a.selectbox('Client *',list(cids.keys())); typ=b.selectbox('Type',['Mariage','Fiançailles','Anniversaire','Fête familiale','Cérémonie privée','Autre']); evdate=c.date_input('Date événement',date.today()+timedelta(days=90)); budget=a.number_input('Budget estimatif (MAD)',min_value=0.0,step=1000.0); guests=b.number_input('Invités estimés',min_value=0,step=10); status=c.selectbox('Statut',['Nouveau','Qualifié','Devis envoyé','En négociation','Confirmé','Perdu']); reason=st.text_input('Motif de perte (si applicable)'); notes=st.text_area('Notes')
            if st.form_submit_button('Enregistrer la demande'):
                execute('INSERT INTO demandes(client_id,event_type,event_date,budget,guests,status,lost_reason,created_at,notes) VALUES(?,?,?,?,?,?,?,?,?)',(cids[cl],typ,evdate.isoformat(),budget,guests,status,reason,date.today().isoformat(),notes)); st.success('Demande créée'); st.rerun()
    statusfilter=st.multiselect('Filtrer par statut',df.status.unique().tolist(),default=df.status.unique().tolist() if len(df) else [])
    shown=df[df.status.isin(statusfilter)]
    st.dataframe(shown[['id','client_name','event_type','event_date','budget','guests','status','lost_reason']],hide_index=True,use_container_width=True)
    with st.expander('Modifier le statut ou les détails'):
        if len(df):
            chosen=st.selectbox('Demande ID',df.id.tolist()); row=df[df.id==chosen].iloc[0]
            with st.form('editdem'):
                stat=st.selectbox('Statut',['Nouveau','Qualifié','Devis envoyé','En négociation','Confirmé','Perdu'],index=['Nouveau','Qualifié','Devis envoyé','En négociation','Confirmé','Perdu'].index(row.status)); reason=st.text_input('Motif de perte',row.lost_reason or ''); notes=st.text_area('Notes',row.notes or '')
                if st.form_submit_button('Actualiser'):
                    execute('UPDATE demandes SET status=?,lost_reason=?,notes=? WHERE id=?',(stat,reason,notes,int(chosen))); st.success('Demande mise à jour'); st.rerun()

elif page=='Devis':
    st.title('Devis'); st.caption('Gérez les propositions commerciales et leur suivi.')
    with st.expander('＋ Ajouter un devis',expanded=False):
        with st.form('addquote'):
            dops=opts_demands(); d=st.selectbox('Demande',list(dops.keys())); a,b=st.columns(2); amount=a.number_input('Montant (MAD)',min_value=0.0,step=500.0); sent=b.date_input('Date d’envoi',date.today()); expiry=a.date_input('Date de validité',date.today()+timedelta(days=15)); status=b.selectbox('Statut',['Brouillon','Envoyé','En attente','Accepté','Refusé','Expiré']); notes=st.text_area('Notes')
            if st.form_submit_button('Enregistrer le devis'):
                execute('INSERT INTO devis(demande_id,amount,sent_date,expiry_date,status,notes) VALUES(?,?,?,?,?,?)',(dops[d],amount,sent.isoformat(),expiry.isoformat(),status,notes)); st.success('Devis enregistré'); st.rerun()
    st.dataframe(quotes[['id','client_name','event_type','amount','sent_date','expiry_date','status']],hide_index=True,use_container_width=True)
    with st.expander('Modifier le statut du devis'):
        if len(quotes):
            qid=st.selectbox('Devis #',quotes.id.tolist()); qr=quotes[quotes.id==qid].iloc[0]
            with st.form('editquote'):
                qstat=st.selectbox('Statut',['Brouillon','Envoyé','En attente','Accepté','Refusé','Expiré'],index=['Brouillon','Envoyé','En attente','Accepté','Refusé','Expiré'].index(qr.status)); qnotes=st.text_area('Notes',qr.notes or '')
                if st.form_submit_button('Mettre à jour'):
                    execute('UPDATE devis SET status=?,notes=? WHERE id=?',(qstat,qnotes,int(qid))); st.rerun()

elif page=='Relances':
    st.title('Relances'); st.caption('Planifiez les prochaines actions commerciales.')
    with st.expander('＋ Planifier une relance',expanded=False):
        with st.form('addfollow'):
            cids=opts_clients(); dops=opts_demands(); a,b=st.columns(2); cl=a.selectbox('Client',list(cids.keys())); d=b.selectbox('Demande associée (facultatif)',list(dops.keys())); title=st.text_input('Objet *'); due=a.date_input('Date de relance',date.today()); channel=b.selectbox('Canal',['WhatsApp','Téléphone','Email','Rendez-vous','Autre']); status=st.selectbox('Statut',['À faire','Effectuée']); result=st.text_area('Résultat / notes')
            if st.form_submit_button('Enregistrer'):
                execute('INSERT INTO relances(client_id,demande_id,title,due_date,channel,status,result) VALUES(?,?,?,?,?,?,?)',(cids[cl],dops[d],title,due.isoformat(),channel,status,result)); st.success('Relance enregistrée'); st.rerun()
    st.dataframe(follow[['id','client_name','event_type','title','due_date','channel','status','result']],hide_index=True,use_container_width=True)
    with st.expander('Mettre à jour une relance'):
        if len(follow):
            rid=st.selectbox('Relance #',follow.id.tolist()); rr=follow[follow.id==rid].iloc[0]
            with st.form('editfollow'):
                fs=st.selectbox('Statut',['À faire','En retard','Effectuée'],index=['À faire','En retard','Effectuée'].index(rr.status) if rr.status in ['À faire','En retard','Effectuée'] else 0); res=st.text_area('Résultat',rr.result or '')
                if st.form_submit_button('Mettre à jour'):
                    execute('UPDATE relances SET status=?,result=? WHERE id=?',(fs,res,int(rid))); st.rerun()

elif page=='Interactions':
    st.title('Interactions'); st.caption('Gardez une trace de chaque échange avec vos clients.')
    with st.expander('＋ Ajouter une interaction',expanded=False):
        with st.form('addact'):
            cids=opts_clients(); dops=opts_demands(); a,b=st.columns(2); cl=a.selectbox('Client',list(cids.keys())); d=b.selectbox('Demande',list(dops.keys())); kind=a.selectbox('Type',['WhatsApp','Téléphone','Email','Rendez-vous','Visite','Autre']); dt=b.date_input('Date',date.today()); summary=st.text_area('Résumé de l’échange *')
            if st.form_submit_button('Enregistrer'):
                execute('INSERT INTO interactions(client_id,demande_id,kind,date,summary) VALUES(?,?,?,?,?)',(cids[cl],dops[d],kind,dt.isoformat(),summary)); st.success('Interaction ajoutée'); st.rerun()
    acts=read('SELECT i.*,c.name AS client_name,d.event_type FROM interactions i LEFT JOIN clients c ON c.id=i.client_id LEFT JOIN demandes d ON d.id=i.demande_id ORDER BY i.date DESC')
    st.dataframe(acts[['id','client_name','event_type','kind','date','summary']],hide_index=True,use_container_width=True)

elif page=='Fidélisation':
    st.title('Fidélisation'); st.caption('Suivi post-événement et satisfaction client.')
    with st.expander('＋ Enregistrer un retour client',expanded=False):
        with st.form('feedback'):
            dops=opts_demands(); d=st.selectbox('Demande / événement',list(dops.keys())); evdate=st.date_input('Date de réalisation',date.today()); score=st.slider('Satisfaction client',1,5,5); comment=st.text_area('Commentaire')
            if st.form_submit_button('Enregistrer le retour'):
                execute('INSERT INTO feedback(demande_id,event_date,satisfaction,comment) VALUES(?,?,?,?)',(dops[d],evdate.isoformat(),score,comment)); st.success('Retour enregistré'); st.rerun()
    f=read('SELECT f.*,c.name AS client_name,d.event_type,d.event_date AS demande_event_date FROM feedback f LEFT JOIN demandes d ON d.id=f.demande_id LEFT JOIN clients c ON c.id=d.client_id ORDER BY f.id DESC')
    if len(f): st.dataframe(f[['client_name','event_type','demande_event_date','satisfaction','comment']],hide_index=True,use_container_width=True)
    else: st.info('Aucun retour enregistré pour le moment.')
    st.subheader('Clients ayant plusieurs demandes')
    repeat=read('SELECT c.name,COUNT(d.id) AS demandes FROM clients c JOIN demandes d ON d.client_id=c.id GROUP BY c.id HAVING COUNT(d.id)>1')
    st.dataframe(repeat,hide_index=True,use_container_width=True)

elif page=='Rapports':
    st.title('Rapports & performance'); st.caption('Indicateurs de pilotage commercial — calculés sur les données enregistrées.')
    d=read('SELECT * FROM demandes'); q=read('SELECT * FROM devis'); r=read('SELECT * FROM relances'); f=read('SELECT * FROM feedback')
    total=len(d); won=len(d[d.status=='Confirmé']); lost=len(d[d.status=='Perdu']); conversion=won/total*100 if total else 0
    decided=len(q[q.status.isin(['Accepté','Refusé'])]); accepted=len(q[q.status=='Accepté']); acceptance=accepted/decided*100 if decided else 0
    a,b,c,e=st.columns(4)
    a.metric('Taux de conversion',f'{conversion:.1f}%'); b.metric('Acceptation devis',f'{acceptance:.1f}%'); c.metric('Demandes perdues',lost); e.metric('Satisfaction moyenne',f'{f.satisfaction.mean():.1f}/5' if len(f) else '—')
    st.subheader('Répartition par statut')
    if len(d): st.plotly_chart(px.bar(d.groupby('status',as_index=False).size(),x='status',y='size',template='plotly_white',labels={'size':'Nombre','status':'Statut'}),use_container_width=True)
    st.subheader('Demandes par type')
    if len(d): st.plotly_chart(px.pie(d,names='event_type',hole=.5,template='plotly_white'),use_container_width=True)
    st.subheader('Export des données')
    for label,table in [('Clients',clients_df),('Demandes',df),('Devis',quotes),('Relances',follow)]:
        st.download_button(f'Télécharger {label} (CSV)',table.to_csv(index=False).encode('utf-8-sig'),file_name=f'eventflow_{label.lower()}.csv',mime='text/csv',key=f'dl_{label}')

st.markdown('---')
st.caption('EventFlow CRM · Prototype de démonstration · Données fictives · Marrakech')
