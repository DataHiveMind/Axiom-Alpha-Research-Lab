/ Axiom-Alpha-Research-Lab: Master Ticker Plant (tick.q)
/ Core Engine: Ingests data, writes to transaction log, and publishes to the RDB.

/ Load the master schema
\l sym.q

/ -------------------------------------------------------------------------
/ 1. Initialization & State Management
/ -------------------------------------------------------------------------

.u.w: ()!()                  / Dictionary holding all subscribers by table
.u.i: 0j                     / Message counter for sequence tracking
.u.d: .z.D                   / Current system date
.u.L: `$":./hdb/tplog_",string[.u.d]  / Path to today's transaction log

/ Create and open the transaction log file
.[`u.l;();:;hopen .u.L];

/ -------------------------------------------------------------------------
/ 2. Subscription Engine
/ -------------------------------------------------------------------------

/ Called by the RDB (or your Python dashboard) to subscribe to a live feed
.u.sub:{[tbl; symList]
    / If table isn't registered yet, initialize it
    if[not tbl in keys .u.w; .u.w[tbl]:()];
    
    / Add the subscriber's handle (.z.w) to the list for this table
    .u.w[tbl],: enlist(.z.w; symList);
    
    / Return the schema so the subscriber can initialize their local table
    (tbl; value tbl)
    };

/ -------------------------------------------------------------------------
/ 3. Publishing Engine (The Core Loop)
/ -------------------------------------------------------------------------

/ Pushes data asynchronously to all active subscribers
.u.pub:{[tbl; data]
    / Iterate through subscribers and push the 'upd' message via negative handle
    {[tbl; data; subHandle] 
        if[count data; (neg first subHandle)(`upd; tbl; data)] 
    }[tbl; data] each .u.w[tbl];
    };

/ The main update function called by your external data feeds (via PyKX)
upd:{[tbl; data]
    .u.i+: 1;                   / Increment message count
    .u.l enlist(`upd;tbl;data); / Append async to the transaction log file
    .u.pub[tbl; data];          / Broadcast to the RDB and Python models
    };

/ -------------------------------------------------------------------------
/ 4. End of Day (EOD) Rollover
/ -------------------------------------------------------------------------

/ Triggered at midnight (or market close) to roll the logs and reset
.u.end:{[date]
    .u.d: date + 1;
    hclose .u.l;                               / Close yesterday's log
    .u.L: `$":./hdb/tplog_",string[.u.d];      / Create today's log name
    .[`u.l;();:;hopen .u.L];                   / Open new log
    
    / Send EOD signal to all subscribers so the RDB knows to save to disk
    {[handle] (neg first handle)(`.u.end; date)} each distinct raze .u.w;
    };

/ -------------------------------------------------------------------------
-1 ">>> Axiom Ticker Plant initialized. Listening for feeds...";