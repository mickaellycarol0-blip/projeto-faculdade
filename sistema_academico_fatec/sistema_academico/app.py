import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import date, datetime
import os

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sistema Acadêmico FATEC-PB", page_icon="🎓", layout="wide")
DB = "academico.db"

# ─── BANCO DE DADOS ─────────────────────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT DEFAULT 'usuario'
    );
    CREATE TABLE IF NOT EXISTS candidatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, cpf TEXT UNIQUE NOT NULL,
        email TEXT, telefone TEXT, endereco TEXT,
        num_inscricao TEXT UNIQUE, status TEXT DEFAULT 'candidato'
    );
    CREATE TABLE IF NOT EXISTS cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL, nome TEXT NOT NULL,
        carga_horaria INTEGER, observacoes TEXT
    );
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, carga_horaria INTEGER,
        ementa TEXT, curso_id INTEGER,
        FOREIGN KEY(curso_id) REFERENCES cursos(id)
    );
    CREATE TABLE IF NOT EXISTS professores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula TEXT UNIQUE NOT NULL, nome TEXT NOT NULL,
        cpf TEXT, email TEXT, telefone TEXT, especialidade TEXT
    );
    CREATE TABLE IF NOT EXISTS turmas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, horario TEXT, periodo TEXT,
        data_abertura TEXT, curso_id INTEGER, status TEXT DEFAULT 'ativa',
        FOREIGN KEY(curso_id) REFERENCES cursos(id)
    );
    CREATE TABLE IF NOT EXISTS turma_alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turma_id INTEGER, aluno_id INTEGER, data_matricula TEXT,
        FOREIGN KEY(turma_id) REFERENCES turmas(id),
        FOREIGN KEY(aluno_id) REFERENCES candidatos(id)
    );
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula TEXT UNIQUE NOT NULL, nome TEXT NOT NULL,
        cpf TEXT, endereco TEXT, telefone TEXT,
        salario REAL, cargo TEXT, departamento TEXT
    );
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER, disciplina_id INTEGER,
        valor REAL, tipo TEXT, data TEXT,
        FOREIGN KEY(aluno_id) REFERENCES candidatos(id),
        FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id)
    );
    CREATE TABLE IF NOT EXISTS mensalidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER, valor REAL, vencimento TEXT,
        pagamento TEXT, status TEXT DEFAULT 'pendente',
        juros REAL DEFAULT 0, desconto REAL DEFAULT 0,
        FOREIGN KEY(aluno_id) REFERENCES candidatos(id)
    );
    INSERT OR IGNORE INTO usuarios (login, senha, perfil)
        VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');
    """)
    conn.commit()
    conn.close()

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# ─── AUTH ───────────────────────────────────────────────────────────────────────
def login_page():
    st.markdown("<h1 style='text-align:center'>🎓 Sistema Acadêmico FATEC-PB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Projeto de Análise e Desenvolvimento de Sistemas</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.subheader("🔐 Login")
        login = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            conn = get_conn()
            row = conn.execute("SELECT perfil FROM usuarios WHERE login=? AND senha=?",
                               (login, hash_senha(senha))).fetchone()
            conn.close()
            if row:
                st.session_state.user = login
                st.session_state.perfil = row[0]
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
        st.info("👤 Admin padrão: **admin** / **admin**")

# ─── MÓDULOS ────────────────────────────────────────────────────────────────────
def modulo_candidatos():
    st.header("👥 Q1 - Cadastro de Candidatos e Inscrições")
    tab1, tab2 = st.tabs(["📋 Listar / Consultar", "➕ Novo Candidato"])
    with tab1:
        busca = st.text_input("🔍 Buscar por Nome, CPF ou Nº Inscrição")
        conn = get_conn()
        if busca:
            df = pd.read_sql(f"SELECT * FROM candidatos WHERE nome LIKE ? OR cpf LIKE ? OR num_inscricao LIKE ?",
                             conn, params=(f"%{busca}%", f"%{busca}%", f"%{busca}%"))
        else:
            df = pd.read_sql("SELECT * FROM candidatos", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            sel = st.selectbox("Selecionar para excluir", df['id'].tolist(), key="del_cand")
            if st.button("🗑️ Excluir selecionado"):
                conn = get_conn()
                conn.execute("DELETE FROM candidatos WHERE id=?", (sel,))
                conn.commit(); conn.close()
                st.success("Excluído!"); st.rerun()
    with tab2:
        with st.form("form_cand"):
            nome = st.text_input("Nome completo*")
            col1, col2 = st.columns(2)
            cpf = col1.text_input("CPF*")
            num_insc = col2.text_input("Nº Inscrição*")
            email = col1.text_input("E-mail")
            tel = col2.text_input("Telefone")
            end = st.text_input("Endereço")
            if st.form_submit_button("💾 Cadastrar"):
                if nome and cpf and num_insc:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO candidatos (nome,cpf,email,telefone,endereco,num_inscricao) VALUES (?,?,?,?,?,?)",
                                     (nome,cpf,email,tel,end,num_insc))
                        conn.commit(); conn.close()
                        st.success(f"✅ Candidato {nome} cadastrado!")
                    except: st.error("CPF ou Nº de Inscrição já cadastrado.")
                else: st.warning("Preencha os campos obrigatórios (*)")

def modulo_cursos():
    st.header("📚 Q2 - Cadastro de Cursos")
    tab1, tab2 = st.tabs(["📋 Listar", "➕ Novo Curso"])
    with tab1:
        conn = get_conn()
        df = pd.read_sql("SELECT * FROM cursos", conn); conn.close()
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            sel = st.selectbox("Selecionar para excluir", df['id'].tolist(), key="del_curso")
            if st.button("🗑️ Excluir"):
                if st.session_state.get("confirm_curso") == sel:
                    conn = get_conn(); conn.execute("DELETE FROM cursos WHERE id=?", (sel,))
                    conn.commit(); conn.close(); st.success("Excluído!"); st.rerun()
                else:
                    st.session_state.confirm_curso = sel
                    st.warning("⚠️ Clique novamente para confirmar a exclusão.")
    with tab2:
        with st.form("form_curso"):
            col1, col2 = st.columns(2)
            codigo = col1.text_input("Código*")
            nome = col2.text_input("Nome do Curso*")
            carga = st.number_input("Carga Horária (h)", min_value=0, step=10)
            obs = st.text_area("Observações")
            if st.form_submit_button("💾 Salvar"):
                if codigo and nome:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO cursos (codigo,nome,carga_horaria,observacoes) VALUES (?,?,?,?)", (codigo,nome,carga,obs))
                        conn.commit(); conn.close(); st.success("✅ Curso cadastrado!")
                    except: st.error("Código já existente.")
                else: st.warning("Preencha os campos obrigatórios.")

def modulo_disciplinas():
    st.header("📖 Q3 - Cadastro de Disciplinas")
    conn = get_conn()
    cursos = pd.read_sql("SELECT id, nome FROM cursos", conn); conn.close()
    tab1, tab2 = st.tabs(["📋 Listar", "➕ Nova Disciplina"])
    with tab1:
        conn = get_conn()
        df = pd.read_sql("""SELECT d.id, d.nome, d.carga_horaria, d.ementa, c.nome as curso
                            FROM disciplinas d LEFT JOIN cursos c ON d.curso_id=c.id""", conn)
        conn.close(); st.dataframe(df, use_container_width=True)
    with tab2:
        with st.form("form_disc"):
            nome = st.text_input("Nome da Disciplina*")
            col1, col2 = st.columns(2)
            carga = col1.number_input("Carga Horária (h)", min_value=0, step=10)
            curso_opts = {r['nome']: r['id'] for _, r in cursos.iterrows()} if not cursos.empty else {}
            curso_sel = col2.selectbox("Curso", list(curso_opts.keys()) if curso_opts else ["(Sem cursos)"])
            ementa = st.text_area("Ementa")
            if st.form_submit_button("💾 Salvar"):
                if nome:
                    conn = get_conn()
                    curso_id = curso_opts.get(curso_sel)
                    conn.execute("INSERT INTO disciplinas (nome,carga_horaria,ementa,curso_id) VALUES (?,?,?,?)", (nome,carga,ementa,curso_id))
                    conn.commit(); conn.close(); st.success("✅ Disciplina cadastrada!")
                else: st.warning("Informe o nome.")

def modulo_professores():
    st.header("👨‍🏫 Q4 - Cadastro de Professores")
    tab1, tab2 = st.tabs(["📋 Listar", "➕ Novo Professor"])
    with tab1:
        conn = get_conn()
        df = pd.read_sql("SELECT * FROM professores", conn); conn.close()
        st.dataframe(df, use_container_width=True)
    with tab2:
        with st.form("form_prof"):
            col1, col2 = st.columns(2)
            matricula = col1.text_input("Matrícula*")
            nome = col2.text_input("Nome completo*")
            cpf = col1.text_input("CPF")
            email = col2.text_input("E-mail")
            tel = col1.text_input("Telefone")
            espec = col2.text_input("Especialidade")
            if st.form_submit_button("💾 Salvar"):
                if matricula and nome:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO professores (matricula,nome,cpf,email,telefone,especialidade) VALUES (?,?,?,?,?,?)",
                                     (matricula,nome,cpf,email,tel,espec))
                        conn.commit(); conn.close(); st.success("✅ Professor cadastrado!")
                    except: st.error("Matrícula já existente.")
                else: st.warning("Matrícula e Nome são obrigatórios.")

def modulo_turmas():
    st.header("🏫 Q5 - Turmas e Lançamento de Alunos")
    conn = get_conn()
    cursos = pd.read_sql("SELECT id, nome FROM cursos", conn)
    alunos = pd.read_sql("SELECT id, nome, num_inscricao FROM candidatos", conn)
    conn.close()
    tab1, tab2, tab3 = st.tabs(["📋 Turmas", "➕ Nova Turma", "👥 Lançar Alunos"])
    with tab1:
        conn = get_conn()
        df = pd.read_sql("""SELECT t.id, t.nome, t.horario, t.periodo, t.status, c.nome as curso
                            FROM turmas t LEFT JOIN cursos c ON t.curso_id=c.id""", conn)
        conn.close(); st.dataframe(df, use_container_width=True)
    with tab2:
        with st.form("form_turma"):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome da Turma*")
            horario = col2.text_input("Horário (ex: 19h-22h)")
            periodo = col1.text_input("Período (ex: 2024.1)")
            curso_opts = {r['nome']: r['id'] for _, r in cursos.iterrows()} if not cursos.empty else {}
            curso_sel = col2.selectbox("Curso", list(curso_opts.keys()) if curso_opts else ["(Sem cursos)"])
            data_ab = st.date_input("Data de Abertura", date.today())
            if st.form_submit_button("💾 Salvar"):
                if nome:
                    conn = get_conn()
                    conn.execute("INSERT INTO turmas (nome,horario,periodo,data_abertura,curso_id) VALUES (?,?,?,?,?)",
                                 (nome,horario,periodo,str(data_ab),curso_opts.get(curso_sel)))
                    conn.commit(); conn.close(); st.success("✅ Turma cadastrada!")
    with tab3:
        conn = get_conn()
        turmas_df = pd.read_sql("SELECT id, nome FROM turmas WHERE status='ativa'", conn); conn.close()
        if not turmas_df.empty and not alunos.empty:
            turma_opts = {r['nome']: r['id'] for _, r in turmas_df.iterrows()}
            turma_sel = st.selectbox("Turma", list(turma_opts.keys()))
            aluno_opts = {f"{r['nome']} ({r['num_inscricao']})": r['id'] for _, r in alunos.iterrows()}
            aluno_sel = st.selectbox("Aluno", list(aluno_opts.keys()))
            if st.button("➕ Lançar Aluno na Turma"):
                conn = get_conn()
                conn.execute("INSERT OR IGNORE INTO turma_alunos (turma_id,aluno_id,data_matricula) VALUES (?,?,?)",
                             (turma_opts[turma_sel], aluno_opts[aluno_sel], str(date.today())))
                conn.commit(); conn.close(); st.success("✅ Aluno lançado!")
            conn = get_conn()
            alunos_turma = pd.read_sql("""SELECT c.nome, c.num_inscricao, ta.data_matricula
                FROM turma_alunos ta JOIN candidatos c ON ta.aluno_id=c.id
                WHERE ta.turma_id=?""", conn, params=(turma_opts[turma_sel],))
            conn.close()
            st.dataframe(alunos_turma, use_container_width=True)
        else:
            st.info("Cadastre turmas e candidatos primeiro.")

def modulo_funcionarios():
    st.header("🧑‍💼 Q6 - Cadastro de Funcionários")
    tab1, tab2 = st.tabs(["📋 Listar", "➕ Novo Funcionário"])
    with tab1:
        conn = get_conn()
        df = pd.read_sql("SELECT * FROM funcionarios", conn); conn.close()
        st.dataframe(df, use_container_width=True)
    with tab2:
        with st.form("form_func"):
            col1, col2 = st.columns(2)
            matricula = col1.text_input("Matrícula*")
            nome = col2.text_input("Nome completo*")
            cpf = col1.text_input("CPF")
            tel = col2.text_input("Telefone")
            cargo = col1.text_input("Cargo")
            depto = col2.text_input("Departamento")
            salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0, format="%.2f")
            end = st.text_input("Endereço")
            if st.form_submit_button("💾 Salvar"):
                if matricula and nome:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO funcionarios (matricula,nome,cpf,telefone,cargo,departamento,salario,endereco) VALUES (?,?,?,?,?,?,?,?)",
                                     (matricula,nome,cpf,tel,cargo,depto,salario,end))
                        conn.commit(); conn.close(); st.success("✅ Funcionário cadastrado!")
                    except: st.error("Matrícula já existente.")

def modulo_consulta_candidatos():
    st.header("🔍 Q7 - Consulta de Candidatos")
    tipo = st.radio("Buscar por:", ["Nome", "CPF", "Nº de Inscrição"], horizontal=True)
    busca = st.text_input("Digite o valor para busca")
    if busca:
        campo = {"Nome":"nome","CPF":"cpf","Nº de Inscrição":"num_inscricao"}[tipo]
        conn = get_conn()
        df = pd.read_sql(f"SELECT * FROM candidatos WHERE {campo} LIKE ?", conn, params=(f"%{busca}%",))
        conn.close()
        if df.empty:
            st.warning("Nenhum candidato encontrado.")
        else:
            st.success(f"{len(df)} resultado(s) encontrado(s)")
            st.dataframe(df, use_container_width=True)

def modulo_comprovante():
    st.header("🖨️ Q8 - Emissão de Comprovante de Inscrição")
    busca = st.text_input("🔍 Buscar candidato por CPF ou Nome")
    if busca:
        conn = get_conn()
        df = pd.read_sql("SELECT * FROM candidatos WHERE cpf LIKE ? OR nome LIKE ?", conn, params=(f"%{busca}%",f"%{busca}%"))
        conn.close()
        if df.empty:
            st.warning("Candidato não encontrado.")
        else:
            cand = df.iloc[0]
            st.success("✅ Candidato encontrado!")
            st.markdown(f"""
