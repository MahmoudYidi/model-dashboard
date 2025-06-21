import pandas as pd
import numpy as np
from datetime import datetime

def run_model():
    """Sample model that generates dummy data"""
    # Generate sample data
    np.random.seed(42)
    size = 100
    data = pd.DataFrame({
        'date': pd.date_range(start=datetime.today(), periods=size),
        'value': np.random.normal(100, 10, size),
        'category': np.random.choice(['A', 'B', 'C'], size)
    })
    
    # Calculate some metrics
    metrics = {
        'mean': data['value'].mean(),
        'std': data['value'].std(),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return {
        'metrics': metrics,
        'data': data,
        'status': 'success'
    }