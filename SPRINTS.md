# Open Scheduler - Sprint Planning

**Projeto:** Webapp de agendamento de tarefas Python (estilo Dagster + Task Scheduler)  
**Início:** 2025-12-07  
**Status:** 🟡 Em desenvolvimento

---

## 📋 Visão Geral

### Objetivo
Criar um scheduler webapp bonito e responsivo que permite:
- Visualizar jobs ativos com status visual (verde/vermelho/laranja)
- Adicionar jobs selecionando arquivos .py via file tree ou upload
- Configurar schedule sem modificar código Python
- Monitorar execuções e logs
- Gerenciar múltiplos diretórios trackeados

### Stack Técnico
- **Frontend:** Dash 2.14 + Dash Bootstrap Components
- **Backend:** Python + APScheduler + SQLAlchemy
- **Database:** SQLite
- **Styling:** Bootstrap 5 + CSS custom (tema escuro)
- **Deployment:** Host direto (sem Docker)

---

## 🎯 Sprints

### ✅ Sprint 0: Setup Inicial (COMPLETO)
**Status:** ✅ Concluído  
**Data:** 2025-12-07

- [x] Estrutura de pastas (backend/, frontend/, docs/)
- [x] requirements.txt
- [x] run.bat
- [x] Backend base (app.py, core/__init__.py)
- [x] Módulos básicos (fileops.py, executor.py, scheduler.py)
- [x] .gitignore, .env.example, README.md

---

### ✅ Sprint 1: Database Schema & Models
**Status:** ✅ Completo  
**Estimativa:** 1-2h  
**Real:** 0.5h  
**Prioridade:** ALTA

#### Objetivos
- Criar models SQLAlchemy completos
- Setup database com SQLite
- Migrations básicas (se necessário)
- Seed data para testes

#### Tarefas
- [x] `backend/core/database.py` - SQLAlchemy engine, sessionmaker, Base
- [x] `backend/core/models.py` - Models:
  - `TrackedDirectory` (id, path, active, created_at)
  - `Job` (id, name, description, file_path, file_source, schedule_type, schedule_value, timezone, status, args, env_vars, timeout, retry_max, retry_delay, next_run, last_run, last_status, created_at, updated_at)
  - `Execution` (id, job_id FK, started_at, ended_at, status, output, exit_code, duration)
  - `UploadedFile` (id, original_name, stored_path, file_hash, size_bytes, uploaded_at)
- [x] `backend/core/schemas.py` - Pydantic schemas para validação
- [x] Script de inicialização do DB (`backend/init_db.py`)
- [x] Testar criação de tabelas

#### Entregáveis
- ✅ Database `scheduler.db` criado
- ✅ Models funcionais com relationships
- ✅ Script de teste que cria/lê registros
- ✅ Seed data: tracked directory padrão (project root)

---

### ✅ Sprint 2: Frontend Base & Styling
**Status:** ✅ Completo  
**Estimativa:** 2-3h  
**Real:** 1h  
**Prioridade:** ALTA

#### Objetivos
- Layout base com navbar
- Tema escuro moderno
- Componentes reutilizáveis
- CSS customizado

#### Tarefas
- [x] `frontend/` package setup
- [x] `frontend/components/navbar.py` - Navbar com links para páginas
- [x] `frontend/components/status_badge.py` - Badge colorido (🟢🔴🟠)
- [x] `frontend/components/job_card.py` - Card visual de job
- [x] `frontend/assets/custom.css` - Tema escuro, cores, responsividade
- [x] `backend/app.py` - Integrar Dash multi-page + navbar
- [x] Testar navegação entre páginas

#### Entregáveis
- ✅ Navbar funcional
- ✅ Páginas vazias (Overview, Jobs, New Job, Logs, Settings)
- ✅ Tema escuro aplicado
- ✅ Componentes reutilizáveis prontos
- ✅ App rodando em http://localhost:8050

---

### ✅ Sprint 3: Overview Page (Dashboard)
**Status:** ✅ Completo  
**Estimativa:** 3-4h  
**Real:** 1.5h  
**Prioridade:** ALTA

#### Objetivos
- Dashboard com KPIs
- Cards de jobs ativos
- Recent activity chart
- Auto-refresh (5s)