<div style="border:2px solid #2980b9; border-radius:10px; padding:20px; background:#f0f8ff; font-family:monospace">
<h3 style="text-align:center; color:#2980b9">🎓 COMPROVANTE DE INSCRIÇÃO - FATEC-PB</h3>
<hr>
<b>Nome:</b> {cand['nome']}<br>
<b>CPF:</b> {cand['cpf']}<br>
<b>Nº Inscrição:</b> {cand['num_inscricao']}<br>
<b>E-mail:</b> {cand['email']}<br>
<b>Telefone:</b> {cand['telefone']}<br>
<b>Endereço:</b> {cand['endereco']}<br>
<b>Status:</b> {cand['status']}<br>
<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
<hr>
<p style="text-align:center; color:gray; font-size:12px">Este comprovante deve ser apresentado na secretaria da FATEC-PB</p>
</div>
""", unsafe_allow_html=True)
            if st.button("🖨️ Imprimir Comprovante"):
                st.info("Use Ctrl+P para imprimir esta página.")

def modulo_autenticacao():
    st.header("🔐 Q9 - Gerenciamento de Usuários")
    if st.session_state.get("perfil") != "admin":
        st.warning("Acesso restrito ao administrador.")
        return
    tab1, tab2 = st.tabs(["👥 Usuários cadastrados", "➕ Novo Usuário"])
    with tab1:
        conn = get_conn()
        df = pd.read_sql("SELECT id, login, perfil FROM usuarios", conn); conn.close()
        st.dataframe(df, use_container_width=True)
    with tab2:
        with st.form("form_user"):
            login = st.text_input("Login*")
            senha = st.text_input("Senha*", type="password")
            perfil = st.selectbox("Perfil", ["usuario","supervisor","admin"])
            if st.form_submit_button("💾 Criar Usuário"):
                if login and senha:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO usuarios (login,senha,perfil) VALUES (?,?,?)", (login,hash_senha(senha),perfil))
                        conn.commit(); conn.close(); st.success("✅ Usuário criado!")
                    except: st.error("Login já existente.")

def modulo_notas():
    st.header("📊 Q10 - Lançamento de Notas e Boletim Escolar")
    conn = get_conn()
    alunos = pd.read_sql("SELECT id, nome, num_inscricao FROM candidatos", conn)
    discs = pd.read_sql("SELECT id, nome FROM disciplinas", conn); conn.close()
    tab1, tab2 = st.tabs(["📝 Lançar Nota", "📋 Boletim"])
    with tab1:
        if not alunos.empty and not discs.empty:
            with st.form("form_nota"):
                col1, col2 = st.columns(2)
                aluno_opts = {f"{r['nome']} ({r['num_inscricao']})": r['id'] for _, r in alunos.iterrows()}
                disc_opts = {r['nome']: r['id'] for _, r in discs.iterrows()}
                aluno_sel = col1.selectbox("Aluno", list(aluno_opts.keys()))
                disc_sel = col2.selectbox("Disciplina", list(disc_opts.keys()))
                nota = col1.number_input("Nota", min_value=0.0, max_value=10.0, step=0.1, format="%.1f")
                tipo = col2.selectbox("Tipo", ["AV1","AV2","AV3","Final"])
                if st.form_submit_button("💾 Lançar Nota"):
                    conn = get_conn()
                    conn.execute("INSERT INTO notas (aluno_id,disciplina_id,valor,tipo,data) VALUES (?,?,?,?,?)",
                                 (aluno_opts[aluno_sel],disc_opts[disc_sel],nota,tipo,str(date.today())))
                    conn.commit(); conn.close(); st.success("✅ Nota lançada!")
        else:
            st.info("Cadastre alunos e disciplinas primeiro.")
    with tab2:
        if not alunos.empty:
            aluno_opts = {f"{r['nome']} ({r['num_inscricao']})": r['id'] for _, r in alunos.iterrows()}
            aluno_sel = st.selectbox("Selecionar Aluno", list(aluno_opts.keys()))
            conn = get_conn()
            df = pd.read_sql("""SELECT d.nome as disciplina, n.tipo, n.valor, n.data
                FROM notas n JOIN disciplinas d ON n.disciplina_id=d.id
                WHERE n.aluno_id=?""", conn, params=(aluno_opts[aluno_sel],))
            conn.close()
            if df.empty:
                st.info("Nenhuma nota lançada para este aluno.")
            else:
                media = df['valor'].mean()
                st.metric("Média Geral", f"{media:.1f}", delta="Aprovado ✅" if media >= 5 else "Reprovado ❌")
                st.dataframe(df.style.applymap(
                    lambda v: "background-color:#d4edda" if isinstance(v, float) and v >= 5
                    else ("background-color:#f8d7da" if isinstance(v, float) else ""),
                    subset=['valor']), use_container_width=True)

def modulo_mensalidades():
    st.header("💰 Q11 - Mensalidades e Controle Financeiro")
    conn = get_conn()
    alunos = pd.read_sql("SELECT id, nome, num_inscricao FROM candidatos", conn); conn.close()
    tab1, tab2, tab3 = st.tabs(["💳 Lançar Mensalidade", "📋 Histórico", "⚠️ Inadimplentes"])
    with tab1:
        if not alunos.empty:
            with st.form("form_mens"):
                aluno_opts = {f"{r['nome']} ({r['num_inscricao']})": r['id'] for _, r in alunos.iterrows()}
                aluno_sel = st.selectbox("Aluno", list(aluno_opts.keys()))
                col1, col2 = st.columns(2)
                valor = col1.number_input("Valor (R$)", min_value=0.0, step=50.0, format="%.2f")
                venc = col2.date_input("Vencimento", date.today())
                pag = col1.date_input("Data de Pagamento", date.today())
                juros = col2.number_input("Juros (R$)", min_value=0.0, step=1.0, format="%.2f")
                desc = col1.number_input("Desconto (R$)", min_value=0.0, step=1.0, format="%.2f")
                status = col2.selectbox("Status", ["pago","pendente","atrasado"])
                if st.form_submit_button("💾 Registrar"):
                    conn = get_conn()
                    conn.execute("INSERT INTO mensalidades (aluno_id,valor,vencimento,pagamento,status,juros,desconto) VALUES (?,?,?,?,?,?,?)",
                                 (aluno_opts[aluno_sel],valor,str(venc),str(pag),status,juros,desc))
                    conn.commit(); conn.close(); st.success("✅ Mensalidade registrada!")
    with tab2:
        if not alunos.empty:
            aluno_opts = {f"{r['nome']} ({r['num_inscricao']})": r['id'] for _, r in alunos.iterrows()}
            aluno_sel = st.selectbox("Selecionar Aluno", list(aluno_opts.keys()), key="hist_aluno")
            conn = get_conn()
            df = pd.read_sql("SELECT * FROM mensalidades WHERE aluno_id=? ORDER BY vencimento DESC", conn, params=(aluno_opts[aluno_sel],))
            conn.close()
            if df.empty:
                st.info("Nenhuma mensalidade registrada.")
            else:
                total_pago = df[df['status']=='pago']['valor'].sum()
                total_pend = df[df['status']!='pago']['valor'].sum()
                col1,col2 = st.columns(2)
                col1.metric("Total Pago", f"R$ {total_pago:.2f}")
                col2.metric("Total Pendente", f"R$ {total_pend:.2f}")
                st.dataframe(df, use_container_width=True)
    with tab3:
        conn = get_conn()
        df = pd.read_sql("""SELECT c.nome, c.num_inscricao, m.valor, m.vencimento, m.status
            FROM mensalidades m JOIN candidatos c ON m.aluno_id=c.id
            WHERE m.status='atrasado' OR m.status='pendente'
            ORDER BY m.vencimento""", conn)
        conn.close()
        if df.empty:
            st.success("✅ Nenhum aluno inadimplente!")
        else:
            st.warning(f"⚠️ {len(df)} mensalidade(s) em aberto")
            st.dataframe(df, use_container_width=True)

# ─── MENU PRINCIPAL ─────────────────────────────────────────────────────────────
def main():
    init_db()
    if "user" not in st.session_state:
        login_page()
        return

    with st.sidebar:
        st.markdown(f"### 🎓 FATEC-PB")
        st.markdown(f"👤 **{st.session_state.user}** ({st.session_state.perfil})")
        st.divider()
        menu = st.radio("📂 Módulos", [
            "🏠 Início",
            "Q1 - Candidatos",
            "Q2 - Cursos",
            "Q3 - Disciplinas",
            "Q4 - Professores",
            "Q5 - Turmas",
            "Q6 - Funcionários",
            "Q7 - Consulta Candidatos",
            "Q8 - Comprovante",
            "Q9 - Usuários",
            "Q10 - Notas",
            "Q11 - Mensalidades",
        ])
        st.divider()
        if st.button("🚪 Sair"):
            del st.session_state.user; del st.session_state.perfil; st.rerun()

    if menu == "🏠 Início":
        st.title("🎓 Sistema de Gestão Acadêmica - FATEC-PB")
        st.markdown("**Sistema de Informações Acadêmicas** desenvolvido como projeto de análise e desenvolvimento de sistemas.")
        cols = st.columns(3)
        with get_conn() as conn:
            n_cand = conn.execute("SELECT COUNT(*) FROM candidatos").fetchone()[0]
            n_cursos = conn.execute("SELECT COUNT(*) FROM cursos").fetchone()[0]
            n_profs = conn.execute("SELECT COUNT(*) FROM professores").fetchone()[0]
        cols[0].metric("👥 Candidatos", n_cand)
        cols[1].metric("📚 Cursos", n_cursos)
        cols[2].metric("👨‍🏫 Professores", n_profs)
        st.info("📌 Use o menu lateral para navegar entre os módulos do sistema.")
    elif menu == "Q1 - Candidatos": modulo_candidatos()
    elif menu == "Q2 - Cursos": modulo_cursos()
    elif menu == "Q3 - Disciplinas": modulo_disciplinas()
    elif menu == "Q4 - Professores": modulo_professores()
    elif menu == "Q5 - Turmas": modulo_turmas()
    elif menu == "Q6 - Funcionários": modulo_funcionarios()
    elif menu == "Q7 - Consulta Candidatos": modulo_consulta_candidatos()
    elif menu == "Q8 - Comprovante": modulo_comprovante()
    elif menu == "Q9 - Usuários": modulo_autenticacao()
    elif menu == "Q10 - Notas": modulo_notas()
    elif menu == "Q11 - Mensalidades": modulo_mensalidades()

if __name__ == "__main__":
    main()
