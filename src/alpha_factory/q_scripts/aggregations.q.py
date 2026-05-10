/ Axiom-Alpha-Research-Lab: Vectorized Feature Aggregations
/ These functions are executed directly inside the kdb+ memory space.

/ Calculate Order Book Imbalance (OBI) from Quote data
/ OBI = (BidSize - AskSize) / (BidSize + AskSize)
calc_obi:{[quote_table]
    update obi:(bsize - asize) % (bsize + asize) from quote_table
    };

/ Calculate Volume Weighted Average Price (VWAP) over a specific time window
/ x is the trades table, w is the window size (e.g., 5v for 5-minute bars)
calc_vwap_bars:{[trade_table; window]
    select vwap: wavg[size; price], total_volume: sum size 
    by sym, window xbar time.minute 
    from trade_table
    };

/ Calculate Micro-Price (price weighted by opposite side depth)
calc_micro_price:{[quote_table]
    update mprice: ((bid * asize) + (ask * bsize)) % (bsize + asize) from quote_table
    };