# HAZOP Software - System Architecture Diagram

## Complete System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer - React + TypeScript"
        UI1[Studies Management]
        UI2[HAZOP Worksheet]
        UI3[Dashboard & Analytics]
        UI4[P&ID Viewer]

        UI1 --> |Create/List/Navigate| Router[React Router]
        UI2 --> |Interactive Analysis| Router
        UI3 --> |Visual Reports| Router
        UI4 --> |PDF Rendering| Router

        subgraph "UI Components"
            C1[Metric Cards]
            C2[Charts - Donut/Bar]
            C3[AI Insights Panel]
            C4[Risk Matrix]
            C5[Node Markers]
            C6[Excel Export]
        end
    end

    Router --> |HTTPS/REST API| Gateway[API Gateway - FastAPI]

    subgraph "Backend Layer - Python FastAPI"
        Gateway --> Auth[Auth API - JWT]
        Gateway --> StudyAPI[Studies API]
        Gateway --> HAZOPAPI[HAZOP API]
        Gateway --> GeminiAPI[Gemini AI API]
        Gateway --> DashAPI[Dashboard API]
        Gateway --> ExportAPI[Export API]
        Gateway --> PIDAPI[P&ID API]

        subgraph "Business Services"
            GeminiSvc[Gemini Service<br/>Async + ThreadPool]
            ExcelSvc[Excel Service<br/>OpenPyXL]
            AggSvc[Aggregation Service<br/>Metrics & Stats]
        end

        GeminiAPI --> GeminiSvc
        ExportAPI --> ExcelSvc
        DashAPI --> AggSvc
    end

    subgraph "Data Layer - PostgreSQL"
        DB[(PostgreSQL Database)]

        subgraph "Core Tables"
            T1[users]
            T2[hazop_studies]
            T3[hazop_nodes]
            T4[deviations]
            T5[causes]
            T6[consequences]
            T7[safeguards]
            T8[recommendations]
            T9[impact_assessments]
            T10[pid_documents]
            T11[node_pid_locations]
        end

        T1 --> |created_by| T2
        T2 --> |1:N| T3
        T3 --> |1:N| T4
        T4 --> |1:N| T5
        T5 --> |1:N| T6
        T6 --> |1:N| T7
        T6 --> |1:N| T8
        T6 --> |1:1| T9
        T3 --> |N:M| T10
        T3 --> |coordinates| T11
    end

    Auth --> |SQLAlchemy ORM| DB
    StudyAPI --> |SQLAlchemy ORM| DB
    HAZOPAPI --> |SQLAlchemy ORM| DB
    AggSvc --> |Query| DB
    PIDAPI --> |Binary Storage| DB

    subgraph "External Services"
        Gemini[Google Gemini AI<br/>gemini-2.5-flash]
    end

    GeminiSvc --> |API Calls| Gemini

    style UI1 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style UI2 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style UI3 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style UI4 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style Gateway fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style DB fill:#10B981,stroke:#059669,color:#fff
    style Gemini fill:#E2E8F0,stroke:#CBD5E1,color:#4B5563
    style GeminiSvc fill:#EF4444,stroke:#DC2626,color:#fff
```

---

## Simplified Data Flow Architecture

```mermaid
flowchart LR
    subgraph Client["👤 User Interface"]
        Browser[Web Browser<br/>React App]
    end

    subgraph API["⚡ API Layer"]
        FastAPI[FastAPI Server<br/>Port 8000]
        JWT[JWT Auth<br/>Middleware]
    end

    subgraph Services["🔧 Business Logic"]
        HAZOP[HAZOP Service<br/>CRUD Operations]
        AI[AI Service<br/>Gemini Integration]
        Export[Export Service<br/>Excel Generation]
        Dashboard[Dashboard Service<br/>Analytics]
    end

    subgraph Data["💾 Data Storage"]
        PostgreSQL[(PostgreSQL<br/>Database)]
        Files[File Storage<br/>P&ID PDFs]
    end

    subgraph External["🌐 External APIs"]
        GeminiAPI[Google Gemini AI<br/>Natural Language AI]
    end

    Browser -->|HTTPS Request| FastAPI
    FastAPI -->|Validate Token| JWT
    JWT -->|Authorized| HAZOP
    JWT -->|Authorized| AI
    JWT -->|Authorized| Export
    JWT -->|Authorized| Dashboard

    HAZOP -->|Read/Write| PostgreSQL
    AI -->|Query Data| PostgreSQL
    AI -->|API Call| GeminiAPI
    Export -->|Fetch Data| PostgreSQL
    Dashboard -->|Aggregate| PostgreSQL
    HAZOP -->|Store PDFs| Files

    PostgreSQL -->|Response| HAZOP
    GeminiAPI -->|Suggestions| AI

    HAZOP -->|JSON Response| Browser
    AI -->|AI Insights| Browser
    Export -->|Excel File| Browser
    Dashboard -->|Metrics/Charts| Browser

    style Browser fill:#3B82F6,stroke:#1E40AF,color:#fff
    style FastAPI fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style PostgreSQL fill:#10B981,stroke:#059669,color:#fff
    style GeminiAPI fill:#E2E8F0,stroke:#CBD5E1,color:#4B5563
