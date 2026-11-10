import sqlite3

def init_db():
    conn = sqlite3.connect('shop_pi_pos.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            Role TEXT,
            Username TEXT PRIMARY KEY,
            Name TEXT,
            Location TEXT,
            Phone TEXT,
            PiWalletAddress TEXT,
            ProfilePic TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dealer_catalog (
            Barcode TEXT,
            DealerName TEXT,
            ItemName TEXT,
            PRIMARY KEY (Barcode, DealerName)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            ItemCode TEXT PRIMARY KEY,
            Item TEXT,
            BuyingPrice REAL,
            Price REAL,
            Stock INTEGER,
            FreeItems INTEGER,
            ReorderLevel INTEGER,
            Branch TEXT,
            Dealer TEXT,
            Synced TEXT DEFAULT 'No'
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS live_stock_shop (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ShopName TEXT,
            Location TEXT,
            DealerName TEXT,
            ItemName TEXT,
            Price REAL,
            StockIn INTEGER DEFAULT 0,
            Sales INTEGER DEFAULT 0,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dealer_deliveries (
            DeliveryID INTEGER PRIMARY KEY AUTOINCREMENT,
            ShopName TEXT,
            Location TEXT,
            DealerName TEXT,
            ItemName TEXT,
            Quantity INTEGER,
            UnitPrice REAL,
            TotalAmount REAL,
            DeliveryTime TEXT,
            DateStamp TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS promotions (
            PromoID INTEGER PRIMARY KEY AUTOINCREMENT,
            ShopName TEXT,
            ItemCode TEXT,
            ItemName TEXT,
            OriginalPrice REAL,
            DiscountPercent INTEGER,
            NewPrice REAL,
            DurationDays INTEGER,
            Status TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PiUser TEXT,
            ShopName TEXT,
            Time TEXT,
            Type TEXT,
            Amount TEXT,
            Status TEXT,
            Synced TEXT DEFAULT 'No'
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            BranchName TEXT PRIMARY KEY
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS staff_users (
            Username TEXT PRIMARY KEY,
            Pin TEXT,
            Role TEXT,
            Branch TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerUsername TEXT,
            ShopName TEXT,
            ReferralCode TEXT UNIQUE,
            Ref1 TEXT DEFAULT '',
            Ref2 TEXT DEFAULT '',
            Ref3 TEXT DEFAULT '',
            Income REAL DEFAULT 0.0
        )
    ''')
    
    c.execute('SELECT COUNT(*) FROM branches')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO branches VALUES ('Matara Main')")
        c.execute("INSERT INTO branches VALUES ('Tangalle Branch')")
        
    c.execute('SELECT COUNT(*) FROM dealer_catalog')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO dealer_catalog VALUES (?, ?, ?)', [
            ("BAR001", "Global Foods Ltd (Matara)", "Maliban Chocolate Biscuit 400g"),
            ("BAR002", "Global Foods Ltd (Matara)", "Munchee Lemon Puff 200g")
        ])

    conn.commit()
    return conn