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
    
    # Migration: Add user_id and credits_charged to generations table (run once)
    if 'generations' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('generations')]
        
        with engine.connect() as conn:
            if 'user_id' not in columns:
                conn.execute(text('ALTER TABLE generations ADD COLUMN user_id INTEGER'))
                conn.commit()
            
            if 'credits_charged' not in columns:
                conn.execute(text('ALTER TABLE generations ADD COLUMN credits_charged INTEGER'))
                conn.commit()
            
            if 'local_path' not in columns:
                conn.execute(text('ALTER TABLE generations ADD COLUMN local_path VARCHAR'))
                conn.commit()
    
    # Migration: Create users table if it doesn't exist (run once)
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
            
            # Create default demo user
            conn.execute(text('''
                INSERT INTO users (id, email, credits_balance, total_credits_purchased)
                VALUES (1, 'demo@videlo.ai', 100, 100)
            '''))
            conn.commit()
    
    # Migration: Create credit_transactions table if it doesn't exist (run once)
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
    
    # Migration: Create credit_packages table if it doesn't exist (run once)
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
    
    # Migration: Create ad-related tables if they don't exist
    # NOTE: We use CREATE TABLE IF NOT EXISTS to preserve existing data
    with engine.connect() as conn:
        # ad_campaigns - multi-phase schema
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ad_campaigns (
                id INTEGER PRIMARY KEY,
                user_prompt TEXT NOT NULL,
                current_phase INTEGER DEFAULT 1,
                phase_status VARCHAR(50) DEFAULT 'pending',
                clarification_questions JSON,
                user_answers JSON,
                context JSON,
                ad_angles JSON,
                num_scripts INTEGER DEFAULT 5,
                num_avatars INTEGER DEFAULT 3,
                scripts_status VARCHAR(50) DEFAULT 'pending',
                avatars_status VARCHAR(50) DEFAULT 'pending',
                storyboards_status VARCHAR(50) DEFAULT 'pending',
                image_prompts_status VARCHAR(50) DEFAULT 'pending',
                video_prompts_status VARCHAR(50) DEFAULT 'pending',
                iteration_count INTEGER DEFAULT 0,
                last_iteration_command TEXT,
                overall_status VARCHAR(50) DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        '''))
        conn.commit()
        
        # ad_avatars
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ad_avatars (
                id INTEGER PRIMARY KEY,
                campaign_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                age INTEGER,
                gender VARCHAR(20),
                region VARCHAR(50),
                appearance TEXT,
                outfit_style TEXT,
                personality_vibe TEXT,
                appearance_locked BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES ad_campaigns(id)
            )
        '''))
        conn.commit()
        
        # ad_scripts
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ad_scripts (
                id INTEGER PRIMARY KEY,
                campaign_id INTEGER NOT NULL,
                script_id INTEGER NOT NULL,
                hook TEXT NOT NULL,
                cta TEXT,
                framework VARCHAR(50),
                scenes JSON NOT NULL,
                avatar_id INTEGER,
                ad_angle_ref INTEGER,
                version INTEGER DEFAULT 1,
                iteration_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES ad_campaigns(id),
                FOREIGN KEY (avatar_id) REFERENCES ad_avatars(id)
            )
        '''))
        conn.commit()
        
        # ad_storyboards
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ad_storyboards (
                id INTEGER PRIMARY KEY,
                campaign_id INTEGER NOT NULL,
                script_id INTEGER NOT NULL,
                scenes JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES ad_campaigns(id),
                FOREIGN KEY (script_id) REFERENCES ad_scripts(id)
            )
        '''))
        conn.commit()
        
        # ad_scene_prompts
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ad_scene_prompts (
                id INTEGER PRIMARY KEY,
                storyboard_id INTEGER NOT NULL,
                scene_num INTEGER NOT NULL,
                image_prompt TEXT,
                image_generation_id INTEGER,
                image_url VARCHAR,
                image_status VARCHAR(50) DEFAULT 'pending',
                video_prompt TEXT,
                video_generation_id INTEGER,
                video_url VARCHAR,
                video_status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (storyboard_id) REFERENCES ad_storyboards(id),
                FOREIGN KEY (image_generation_id) REFERENCES generations(id),
                FOREIGN KEY (video_generation_id) REFERENCES generations(id)
            )
        '''))
        conn.commit()
        
        # ad_conversations
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ad_conversations (
                id INTEGER PRIMARY KEY,
                campaign_id INTEGER NOT NULL,
                role VARCHAR(20) NOT NULL,
                phase INTEGER,
                content TEXT NOT NULL,
                message_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES ad_campaigns(id)
            )
        '''))
        conn.commit()
        
        # ai_avatar_projects - AI Video Avatar Pipeline
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ai_avatar_projects (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                portrait_prompt TEXT NOT NULL,
                speech_text TEXT NOT NULL,
                motion_prompt TEXT,
                voice_model VARCHAR(50) DEFAULT 'Kokoro',
                voice_id VARCHAR(50) DEFAULT 'af_sky',
                voice_speed REAL DEFAULT 1.0,
                voice_lang VARCHAR(20) DEFAULT 'en-us',
                portrait_model VARCHAR(50) DEFAULT 'Flux_2_Klein_4B_BF16',
                portrait_width INTEGER DEFAULT 512,
                portrait_height INTEGER DEFAULT 512,
                animation_model VARCHAR(50) DEFAULT 'Ltx2_3_22B_Dist_INT8',
                animation_frames INTEGER DEFAULT 97,
                animation_fps INTEGER DEFAULT 24,
                portrait_request_id VARCHAR,
                portrait_url VARCHAR,
                portrait_generation_id INTEGER,
                portrait_status VARCHAR(50) DEFAULT 'pending',
                audio_request_id VARCHAR,
                audio_url VARCHAR,
                audio_generation_id INTEGER,
                audio_status VARCHAR(50) DEFAULT 'pending',
                video_request_id VARCHAR,
                video_url VARCHAR,
                video_generation_id INTEGER,
                video_status VARCHAR(50) DEFAULT 'pending',
                current_step INTEGER DEFAULT 1,
                overall_status VARCHAR(50) DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (portrait_generation_id) REFERENCES generations(id),
                FOREIGN KEY (audio_generation_id) REFERENCES generations(id),
                FOREIGN KEY (video_generation_id) REFERENCES generations(id)
            )
        '''))
        conn.commit()
    
    # Migration: Add request_id columns to ai_avatar_projects if they don't exist
    if 'ai_avatar_projects' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('ai_avatar_projects')]
        
        with engine.connect() as conn:
            if 'portrait_request_id' not in columns:
                conn.execute(text('ALTER TABLE ai_avatar_projects ADD COLUMN portrait_request_id VARCHAR'))
                conn.commit()
            
            if 'audio_request_id' not in columns:
                conn.execute(text('ALTER TABLE ai_avatar_projects ADD COLUMN audio_request_id VARCHAR'))
                conn.commit()
            
            if 'video_request_id' not in columns:
                conn.execute(text('ALTER TABLE ai_avatar_projects ADD COLUMN video_request_id VARCHAR'))
                conn.commit()