```

---

## HAZOP Analysis Workflow

```mermaid
sequenceDiagram
    participant User as 👤 Safety Engineer
    participant UI as 🖥️ Frontend
    participant API as ⚡ Backend API
    participant DB as 💾 Database
    participant AI as 🤖 Gemini AI

    User->>UI: Select Deviation
    UI->>API: GET /api/hazop/deviations/{id}/causes
    API->>DB: Query causes
    DB-->>API: Return causes
    API-->>UI: Causes list
    UI-->>User: Display causes

    User->>UI: Click "AI Insights"
    UI->>UI: Show context form
    User->>UI: Enter context (equipment, fluid, conditions)

    UI->>API: POST /api/gemini/suggest-causes
    Note over API: Validate & Process
    API->>AI: Generate suggestions with context
    Note over AI: NLP Processing<br/>Industry Knowledge<br/>Pattern Matching
    AI-->>API: Return 5 suggestions with confidence
    API->>API: Parse & validate JSON
    API-->>UI: Suggestions array
    UI-->>User: Display AI suggestions

    User->>UI: Click "+" to add suggestion
    UI->>API: POST /api/hazop/causes
    API->>DB: Insert new cause
    DB-->>API: Confirm save
    API-->>UI: Success response
    UI-->>User: Update worksheet (auto-saved)

    Note over User,AI: Time: 3-5 seconds total<br/>vs 15-20 min manual
