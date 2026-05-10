import pytest
from src.alpha_factory.kdb_interface import KDBInterface

@pytest.mark.skipif(condition=True, reason="Requires live kdb+ instance")
def test_kdb_connection_and_query():
    """Verifies that the Python layer can execute a .q vector aggregation."""
    interface = KDBInterface(mode="rdb")
    
    # Attempt to pull a simple table back as a Pandas DataFrame
    df = interface.get_order_book_imbalance(["AAPL"])
    
    assert not df.empty
    assert "obi" in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)