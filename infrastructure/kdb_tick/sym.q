/ Axiom-Alpha-Research-Lab: Master Schema Definition
/ This defines the tables that will stream into the RL Alpha Factory

/ 1. Trade Data (High-Frequency Executions)
trades:([sym:`symbol$()] time:`timespan$(); price:`float$(); size:`int$(); cond:`char$());

/ 2. Quote Data (Order Book Updates for Slippage Modeling)
quotes:([sym:`symbol$()] time:`timespan$(); bid:`float$(); ask:`float$(); bsize:`int$(); asize:`int$());

/ 3. Derived Causal Features (Calculated live by your Python/PyKX engine)
causal_alpha:([sym:`symbol$()] time:`timespan$(); feature_name:`symbol$(); value:`float$(); signal_strength:`float$());