```

---

## Database Schema Relationships

```mermaid
erDiagram
    USERS ||--o{ HAZOP_STUDIES : creates
    HAZOP_STUDIES ||--o{ HAZOP_NODES : contains
    HAZOP_NODES ||--o{ DEVIATIONS : has
    HAZOP_NODES ||--o{ NODE_PID_LOCATIONS : marked_on
    HAZOP_NODES }o--o{ PID_DOCUMENTS : references

    DEVIATIONS ||--o{ CAUSES : identified
    CAUSES ||--o{ CONSEQUENCES : leads_to
    CONSEQUENCES ||--o{ SAFEGUARDS : mitigated_by
    CONSEQUENCES ||--o{ RECOMMENDATIONS : requires
    CONSEQUENCES ||--|| IMPACT_ASSESSMENTS : assessed_by

    USERS {
        uuid id PK
        string email
        string password_hash
        string full_name
        string role
        timestamp created_at
    }

    HAZOP_STUDIES {
        uuid id PK
        uuid created_by FK
        string title
        string description
        string facility_name
        string status
        timestamp created_at
    }

    HAZOP_NODES {
        uuid id PK
        uuid study_id FK
        string node_number
        string node_name
        string description
        string design_intent
        string status
    }

    DEVIATIONS {
        uuid id PK
        uuid node_id FK
        string parameter
        string guide_word
        string deviation_description
        timestamp created_at
    }

    CAUSES {
        uuid id PK
        uuid deviation_id FK
        string cause_description
        string likelihood
        boolean ai_suggested
        timestamp created_at
    }

    CONSEQUENCES {
        uuid id PK
        uuid deviation_id FK
        uuid cause_id FK
        string consequence_description
        string severity
        string category
        timestamp created_at
    }

    SAFEGUARDS {
        uuid id PK
        uuid consequence_id FK
        string safeguard_description
        string safeguard_type
        string effectiveness
        timestamp created_at
    }

    RECOMMENDATIONS {
        uuid id PK
        uuid consequence_id FK
        string recommendation_description
        string priority
        string responsible_party
        date target_date
        string status
    }

    IMPACT_ASSESSMENTS {
        uuid id PK
        uuid consequence_id FK
        string risk_level
        int likelihood_score
        int severity_score
        string justification
        timestamp created_at
    }

    PID_DOCUMENTS {
        uuid id PK
        uuid study_id FK
        string filename
        string file_path
        timestamp uploaded_at
    }

    NODE_PID_LOCATIONS {
        uuid id PK
        uuid node_id FK
        uuid pid_document_id FK
        float x_coordinate
        float y_coordinate
        int page_number
    }
```

---

## Technology Stack Overview

```mermaid
mindmap
  root((HAZOP Software<br/>Technology Stack))
    Frontend
      React 18.3.1
        TypeScript 5.5
        Vite Build Tool
        TailwindCSS 3.4
      Libraries
        Recharts - Charts
        Axios - HTTP
        React-PDF - Viewer
        Zustand - State
        XLSX - Export
    Backend
      Python 3.11+
        FastAPI 0.115
        SQLAlchemy 2.0
        Pydantic Validation
      Libraries
        OpenPyXL - Excel
        JWT - Auth
        Async/Await
    Database
      PostgreSQL 14+
        ACID Compliant
        Connection Pool
        Foreign Keys
        Indexed Tables
    External
      Google Gemini AI
        gemini-2.5-flash
        NLP Processing
        Context Aware
    DevOps
      Git Version Control
      Environment Config
      Backup Ready
      Docker Ready
```

---

## Feature Module Map

```mermaid
mindmap
  root((HAZOP Software<br/>Features))
    Study Management
      Create Studies
      List Studies
      Navigate Studies
      Delete Studies
      Dashboard Link
    Node Management
      Add Nodes
      Edit Nodes
      Delete Nodes
      Duplicate Nodes
      P&ID Mapping
    Deviation Analysis
      Add Deviations
      Parameters
      Guide Words
      Collapsible UI
      Auto-save
    HAZOP Worksheet
      Causes Analysis
      Consequences
      Safeguards
      Recommendations
      Hierarchical View
    AI Features
      Context Input
      Cause Suggestions
      Consequence Prediction
      Safeguard Recommendations
      Knowledge Base
      Confidence Scoring
    Risk Assessment
      Impact Assessment
      Likelihood Scoring
      Risk Matrix
      Color Coding
      Severity Categories
    P&ID Integration
      PDF Upload
      PDF Viewer
      Node Markers
      Coordinate Storage
      Multi-document
    Dashboard
      Metrics Cards
      Risk Distribution
      Deviation Charts
      Quick Navigation
      Excel Export
    Export & Reports
      Excel Formatted
      Color Coded Risks
      Multi-sheet Support
      Auto-width Columns
      Professional Styling
```

---

## Deployment Architecture (Production Ready)

```mermaid
graph TB
    subgraph "Client Layer"
        Users[👥 Users<br/>Web Browsers]
    end

    subgraph "Load Balancer"
        LB[Nginx/HAProxy<br/>SSL Termination]
    end

    subgraph "Application Servers"
        App1[FastAPI Instance 1<br/>Port 8000]
        App2[FastAPI Instance 2<br/>Port 8001]
        App3[FastAPI Instance 3<br/>Port 8002]
    end

    subgraph "Frontend Hosting"
        CDN[CDN<br/>Static Assets]
        Static[Nginx<br/>React Build]
    end

    subgraph "Database Cluster"
        Primary[(PostgreSQL<br/>Primary)]
        Replica1[(PostgreSQL<br/>Replica 1)]
        Replica2[(PostgreSQL<br/>Replica 2)]
    end

    subgraph "File Storage"
        S3[Object Storage<br/>P&ID Documents]
    end

    subgraph "Caching Layer"
        Redis[(Redis Cache<br/>Session/Data)]
    end

    subgraph "External Services"
        Gemini[Google Gemini AI]
    end

    subgraph "Monitoring"
        Logs[Log Aggregation<br/>ELK Stack]
        Metrics[Metrics<br/>Prometheus]
        Alerts[Alerting<br/>Grafana]
    end

    Users --> LB
    LB --> Static
    Static --> CDN
    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> Primary
    App2 --> Primary
    App3 --> Primary

    Primary --> Replica1
    Primary --> Replica2

    App1 --> Redis
    App2 --> Redis
    App3 --> Redis

    App1 --> S3
    App2 --> S3
    App3 --> S3

    App1 --> Gemini
    App2 --> Gemini
    App3 --> Gemini

    App1 --> Logs
    App2 --> Logs
    App3 --> Logs

    Primary --> Metrics
    App1 --> Metrics

    Metrics --> Alerts

    style Users fill:#3B82F6,stroke:#1E40AF,color:#fff
    style LB fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style Primary fill:#10B981,stroke:#059669,color:#fff
    style Gemini fill:#E2E8F0,stroke:#CBD5E1,color:#4B5563
    style Redis fill:#EF4444,stroke:#DC2626,color:#fff
```

---

## AI Integration Architecture

```mermaid
graph LR
    subgraph "User Input"
        Context[Context Form<br/>• Equipment Type<br/>• Fluid Properties<br/>• Operating Conditions<br/>• Historical Incidents]
    end

    subgraph "Frontend Processing"
        Validation[Input Validation<br/>• Required fields<br/>• Format check]
        API_Call[API Request<br/>POST /api/gemini/suggest]
    end

    subgraph "Backend Processing"
        Auth[JWT Validation]
        Service[Gemini Service<br/>• Prompt Engineering<br/>• Context Formatting]
        ThreadPool[ThreadPoolExecutor<br/>Non-blocking Async]
    end

    subgraph "AI Processing"
        Gemini[Google Gemini AI<br/>• NLP Analysis<br/>• Knowledge Retrieval<br/>• Pattern Matching<br/>• Confidence Scoring]
    end

    subgraph "Response Processing"
        Parse[JSON Parsing<br/>• Extract suggestions<br/>• Validate structure]
        Enrich[Data Enrichment<br/>• Add metadata<br/>• Format response]
    end

    subgraph "User Display"
        UI[Interactive Panel<br/>• Suggestions list<br/>• Confidence badges<br/>• Add buttons]
        Worksheet[HAZOP Worksheet<br/>• Auto-populate<br/>• Save to DB]
    end

    Context --> Validation
    Validation --> API_Call
    API_Call --> Auth
    Auth --> Service
    Service --> ThreadPool
    ThreadPool --> Gemini
    Gemini --> Parse
    Parse --> Enrich
    Enrich --> UI
    UI --> Worksheet

    style Context fill:#3B82F6,stroke:#1E40AF,color:#fff
    style Gemini fill:#E2E8F0,stroke:#CBD5E1,color:#4B5563
    style ThreadPool fill:#EF4444,stroke:#DC2626,color:#fff
    style Worksheet fill:#10B981,stroke:#059669,color:#fff
```

---

## Dashboard Data Aggregation Flow

```mermaid
flowchart TD
    Start[User Opens Dashboard] --> API[GET /api/studies/:id/dashboard]

    API --> Auth{JWT Valid?}
    Auth -->|No| Error[401 Unauthorized]
    Auth -->|Yes| FetchStudy[Fetch Study Info]

    FetchStudy --> Metrics[Calculate Metrics]

    Metrics --> M1[Count Nodes]
    Metrics --> M2[Count Deviations]
    Metrics --> M3[Count Causes]
    Metrics --> M4[Count Consequences]
    Metrics --> M5[Count Safeguards]
    Metrics --> M6[Count Recommendations]

    M1 --> Charts[Generate Chart Data]
    M2 --> Charts
    M3 --> Charts
    M4 --> Charts
    M5 --> Charts
    M6 --> Charts

    Charts --> Risk[Risk Distribution<br/>Critical/High/Medium/Low]
    Charts --> NodeDev[Deviations by Node]
    Charts --> Category[Consequences by Category]

    Risk --> Aggregate[Aggregate Response]
    NodeDev --> Aggregate
    Category --> Aggregate

    Aggregate --> JSON[JSON Response]
    JSON --> Frontend[Render Dashboard]

    Frontend --> Display1[Metric Cards]
    Frontend --> Display2[Donut Chart]
    Frontend --> Display3[Bar Chart]
    Frontend --> Display4[Node Grid]

    style Start fill:#3B82F6,stroke:#1E40AF,color:#fff
    style Aggregate fill:#10B981,stroke:#059669,color:#fff
    style Frontend fill:#8B5CF6,stroke:#6D28D9,color:#fff
```

---

**Note**: These diagrams provide a comprehensive visual representation of the HAZOP software architecture, data flows, and system interactions. Each diagram focuses on a specific aspect of the system for clarity and understanding.
