-- ============================================
-- MoveRenovateAI（搬装智脑）数据库建表脚本
-- 数据库: PostgreSQL 15+
-- ============================================

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'planning',
    requirements JSONB DEFAULT '{}',
    source_address VARCHAR(500),
    target_address VARCHAR(500),
    moving_date DATE,
    mover_count INTEGER DEFAULT 2,
    house_type VARCHAR(50),
    house_area FLOAT,
    style VARCHAR(50),
    current_state VARCHAR(50),
    total_budget FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清单表
CREATE TABLE checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    checklist_type VARCHAR(30) NOT NULL,
    category VARCHAR(50),
    name VARCHAR(200) NOT NULL,
    total_items INTEGER DEFAULT 0,
    completed_items INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清单项表
CREATE TABLE checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checklist_id UUID NOT NULL REFERENCES checklists(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit VARCHAR(20),
    room VARCHAR(100),
    category VARCHAR(50),
    pack_order INTEGER DEFAULT 0,
    box_number VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'normal',
    is_fragile BOOLEAN DEFAULT FALSE,
    is_valuable BOOLEAN DEFAULT FALSE,
    is_packed BOOLEAN DEFAULT FALSE,
    is_unpacked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算表
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    item_name VARCHAR(200) NOT NULL,
    specifications TEXT,
    unit VARCHAR(20),
    quantity FLOAT DEFAULT 1,
    unit_price FLOAT DEFAULT 0,
    planned_amount FLOAT DEFAULT 0,
    actual_amount FLOAT DEFAULT 0,
    supplier VARCHAR(200),
    purchase_url VARCHAR(500),
    purchase_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 施工阶段表
CREATE TABLE phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    order_index INTEGER NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    estimated_days INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    tasks JSONB DEFAULT '[]',
    checkpoints JSONB DEFAULT '[]',
    is_accepted BOOLEAN DEFAULT FALSE,
    budget FLOAT DEFAULT 0,
    actual_cost FLOAT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话历史表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    project_id UUID REFERENCES projects(id),
    session_id VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 索引
-- ============================================
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_type ON projects(project_type);
CREATE INDEX idx_checklists_project ON checklists(project_id);
CREATE INDEX idx_items_checklist ON checklist_items(checklist_id);
CREATE INDEX idx_budgets_project ON budgets(project_id);
CREATE INDEX idx_phases_project ON phases(project_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
