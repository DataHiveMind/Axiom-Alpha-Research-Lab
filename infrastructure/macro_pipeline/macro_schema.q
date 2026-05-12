/ Axiom-Alpha: Macroeconomic Event Schema
/ Stores structured data extracted from central bank PDFs and HTML tables

macro_events: ([] 
    time: `timestamp$();       / Exact time of release/scrape
    indicator: `symbol$();     / e.g., `US_CPI, `FOMC_RATE
    actual_val: `float$();     / The published number
    consensus_val: `float$();  / What the market expected
    sentiment_score: `float$() / NLP score from parsed PDF text
    );

/ Function to upsert new macro data from Python/Robocorp
insert_macro:{[t; i; a; c; s]
    `macro_events insert (t; i; a; c; s);
    0N!"✅ Macro Event Ingested: ", string[i];
    };