from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

settings = get_settings()

# SQLite requires check_same_thread, PostgreSQL does not
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and handle schema migrations."""
    Base.metadata.create_all(bind=engine)
    
    # Handle schema migrations for existing SQLite databases
    if settings.database_url.startswith("sqlite"):
        _run_migrations()


def _run_migrations():
    """Run schema migrations for SQLite database."""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    # Get list of existing tables
    existing_tables = inspector.get_table_names()
    
    # Migration: Add user_id and credits_charged to generations table
    if 'generations' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('generations')]
        
        with engine.connect() as conn:
            if 'user_id' not in columns:
                conn.execute(text('ALTER TABLE generations ADD COLUMN user_id INTEGER'))
                conn.commit()
                print("Migration: Added user_id column to generations table")
            
            if 'credits_charged' not in columns:
                conn.execute(text('ALTER TABLE generations ADD COLUMN credits_charged INTEGER'))
                conn.commit()
                print("Migration: Added credits_charged column to generations table")
    
    # Migration: Create users table if it doesn't exist
    if 'users' not in existing_tables:
        with engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    credits_balance INTEGER DEFAULT 0,
                    total_credits_purchased INTEGER DEFAULT 0,
                    total_credits_used INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            conn.commit()
            print("Migration: Created users table")
            
            # Create default demo user
            conn.execute(text('''
                INSERT INTO users (id, email, credits_balance, total_credits_purchased)
                VALUES (1, 'demo@videlo.ai', 100, 100)
            '''))
            conn.commit()
            print("Migration: Created demo user with 100 credits")
    
    # Migration: Create credit_transactions table if it doesn't exist
    if 'credit_transactions' not in existing_tables:
        with engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE credit_transactions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    generation_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (generation_id) REFERENCES generations(id)
                )
            '''))
            conn.commit()
            print("Migration: Created credit_transactions table")
    
    # Migration: Create credit_packages table if it doesn't exist
    if 'credit_packages' not in existing_tables:
        with engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE credit_packages (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    credits INTEGER NOT NULL,
                    price_cents INTEGER NOT NULL,
                    bonus_percent INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            conn.commit()
            print("Migration: Created credit_packages table")
