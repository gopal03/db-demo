-- AlloyDB Columnar Engine setup configuration
SELECT google_columnar_engine.add_resources('Players');
SELECT google_columnar_engine.add_resources('Sessions');
SELECT google_columnar_engine.add_resources('TelemetryEvents');
SELECT google_columnar_engine.add_resources('PlayerPlayedSession');