#### Tarefas
- [ ] `frontend/pages/overview.py` - Layout do dashboard
- [ ] KPI cards (Total Jobs, Active, Success Rate, Failed Today)
- [ ] Query DB para dados dos cards
- [ ] Job cards com status visual + next run countdown
- [ ] Botões de ação (Pause, Run Now, View Logs)
- [ ] Plotly chart - execuções últimas 24h
- [ ] `dcc.Interval` para auto-refresh (5s)
- [ ] Callbacks para atualizar dados dinamicamente

#### Entregáveis
- Overview page completa e responsiva
- KPIs atualizando em tempo real
- Cards de jobs clicáveis
- Chart de atividade recente

---

### ✅ Sprint 4: New Job Page
**Status:** ✅ Completo  
**Estimativa:** 4-5h  
**Real:** 2h  
**Prioridade:** ALTA

#### Objetivos
- File tree navegável (tracked dirs)
- Upload de arquivos
- Preview de código
- Form de schedule completo
- Test run funcional

#### Tarefas
- [ ] `frontend/pages/new_job.py` - Layout com tabs
- [ ] `frontend/components/file_tree.py` - Árvore recursiva de arquivos
- [ ] Query `TrackedDirectory` do DB
- [ ] `backend/core/fileops.py` - Função `list_files_from_dirs(tracked_dirs)`
- [ ] Tab "Project Files" com file tree
- [ ] Tab "Upload" com `dcc.Upload` (limit 5MB)
- [ ] `backend/core/api.py` - Endpoint `POST /upload`
- [ ] Preview de código (syntax highlight básico)
- [ ] Form: nome, description, schedule type (cron/interval/once)
- [ ] Schedule inputs (cron expression ou interval)
- [ ] Advanced: timeout, retry, args, env vars
- [ ] Botão "Test Run" - executa arquivo e mostra output em modal
- [ ] Callback para salvar job no DB + registrar no scheduler
- [ ] Validações (nome único, arquivo existe, schedule válido)

#### Entregáveis
- New Job page completa
- File tree funcional
- Upload de arquivos com validação
- Preview de código
- Form de schedule com validação
- Test run funcional
- Criação de job com sucesso

---

### ✅ Sprint 5: Backend API & Scheduler
**Status:** ✅ Completo  
**Estimativa:** 4-5h  
**Real:** 1h  
**Prioridade:** ALTA

#### Objetivos
- CRUD completo de jobs
- APScheduler integrado com persist
- Executor robusto
- Re-register jobs ao restart

#### Tarefas
- [ ] `backend/core/api.py` - Endpoints REST:
  - `GET /api/jobs` - listar todos jobs
  - `GET /api/jobs/<id>` - detalhes de um job
  - `POST /api/jobs` - criar novo job
  - `PUT /api/jobs/<id>` - atualizar job
  - `DELETE /api/jobs/<id>` - deletar job
  - `POST /api/jobs/<id>/pause` - pausar job
  - `POST /api/jobs/<id>/resume` - resumir job
  - `POST /api/jobs/<id>/run-now` - executar agora
  - `POST /api/jobs/<id>/test` - test run
  - `GET /api/files` - listar arquivos tracked dirs
  - `POST /api/upload` - upload arquivo
  - `GET /api/executions` - listar execuções (com filtros)
- [ ] `backend/core/scheduler.py` - Melhorias:
  - Persist jobs no DB (usar SQLAlchemyJobStore ou custom)
  - Re-register jobs ao startup
  - Calcular `next_run` corretamente
  - Handle cron/interval/once
- [ ] `backend/core/executor.py` - Melhorias:
  - Criar `Execution` record antes de rodar
  - Atualizar `Execution` após rodar
  - Atualizar `Job.last_run`, `Job.last_status`, `Job.next_run`
  - Retry logic se configurado
  - Limit output (50KB)
- [ ] `backend/app.py` - Startup:
  - Inicializar DB
  - Inicializar scheduler
  - Re-register jobs ativos
  - Integrar API endpoints com Dash
- [ ] Testes de cada endpoint

#### Entregáveis
- API REST completa
- APScheduler persistindo jobs
- Jobs executando no horário correto
- Retry automático funcional
- Logs de execução salvos no DB

---

### ✅ Sprint 6: Jobs Page
**Status:** ✅ Completo  
**Estimativa:** 3-4h  
**Real:** 0.5h  
**Prioridade:** MÉDIA

