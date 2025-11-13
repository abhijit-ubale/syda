# 🏭 SYDA Production Application Flow (End-to-End Architecture)

This document explains the complete execution flow of the production-grade SYDA synthetic data generation library, from library initialization through final data output.

---

## 🎬 Complete System Architecture

```mermaid
graph TB
    subgraph "Client Code"
        A["User Application<br/>(User writes code)"]
    end
    
    subgraph "SYDA Library Layer 1: Initialization"
        B["SyntheticDataGenerator<br/>.__init__()"]
        C["ModelConfig<br/>(AI settings)"]
        D["LLMClient<br/>(AI provider)"]
    end
    
    subgraph "SYDA Library Layer 2: Input Processing"
        E["SchemaLoader<br/>(Parse schemas)"]
        F["validate_schema()<br/>(Validate input)"]
        G["Schema Normalization"]
    end
    
    subgraph "SYDA Library Layer 3: Dependency Analysis"
        H["DependencyHandler<br/>(Analyze relationships)"]
        I["ForeignKeyHandler<br/>(Extract FK rules)"]
        J["NetworkX Graph<br/>(Build dependency graph)"]
    end
    
    subgraph "SYDA Library Layer 4: Data Generation"
        K["GeneratorManager<br/>(Setup generators)"]
        L["LLM API Calls<br/>(Claude/GPT/Gemini)"]
        M["Structured Output<br/>(Parse LLM response)"]
        N["Custom Generators<br/>(Apply business logic)"]
    end
    
    subgraph "SYDA Library Layer 5: Data Integrity"
        O["Foreign Key<br/>Validation"]
        P["Referential Integrity<br/>Check"]
        Q["DataFrame Assembly"]
    end
    
    subgraph "SYDA Library Layer 6: Output"
        R["output.py<br/>(Save data)"]
        S["CSV/JSON Files<br/>(Output format)"]
    end
    
    subgraph "Return to Client"
        T["Dictionary of<br/>DataFrames"]
        U["Results Dictionary"]
    end
    
    A -->|1. Initialize| B
    B -->|2. Setup AI| D
    B -->|3. Get config| C
    A -->|4. Pass schemas| E
    E -->|5. Parse| F
    F -->|6. Normalize| G
    G -->|7. Analyze deps| H
    H -->|8. Extract FKs| I
    I -->|9. Build graph| J
    J -->|10. Order generation| K
    K -->|11. Setup generators| L
    L -->|12. Call LLM APIs| M
    M -->|13. Parse responses| N
    N -->|14. Apply custom| O
    O -->|15. Validate FKs| P
    P -->|16. Assemble| Q
    Q -->|17. Save| R
    R -->|18. Write files| S
    Q -->|19. Return| T
    T -->|20. Process| U
    
    style A fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style B fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style D fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style E fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style H fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style K fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style L fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style O fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style R fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style T fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

---

## 📊 Detailed Production Flow - Phase by Phase

### **PHASE 1: Library Initialization** 🚀

```mermaid
graph TD
    A["User Code:<br/>from syda import SyntheticDataGenerator<br/>generator = SyntheticDataGenerator()"] --> B["__init__() called"]
    B --> C["Validate/Create ModelConfig"]
    C --> D["Create LLMClient"]
    D --> E["initialize_client()"]
    E --> F{Which AI Provider?}
    F -->|OpenAI| G["Initialize OpenAI Client<br/>with API Key"]
    F -->|Anthropic| H["Initialize Anthropic Client<br/>with API Key"]
    F -->|Gemini| I["Initialize Gemini Client<br/>with API Key"]
    F -->|Azure OpenAI| J["Initialize Azure Client<br/>with Custom Endpoint"]
    F -->|Grok| K["Initialize Grok Client<br/>with xAI API"]
    G -->|Patch| L["Apply Instructor Wrapper"]
    H -->|Patch| L
    I -->|Patch| L
    J -->|Patch| L
    K -->|Patch| L
    L --> M["Store client in LLMClient"]
    M --> N["Create GeneratorManager"]
    N --> O["Create ForeignKeyHandler"]
    O --> P["Create SchemaLoader"]
    P --> Q["✅ SyntheticDataGenerator Ready"]
    
    style A fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style Q fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style F fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style G fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style H fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style I fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style J fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style K fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style L fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
