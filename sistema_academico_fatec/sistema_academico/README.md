#  Sistema de Gestão Acadêmica - FATEC-PB

> **Projeto de Análise e Desenvolvimento de Sistemas**  
> Disciplina: ADS — UNIPÊ  
> Professor: Ricardo Roberto de Lima  
> Entrega: 14/04/2026

---

##  Descrição

Sistema de Informações Acadêmicas baseado no projeto **AQUILES PRO 4** da FATEC-PB, desenvolvido com Python e Streamlit, com banco de dados SQLite. O sistema contempla 11 módulos funcionais, cada um com diagrama de classes UML, requisitos funcionais/não-funcionais e aplicação web.

---

##  Estrutura do Projeto

```
sistema_academico/
├── app.py                        ← Aplicação principal Streamlit (todos os módulos)
├── academico.db                  ← Banco de dados SQLite (gerado automaticamente)
├── README.md                     ← Este arquivo
│
├── questao_01/                   ← Q1: Candidatos e Inscrições
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_02/                   ← Q2: Cursos
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_03/                   ← Q3: Disciplinas
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_04/                   ← Q4: Professores
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_05/                   ← Q5: Turmas e Lançamento de Alunos
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_06/                   ← Q6: Funcionários
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_07/                   ← Q7: Consulta de Candidatos
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_08/                   ← Q8: Comprovante de Inscrição
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_09/                   ← Q9: Autenticação de Usuários
│   ├── diagrama_classes.png
│   └── requisitos.txt
├── questao_10/                   ← Q10: Notas e Boletim
│   ├── diagrama_classes.png
│   └── requisitos.txt
└── questao_11/                   ← Q11: Mensalidades e Inadimplentes
    ├── diagrama_classes.png
    └── requisitos.txt
```

---

##  Como executar

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip instalado

### 2. Instalar dependências

```bash
pip install streamlit pandas
```

### 3. Executar o sistema

```bash
streamlit run app.py
```

O sistema abrirá automaticamente no navegador em: `http://localhost:8501`

### 4. Login padrão

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin   | admin | Administrador |

---

##  Módulos do Sistema

| Questão | Módulo | Descrição |
|---------|--------|-----------|
| Q1 | Candidatos e Inscrições | Cadastro, consulta e gerenciamento de candidatos do vestibular |
| Q2 | Cursos | Cadastro e manutenção dos cursos oferecidos |
| Q3 | Disciplinas | Cadastro de disciplinas vinculadas a cursos |
| Q4 | Professores | Cadastro e gerenciamento de professores |
| Q5 | Turmas | Abertura de turmas e lançamento de alunos |
| Q6 | Funcionários | Cadastro de funcionários e seus cargos |
| Q7 | Consulta Candidatos | Busca por nome, CPF ou número de inscrição |
| Q8 | Comprovante | Emissão e impressão do comprovante de inscrição |
| Q9 | Autenticação | Gerenciamento de usuários, senhas e perfis de acesso |
| Q10 | Notas e Boletim | Lançamento de notas e consulta do boletim escolar |
| Q11 | Mensalidades | Lançamento, histórico e controle de inadimplentes |

---

##  Banco de Dados

Tabelas criadas automaticamente no SQLite:

- `usuarios` — controle de acesso ao sistema
- `candidatos` — dados dos candidatos/alunos
- `cursos` — cursos disponíveis
- `disciplinas` — disciplinas vinculadas aos cursos
- `professores` — corpo docente
- `turmas` — turmas abertas
- `turma_alunos` — relação aluno x turma
- `funcionarios` — funcionários da instituição
- `notas` — notas lançadas por disciplina
- `mensalidades` — controle financeiro dos alunos

---

##  Perfis de Acesso

| Perfil | Permissões |
|--------|-----------|
| `admin` | Acesso total a todos os módulos |
| `supervisor` | Acesso a notas, mensalidades e relatórios |
| `usuario` | Consulta de candidatos e boletins |

---

##  Tecnologias Utilizadas

- **Python 3.x** — linguagem de programação
- **Streamlit** — framework para interface web
- **SQLite** — banco de dados relacional embutido
- **Pandas** — manipulação de dados
- **Matplotlib** — geração dos diagramas de classes UML
- **IA Generativa (Claude)** — apoio na geração do código

---

##  Diagramas de Classes

Cada módulo possui um diagrama UML de classes mostrando:
- **Classes** com seus respectivos nomes
- **Atributos** (tipo e visibilidade)
- **Métodos** principais
- **Relacionamentos** entre classes

Os diagramas estão disponíveis em cada pasta `questao_XX/diagrama_classes.png`.

---

##  Requisitos

Os requisitos funcionais e não-funcionais de cada módulo estão documentados em `questao_XX/requisitos.txt`.

**Exemplo — Q1 Requisitos Funcionais:**
- RF01 - Cadastrar candidatos com nome, CPF, e-mail, telefone e endereço
- RF02 - Consultar candidatos por nome, CPF ou número de inscrição
- RF03 - Alterar dados cadastrais de candidatos
- RF04 - Excluir candidatos do sistema
- RF05 - Registrar inscrições de candidatos para cursos do vestibular

---

## Desenvolvido por

- **Projeto base:** Mickaelly caroline de oliveira brito — UNIPÊ 

---