#### Objetivos
- DataTable interativa de jobs
- Modal de detalhes
- Ações (pause/resume/delete/run now)
- Filtros e search

#### Tarefas
- [ ] `frontend/pages/jobs.py` - Layout
- [ ] Dash DataTable com colunas (status, name, schedule, next run, last run, actions)
- [ ] Query todos jobs do DB
- [ ] Botão "+ New Job" → redirect para new_job page
- [ ] Search input (filtrar por nome)
- [ ] Dropdown filter por status (All, Active, Paused, Failed)
- [ ] Click em row → modal com detalhes do job
- [ ] Modal: histórico de execuções (últimas 10)
- [ ] Botões de ação (Pause, Resume, Delete, Run Now, Edit)
- [ ] Callbacks para ações (chamar API endpoints)
- [ ] Confirmação de delete (modal)
- [ ] Auto-refresh (5s) para atualizar next_run countdown

#### Entregáveis
- Jobs page completa
- DataTable com filtros funcionais
- Modal de detalhes com histórico
- Ações funcionando (pause/resume/delete/run now)

---

### ✅ Sprint 7: Logs Page
**Status:** ✅ Completo  
**Estimativa:** 2-3h  
**Real:** 0.5h  
**Prioridade:** MÉDIA

#### Objetivos
- Histórico de execuções
- Filtros avançados
- Expandable output
- Export

#### Tarefas
- [ ] `frontend/pages/logs.py` - Layout
- [ ] DataTable de execuções (job name, started, status, duration)
- [ ] Query `Execution` do DB com joins
- [ ] Filters: job dropdown, status dropdown, date range
- [ ] Search input (buscar em output)
- [ ] Click em row → expandir para mostrar output completo
- [ ] Syntax highlight básico do output (opcional)
- [ ] Botão "Export" → download CSV ou JSON
- [ ] Paginação (mostrar 50 por página)
- [ ] Auto-refresh (5s) opcional (toggle)

#### Entregáveis
- Logs page completa
- Filtros funcionais
- Output expandable
- Export funcional

---

### 🔵 Sprint 8: Settings & Tracked Directories
**Status:** 🔴 Pendente  
**Estimativa:** 2-3h  
**Prioridade:** MÉDIA

#### Objetivos
- Gerenciar tracked directories
- Add/remove dirs via file picker
- Validações

#### Tarefas
- [ ] `frontend/pages/settings.py` - Layout
- [ ] Seção "Tracked Directories"
- [ ] Lista atual de tracked dirs
- [ ] Botão "+ Add Directory" → abre file picker (como?)
  - Opção 1: Input text com path manual
  - Opção 2: Integração com file dialog (via callback que chama `tkinter.filedialog`?)
- [ ] `backend/core/api.py` - Endpoints:
  - `GET /api/tracked-dirs` - listar
  - `POST /api/tracked-dirs` - adicionar
  - `DELETE /api/tracked-dirs/<id>` - remover
- [ ] Validação: path existe, não está duplicado, tem permissão de leitura
- [ ] Callback para add/remove dirs
- [ ] Refresh file tree quando dirs mudam

#### Entregáveis
- Settings page completa
- Gerenciamento de tracked dirs funcional
- File tree atualiza ao adicionar/remover dir

**Nota:** File picker no browser é limitado. Soluções:
- Input text manual (mais simples)
- Electron/Tauri wrapper (complexo)
- Usar `dcc.Upload` de pasta (não suportado)
- Implementar como input text com validação server-side ✅ (escolhido)

---

### 🔵 Sprint 9: Testes & Polimento Final
**Status:** 🔴 Pendente  
**Estimativa:** 2-3h  
**Prioridade:** BAIXA

#### Objetivos
- Testes de integração
- Polimento de UI
- Documentação final
- Bugfixes

#### Tarefas
- [ ] Testes manuais de todos os fluxos
- [ ] Corrigir bugs encontrados
- [ ] Melhorar responsividade mobile
- [ ] Adicionar tooltips e help text
- [ ] Atualizar README.md com instruções completas
- [ ] Screenshots para documentação
- [ ] Criar arquivo `docs/USAGE.md` com exemplos
- [ ] Code cleanup e refactoring
- [ ] Adicionar comentários em código complexo
- [ ] Performance: otimizar queries lentas
- [ ] Validar acessibilidade (contrast, keyboard nav)