```

**What Happens:**
- **LLMClient** connects to your chosen AI provider
- **Instructor** patches the client for structured output
- **GeneratorManager** prepares custom data generators
- **SchemaLoader** gets ready to parse schemas

---

### **PHASE 2: Schema Input & Validation** 📋

```mermaid
graph TD
    A["User Input:<br/>generate_for_schemas()"] --> B["schemas parameter can be:<br/>1. Dict<br/>2. YAML/JSON files<br/>3. SQLAlchemy models"]
    B --> C["SchemaLoader.load_schema()"]
    C --> D{Input Type?}
    D -->|Dictionary| E["_load_dict_schema()"]
    D -->|File Path| F["_load_schema_file()<br/>Load JSON/YAML"]
    D -->|SQLAlchemy| G["_load_sqlalchemy_model()<br/>Extract from ORM"]
    E -->|Validate| H["validate_schema()"]
    F -->|Validate| H
    G -->|Validate| H
    H --> I{Schema Valid?}
    I -->|NO| J["❌ Raise ValueError<br/>with details"]
    I -->|YES| K["Normalize Schema"]
    K --> L["Extract Metadata"]
    L --> M["Extract Foreign Keys"]
    M --> N["Extract Table Descriptions"]
    N --> O["Build Foreign Key Map"]
    O --> P["✅ Schemas Processed"]
    
    style A fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style P fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style D fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style E fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style F fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style G fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style H fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style J fill:#FF1744,stroke:#FF0040,stroke-width:2px,color:#FFFFFF
```

**Input Options (Production Use Cases):**
```python
# Option 1: Dictionary Schema
schemas = {
    'users': {'id': {'type': 'number'}, 'name': {'type': 'text'}},
    'orders': {'id': {'type': 'number'}, 'user_id': {'type': 'foreign_key'}}
}

# Option 2: YAML/JSON Files (Enterprise common)
schemas = {
    'users': 'schemas/users.yml',
    'orders': 'schemas/orders.json'
}

# Option 3: SQLAlchemy Models (ORM-based - Production common)
schemas = generate_for_sqlalchemy_models(
    sqlalchemy_models=[User, Order, Product],
    ...
)
```

---

### **PHASE 3: Dependency Analysis & Ordering** 🔗

```mermaid
graph TD
    A["Processed Schemas<br/>+ Foreign Keys"] --> B["DependencyHandler<br/>.analyze_dependencies()"]
    B --> C["Extract Foreign Key Relationships<br/>Order → User<br/>OrderItem → Order<br/>OrderItem → Product"]
    C --> D["Build Directed Graph<br/>Using NetworkX"]
    D --> E["Detect Circular<br/>Dependencies?"]
    E -->|YES| F["❌ Raise Error:<br/>Circular dependency"]
    E -->|NO| G["Topological Sort<br/>(Get generation order)"]
    G --> H["Generation Order:<br/>1. User (no deps)<br/>2. Product (no deps)<br/>3. Order (→ User)<br/>4. OrderItem (→ Order, Product)"]
    H --> I["Store Dependency Graph"]
    I --> J["✅ Order Determined"]
    
    style A fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style B fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style D fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style E fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style F fill:#FF1744,stroke:#FF0040,stroke-width:2px,color:#FFFFFF
    style H fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style J fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

**Why This Matters:**
- ⚠️ Can't generate `Order` before `User` exists
- ⚠️ Can't generate `OrderItem` before `Order` and `Product` exist
- ✅ Graph ensures correct generation order EVERY TIME

---

### **PHASE 4: Data Generation Loop** 🎯

