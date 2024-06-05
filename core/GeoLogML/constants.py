class Constants:
    LITHOLOGY_COLORS = {
        0: '#e6e208',
        1: '#f2f21d',
        2: '#0b8102',
        3: '#bb4cd0',
        4: '#f75f00',
        5: '#ff7f0e',
        6: '#1f77b4',
        7: '#ff00ff',
        8: '#9467bd',
        9: '#d62728',
        10: '#8c564b'
    }

    LITHOLOGY_NUMBERS = {
        30000: 0,
        65030: 1,
        65000: 2,
        80000: 3,
        74000: 4,
        70000: 5,
        70032: 6,
        88000: 7,
        86000: 8,
        99000: 9,
        90000: 10,
    }

    LITHOLOGY_KEYS = {
        'Sandstone': 30000,
        'Sandstone/Shale': 65030,
        'Shale': 65000,
        'Marl': 80000,
        'Dolomite': 74000,
        'Limestone': 70000,
        'Chalk': 70032,
        'Halite': 88000,
        'Anhydrite': 86000,
        'Tuff': 99000,
        'Coal': 90000
    }

    FEATURES = [
        'DEPTH_MD',
        'CALI',
        'RSHA',
        'RMED',
        'RDEP',
        'RHOB',
        'GR',
        'DTC',
        'BS',
        'NPHI'
    ]
    exclude_columns = [
        'DEPTH_MD',
        'FORCE_2020_LITHOFACIES_CONFIDENCE',
        'FORCE_2020_LITHOFACIES_LITHOLOGY',
        'X_LOC',
        'Y_LOC',
        'Z_LOC'
    ]