#### Entregáveis
- App 100% funcional
- README atualizado
- Docs completos
- Código limpo e comentado

---

## 📊 Progresso Geral

| Sprint | Status | Progresso | Estimativa | Real |
|--------|--------|-----------|------------|------|
| Sprint 0 | ✅ Completo | 100% | 1h | 1.5h |
| Sprint 1 | ✅ Completo | 100% | 1-2h | 0.5h |
| Sprint 2 | ✅ Completo | 100% | 2-3h | 1h |
| Sprint 3 | ✅ Completo | 100% | 3-4h | 1.5h |
| Sprint 4 | ✅ Completo | 100% | 4-5h | 2h |
| Sprint 5 | ✅ Completo | 100% | 4-5h | 1h |
| Sprint 6 | ✅ Completo | 100% | 3-4h | 0.5h |
| Sprint 7 | ✅ Completo | 100% | 2-3h | 0.5h |
| Sprint 8 | ✅ Completo | 100% | 2-3h | 0.5h |
| Sprint 9 | 🟡 Próximo | 0% | 2-3h | - |
| **TOTAL** | | **80%** | **24-32h** | **9h** |

---

## 🎨 Decisões de Design

### UI/UX
- ✅ Tema escuro por padrão
- ✅ Status visual: 🟢 verde (success), 🔴 vermelho (failed), 🟠 laranja (paused)
- ✅ Auto-refresh: 5s (Overview e Jobs page)
- ✅ File tree: refresh apenas quando na página (evita overhead)
- ✅ Mobile-responsive
- ✅ Bootstrap 5 + CSS custom

### Backend
- ✅ SQLite (simples, file-based)
- ✅ APScheduler BackgroundScheduler
- ✅ Execução no host (sem Docker)
- ✅ Timeout padrão: 300s (5min)
- ✅ Retry padrão: 3x com 60s delay
- ✅ Output limit: 50KB
- ✅ Upload limit: 5MB (arquivo único)

### File Management
- ✅ Tracked directories: usuário pode adicionar múltiplos dirs
- ✅ File tree: lista apenas .py, filtra venv/.git/__pycache__
- ✅ Uploads: salvos em `backend/uploads/` com UUID prefix
- ✅ Deduplicação: hash SHA256 dos uploads

### Segurança
- ⚠️ Execução no host: risco moderado (apenas para usuários confiáveis)
- ✅ Path sanitization: prevenir directory traversal
- ✅ Blacklist de imports perigosos: opcional (não implementado no MVP)
- ✅ Timeout obrigatório: prevenir loops infinitos
- ✅ Output limit: prevenir memory exhaustion

---

## 📝 Notas de Implementação

### Próximos Passos (Sprint 1)
1. Criar `backend/core/database.py` com SQLAlchemy setup
2. Criar models em `backend/core/models.py`
3. Criar schemas Pydantic em `backend/core/schemas.py`
4. Criar script `backend/init_db.py`
5. Testar criação de DB e tabelas

### Dependências Adicionais
- ✅ dash, plotly, dash-bootstrap-components
- ✅ apscheduler
- ✅ sqlalchemy
- ✅ python-dotenv
- ✅ pydantic
- ✅ croniter

---

## 🐛 Issues & Bugs Conhecidos

_Nenhum no momento_

---

## 💡 Ideias Futuras (Backlog)

- [ ] Autenticação (login/logout)
- [ ] Multi-user com permissões
- [ ] Execução em Docker containers (sandbox)
- [ ] Dependencies entre jobs (DAG)
- [ ] Notificações (email/webhook/Slack)
- [ ] Secrets management
- [ ] API REST externa com auth
- [ ] Tema claro/escuro toggle
- [ ] Internacionalização (i18n)
- [ ] Monitoring: Prometheus/Grafana
- [ ] Backup/restore automático do DB
- [ ] Import/export jobs (JSON/YAML)

---

**Última atualização:** 2025-12-07 (Sprint 2 completo, iniciando Sprint 3)

**Status atual:** App rodando com UI completa, navbar, páginas e tema escuro. Próximo: implementar Overview page com dados dinâmicos.