```mermaid
graph TD
    subgraph "For Each Schema (in dependency order)"
        A["schema_name = 'users'<br/>sample_size = 100"]
        A --> B["Get sample_size from parameters"]
        B --> C["Get custom prompt<br/>or use default"]
        C --> D["Get/Create custom<br/>generators if provided"]
        D --> E["results = {} dictionary<br/>to store DataFrames"]
    end
    
    subgraph "For Each Row (1 to sample_size)"
        E --> F["row_num = 1"]
        F --> G["row_data = {}"]
        G --> H["For each field in schema"]
        H --> I{Field Type?}
        
        I -->|AI Field| J["Build prompt for AI"]
        I -->|Custom| K["Call custom generator"]
        I -->|Foreign Key| L["Pick from parent table"]
        I -->|Default| M["Use random generator"]
        
        J -->|Stream| N["Call LLM API<br/>stream=True if large dataset"]
        N -->|Parse| O["Extract structured<br/>output with Instructor"]
        K --> P["Apply business logic"]
        L --> P
        M --> P
        O --> P
        
        P -->|Validate| Q["Type checking<br/>Constraint checking"]
        Q -->|Pass| R["row_data[field] = value"]
        Q -->|Fail| S["Retry or use fallback"]
        S --> R
        
        R --> T["All fields done?"]
        T -->|NO| H
        T -->|YES| U["Append row to results"]
        U --> V["row_num++"]
        V --> W{More rows?}
        W -->|YES| F
        W -->|NO| X["✅ Schema complete"]
    end
    
    style A fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style E fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style F fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style I fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style N fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style O fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style X fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

**Example: Generating 100 users**
```
Row 1: id=1, name="John", email="john@..."
Row 2: id=2, name="Sarah", email="sarah@..."
...
Row 100: id=100, name="Michael", email="michael@..."
```

---

### **PHASE 5: Foreign Key Integrity** 🔐

```mermaid
graph TD
    A["Generated Order:<br/>100 rows<br/>user_id = [1, 3, 7, 15, 2, ...]"] --> B["ForeignKeyHandler<br/>.apply_foreign_keys()"]
    B --> C["Get parent table<br/>(User with 100 rows<br/>IDs: 1-100)"]
    C --> D["Register FK Generator:<br/>For each order row<br/>user_id must be 1-100"]
    D --> E["During generation,<br/>for each OrderItem row:"]
    E --> F["Instead of random user_id,<br/>pick from [1-100]"]
    F --> G["Guarantee:<br/>EVERY order.user_id<br/>exists in users.id"]
    G --> H["✅ Referential Integrity<br/>100%"]
    
    style A fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style B fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style D fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style H fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

**Production Guarantee:**
- ❌ NEVER: `order.user_id = 999` when user 999 doesn't exist
- ✅ ALWAYS: All foreign keys point to valid records

---

### **PHASE 6: Output & File Storage** 💾

```mermaid
graph TD
    A["Generated Data:<br/>results = {<br/>  'users': DataFrame 100x5,<br/>  'orders': DataFrame 500x4,<br/>  'order_items': DataFrame 1500x3<br/>}"] --> B["save_dataframes()"]
    B --> C["Create output directory<br/>if not exists"]
    C --> D["For each DataFrame:<br/>save_dataframe()"]
    D --> E{Output Format?}
    E -->|CSV| F["df.to_csv()"]
    E -->|JSON| G["df.to_json()"]
    F --> H["users.csv<br/>orders.csv<br/>order_items.csv"]
    G --> H
    H --> I["Verify files exist"]
    I --> J["Log success:<br/>100 rows → users.csv<br/>500 rows → orders.csv"]
    J --> K["✅ Files Saved"]
    
    style A fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style B fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style E fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style H fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style K fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

**CSV Output Example:**
```csv
# users.csv
id,name,email,created_at,is_active
1,John,john@example.com,2024-01-15,true
2,Sarah,sarah@example.com,2024-01-16,true
...

# orders.csv
id,user_id,total,status
1,1,150.99,completed
2,2,89.50,pending
...
```

---

## 🔄 Complete End-to-End Timeline

```mermaid
graph TD
    A["⏱️ 00:00<br/>User Code:<br/>Initialize generator"] --> B["⏱️ 00:05<br/>Setup ModelConfig"]
    B --> C["⏱️ 00:10<br/>Call generate_for_schemas()"]
    C --> D["⏱️ 00:15<br/>Library Init:<br/>Create LLMClient"]
    D --> E["⏱️ 00:20<br/>Connect to AI provider"]
    E --> F["⏱️ 00:25<br/>Initialize GeneratorManager"]
    F --> G["⏱️ 00:30<br/>Input Processing:<br/>Load schemas"]
    G --> H["⏱️ 00:35<br/>Validate schemas"]
    H --> I["⏱️ 00:40<br/>Normalize structures"]
    I --> J["⏱️ 00:45<br/>Dependency Analysis:<br/>Extract foreign keys"]
    J --> K["⏱️ 00:50<br/>Build dependency graph"]
    K --> L["⏱️ 00:55<br/>Determine generation order"]
    L --> M["⏱️ 01:00<br/>Data Generation:<br/>Generate Schema 1"]
    M --> N["⏱️ 02:00<br/>Generate Schema 2"]
    N --> O["⏱️ 03:00<br/>Generate Schema 3"]
    O --> P["⏱️ 04:30<br/>Generate Schema 4"]
    P --> Q["⏱️ 05:00<br/>Apply custom generators"]
    Q --> R["⏱️ 05:30<br/>Validate all data"]
    R --> S["⏱️ 06:00<br/>FK Validation:<br/>Check referential integrity"]
    S --> T["⏱️ 06:15<br/>Verify all FKs valid"]
    T --> U["⏱️ 06:30<br/>Output:<br/>Assemble DataFrames"]
    U --> V["⏱️ 06:45<br/>Save CSV files"]
    V --> W["⏱️ 07:00<br/>Log success messages"]
    W --> X["⏱️ 07:15<br/>Return results"]
    X --> Y["⏱️ 07:30<br/>Done:<br/>✅ User gets DataFrames"]
    
    style A fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    style D fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style G fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style J fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style M fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style S fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style U fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style Y fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

---

## 📁 Production Module Responsibilities

```mermaid
graph LR
    subgraph "Input Sources"
        I1["Dict Schemas"]
        I2["YAML Files"]
        I3["JSON Files"]
        I4["SQLAlchemy ORM"]
    end
    
    subgraph "SYDA Core Modules"
        A["schema_loader.py<br/>Schema Parsing"] 
        B["generate.py<br/>Core Orchestrator"]
        C["dependency_handler.py<br/>Relationship Analysis"]
        D["custom_generators.py<br/>Data Generation"]
        E["llm.py<br/>AI Integration"]
        F["output.py<br/>File Storage"]
    end
    
    subgraph "AI Providers"
        P1["OpenAI<br/>GPT-4"]
        P2["Anthropic<br/>Claude"]
        P3["Google<br/>Gemini"]
        P4["xAI<br/>Grok"]
        P5["Azure<br/>OpenAI"]
    end
    
    subgraph "Output Formats"
        O1["CSV Files"]
        O2["JSON Files"]
    end
    
    I1 --> A
    I2 --> A
    I3 --> A
    I4 --> A
    
    A --> B
    C --> B
    D --> B
    E --> B
    F --> B
    
    E --> P1
    E --> P2
    E --> P3
    E --> P4
    E --> P5
    
    B --> F
    F --> O1
    F --> O2
    
    style A fill:#DD00FF,stroke:#FF00FF,stroke-width:2px,color:#FFFFFF
    style B fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style C fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style D fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style E fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style F fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
    
    style I1 fill:#3A86FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style I2 fill:#3A86FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style I3 fill:#3A86FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style I4 fill:#3A86FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    
    style P1 fill:#8B00FF,stroke:#AA00FF,stroke-width:2px,color:#FFFFFF
    style P2 fill:#8B00FF,stroke:#AA00FF,stroke-width:2px,color:#FFFFFF
    style P3 fill:#8B00FF,stroke:#AA00FF,stroke-width:2px,color:#FFFFFF
    style P4 fill:#8B00FF,stroke:#AA00FF,stroke-width:2px,color:#FFFFFF
    style P5 fill:#8B00FF,stroke:#AA00FF,stroke-width:2px,color:#FFFFFF
    
    style O1 fill:#00FF88,stroke:#00CC66,stroke-width:2px,color:#000000
    style O2 fill:#00FF88,stroke:#00CC66,stroke-width:2px,color:#000000
```

---

## 🚨 Error Handling & Recovery

```mermaid
graph TD
    A["Data Generation<br/>in Progress"] --> B{Error<br/>Detected?}
    
    B -->|Invalid Schema| C["ValidationError<br/>with details"]
    B -->|LLM Timeout| D["Retry with<br/>exponential backoff"]
    B -->|FK Mismatch| E["referential_integrity_error<br/>with context"]
    B -->|API Error| F["Re-authenticate<br/>or fallback provider"]
    B -->|No Data| G["ValueError:<br/>Empty DataFrame"]
    
    D -->|Retry 1| H{Success?}
    H -->|YES| I["Continue<br/>generation"]
    H -->|NO| J["Retry 2"]
    J -->|Retry 2| K{Success?}
    K -->|YES| I
    K -->|NO| L["Max retries<br/>reached"]
    L -->|Fallback| M["Use default<br/>generator"]
    M --> I
    
    C -->|Log Error| N["Raise to user<br/>with hints"]
    E -->|Log Error| N
    F -->|Log Error| N
    G -->|Log Error| N
    
    I -->|Continue| O["✅ Resume"]
    
    style A fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style B fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style C fill:#FF1744,stroke:#FF0040,stroke-width:2px,color:#FFFFFF
    style D fill:#FF6600,stroke:#FF7700,stroke-width:2px,color:#FFFFFF
    style O fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

---

## 🎯 Production Configuration Options

```mermaid
graph LR
    A["ModelConfig"] --> B{Provider}
    
    B -->|OpenAI| C["GPT-4<br/>GPT-3.5<br/>Custom models"]
    B -->|Anthropic| D["Claude 3.5 Sonnet<br/>Claude 3 Opus<br/>Haiku"]
    B -->|Gemini| E["Gemini 2.0<br/>Gemini Pro<br/>Advanced"]
    B -->|Grok| F["Grok-3<br/>Latest"]
    B -->|Azure| G["Custom<br/>Endpoint<br/>Deployments"]
    
    C -->|Settings| H["temperature<br/>max_tokens<br/>seed"]
    D -->|Settings| H
    E -->|Settings| H
    F -->|Settings| H
    G -->|Settings| H
    
    H --> I["Streaming<br/>mode"]
    I --> J["✅ Ready<br/>for production"]
    
    style A fill:#00DDFF,stroke:#00FFFF,stroke-width:2px,color:#000000
    style B fill:#FFDD00,stroke:#FFFF00,stroke-width:2px,color:#000000
    style C fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style D fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style E fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style F fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style G fill:#0077FF,stroke:#0088FF,stroke-width:2px,color:#FFFFFF
    style J fill:#22DD22,stroke:#00FF00,stroke-width:2px,color:#000000
```

---

## 📊 Production Use Case Examples

### **Use Case 1: E-Commerce Dataset Generation** 🛒
```
Dependency Order:
1. Categories (100 rows) → No dependencies
2. Products (1000 rows) → FK to Categories
3. Customers (500 rows) → No dependencies
4. Orders (5000 rows) → FK to Customers
5. OrderItems (15000 rows) → FK to Orders, Products
6. Reviews (3000 rows) → FK to Products, Customers

Total: 24,600 rows with PERFECT referential integrity
All generated in ~5-10 minutes
```

### **Use Case 2: Healthcare Dataset (HIPAA Compliant)** 🏥
```
Dependency Order:
1. Patients (1000 rows) → No dependencies
2. Doctors (50 rows) → No dependencies
3. Hospitals (10 rows) → No dependencies
4. Appointments (5000 rows) → FK to Patients, Doctors, Hospitals
5. MedicalRecords (2000 rows) → FK to Patients, Doctors
6. Prescriptions (8000 rows) → FK to Patients, Doctors

Sensitive data NEVER exposed, fully synthetic
All referential integrity guaranteed
```

### **Use Case 3: Financial Dataset** 💰
```
Dependency Order:
1. Accounts (200 rows) → No dependencies
2. Customers (200 rows) → FK to Accounts
3. Transactions (10000 rows) → FK to Accounts
4. Cards (300 rows) → FK to Accounts
5. Disputes (50 rows) → FK to Transactions, Cards

Complex relationships handled automatically
All transactions reconcile perfectly
```

---

## ✅ Production Guarantees

| Guarantee | Implementation |
|-----------|-----------------|
| **Referential Integrity** | FK handler validates all foreign keys |
| **No Orphaned Records** | Dependency ordering ensures parent exists first |
| **Deterministic Output** | Optional seed parameter for reproducibility |
| **Type Safety** | Pydantic validation on all inputs |
| **Error Reporting** | Detailed error messages with suggestions |
| **API Resilience** | Retry logic with exponential backoff |
| **Multi-Provider** | Switch between AI providers without code change |
| **Scaling** | Handles thousands of rows efficiently |
| **Privacy** | No real data exposed, fully synthetic |
| **Extensibility** | Custom generators for business logic |

---

## 🎬 Quick Reference: Call Stack

```
User Code
  └─ generator.generate_for_schemas()
      ├─ SchemaLoader.load_schema()
      │   └─ validate_schema()
      ├─ DependencyHandler.analyze_dependencies()
      │   └─ Build NetworkX graph & topological sort
      ├─ For each schema (in dependency order):
      │   ├─ For each row:
      │   │   ├─ For each field:
      │   │   │   ├─ Check if FK → ForeignKeyHandler
      │   │   │   ├─ Check if custom → GeneratorManager
      │   │   │   └─ Otherwise → LLMClient.call_llm()
      │   │   │       └─ instructor.parse_response()
      │   │   └─ Append row to results
      │   └─ Apply foreign key constraints
      ├─ Validate referential integrity
      ├─ save_dataframes()
      │   └─ save_dataframe() for each table
      └─ Return results dictionary
```

---

That's the complete production-grade SYDA flow! 🚀

