# seed_data.py
from datetime import date, timedelta

# ============================================
# USERS (10 users: 2 per role)
# ============================================
USERS = [
    # ADMIN (2)
    {
        "username": "admin_jane",
        "email": "jane.admin@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000001",
        "role": "admin",
        "status": "active",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "admin_mike",
        "email": "mike.admin@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000002",
        "role": "admin",
        "status": "active",
        "is_staff": True,
        "is_superuser": True,
    },
    # COORDINATOR (2)
    {
        "username": "coord_sarah",
        "email": "sarah.coord@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000003",
        "role": "coordinator",
        "status": "active",
        "is_staff": True,
    },
    {
        "username": "coord_tom",
        "email": "tom.coord@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000004",
        "role": "coordinator",
        "status": "active",
        "is_staff": True,
    },
    # FIELD_AGENT (6)
    {
        "username": "agent_alice",
        "email": "alice.agent@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000005",
        "role": "field_agent",
        "status": "active",
    },
    {
        "username": "agent_bob",
        "email": "bob.agent@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000006",
        "role": "field_agent",
        "status": "active",
    },
    {
        "username": "agent_carol",
        "email": "carol.agent@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000007",
        "role": "field_agent",
        "status": "active",
    },
    {
        "username": "agent_dan",
        "email": "dan.agent@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000008",
        "role": "field_agent",
        "status": "active",
    },
    {
        "username": "agent_eve",
        "email": "eve.agent@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000009",
        "role": "field_agent",
        "status": "active",
    },
    {
        "username": "agent_frank",
        "email": "frank.agent@farm.com",
        "password": "securepass123",
        "phone_number": "+254700000010",
        "role": "field_agent",
        "status": "inactive",
    },
]

# ============================================
# CROP TYPES (6 crops)
# ============================================
CROP_TYPES = [
    {
        "name": "Maize",
        "description": "Hybrid maize variety, drought-resistant",
        "growth_cycle_days": 120,
    },
    {
        "name": "Wheat",
        "description": "Spring wheat, high protein content",
        "growth_cycle_days": 110,
    },
    {
        "name": "Rice",
        "description": "Paddy rice, lowland variety",
        "growth_cycle_days": 150,
    },
    {
        "name": "Potato",
        "description": "Irish potato, high yield variety",
        "growth_cycle_days": 90,
    },
    {
        "name": "Tomato",
        "description": "Greenhouse variety, indeterminate",
        "growth_cycle_days": 80,
    },
    {
        "name": "Beans",
        "description": "Common beans, bush variety",
        "growth_cycle_days": 75,
    },
]

# ============================================
# FIELDS (10 fields)
# ============================================
FIELDS = [
    {
        "name": "North Ridge A",
        "description": "Northern ridge field, well-drained loam soil, 5 acres",
    },
    {
        "name": "North Ridge B",
        "description": "Northern ridge extension, clay-loam soil, 3 acres",
    },
    {
        "name": "Valley Bottom 1",
        "description": "Valley bottom field, alluvial soil, high moisture, 8 acres",
    },
    {
        "name": "Valley Bottom 2",
        "description": "Valley bottom extension, silt-loam soil, 6 acres",
    },
    {
        "name": "Hill Terrace East",
        "description": "Eastern hill terrace, terraced field, sandy-loam, 4 acres",
    },
    {
        "name": "Hill Terrace West",
        "description": "Western hill terrace, rocky-loam soil, 3.5 acres",
    },
    {
        "name": "Riverbank Plot",
        "description": "Riverbank field, fertile silt, irrigation available, 10 acres",
    },
    {
        "name": "Forest Edge",
        "description": "Forest boundary field, organic-rich soil, partial shade, 7 acres",
    },
    {
        "name": "Central Block C",
        "description": "Central farm block C, black cotton soil, 12 acres",
    },
    {
        "name": "South Pasture",
        "description": "Southern pasture conversion, mixed soil, 9 acres",
    },
]

# ============================================
# CROP SEASONS (max 4 per field, only 1 active)
# ============================================
today = date.today()

CROP_SEASONS = [
    # Field 1: North Ridge A (3 seasons, 1 active)
    {
        "name": "Maize NR-A 2024A",
        "field_index": 0,
        "crop_type_index": 0,  # Maize
        "planting_date": today - timedelta(days=45),
        "expected_harvest_date": today + timedelta(days=75),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Wheat NR-A 2023B",
        "field_index": 0,
        "crop_type_index": 1,  # Wheat
        "planting_date": today - timedelta(days=200),
        "expected_harvest_date": today - timedelta(days=90),
        "actual_harvest_date": today - timedelta(days=92),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Potato NR-A 2023A",
        "field_index": 0,
        "crop_type_index": 3,  # Potato
        "planting_date": today - timedelta(days=350),
        "expected_harvest_date": today - timedelta(days=260),
        "actual_harvest_date": today - timedelta(days=258),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 2: North Ridge B (2 seasons, 1 active)
    {
        "name": "Beans NR-B 2024A",
        "field_index": 1,
        "crop_type_index": 5,  # Beans
        "planting_date": today - timedelta(days=20),
        "expected_harvest_date": today + timedelta(days=55),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Tomato NR-B 2023C",
        "field_index": 1,
        "crop_type_index": 4,  # Tomato
        "planting_date": today - timedelta(days=180),
        "expected_harvest_date": today - timedelta(days=100),
        "actual_harvest_date": today - timedelta(days=98),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 3: Valley Bottom 1 (4 seasons, 1 active)
    {
        "name": "Rice VB-1 2024A",
        "field_index": 2,
        "crop_type_index": 2,  # Rice
        "planting_date": today - timedelta(days=60),
        "expected_harvest_date": today + timedelta(days=90),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Maize VB-1 2023B",
        "field_index": 2,
        "crop_type_index": 0,  # Maize
        "planting_date": today - timedelta(days=250),
        "expected_harvest_date": today - timedelta(days=130),
        "actual_harvest_date": today - timedelta(days=128),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Wheat VB-1 2023A",
        "field_index": 2,
        "crop_type_index": 1,  # Wheat
        "planting_date": today - timedelta(days=400),
        "expected_harvest_date": today - timedelta(days=290),
        "actual_harvest_date": today - timedelta(days=287),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Beans VB-1 2022C",
        "field_index": 2,
        "crop_type_index": 5,  # Beans
        "planting_date": today - timedelta(days=500),
        "expected_harvest_date": today - timedelta(days=425),
        "actual_harvest_date": today - timedelta(days=424),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 4: Valley Bottom 2 (3 seasons, 1 active)
    {
        "name": "Tomato VB-2 2024A",
        "field_index": 3,
        "crop_type_index": 4,  # Tomato
        "planting_date": today - timedelta(days=30),
        "expected_harvest_date": today + timedelta(days=50),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Rice VB-2 2023B",
        "field_index": 3,
        "crop_type_index": 2,  # Rice
        "planting_date": today - timedelta(days=300),
        "expected_harvest_date": today - timedelta(days=150),
        "actual_harvest_date": today - timedelta(days=148),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Potato VB-2 2023A",
        "field_index": 3,
        "crop_type_index": 3,  # Potato
        "planting_date": today - timedelta(days=420),
        "expected_harvest_date": today - timedelta(days=330),
        "actual_harvest_date": today - timedelta(days=328),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 5: Hill Terrace East (2 seasons, 1 active)
    {
        "name": "Potato HT-E 2024A",
        "field_index": 4,
        "crop_type_index": 3,  # Potato
        "planting_date": today - timedelta(days=35),
        "expected_harvest_date": today + timedelta(days=55),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Wheat HT-E 2023B",
        "field_index": 4,
        "crop_type_index": 1,  # Wheat
        "planting_date": today - timedelta(days=190),
        "expected_harvest_date": today - timedelta(days=80),
        "actual_harvest_date": today - timedelta(days=78),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 6: Hill Terrace West (3 seasons, 1 active)
    {
        "name": "Wheat HT-W 2024A",
        "field_index": 5,
        "crop_type_index": 1,  # Wheat
        "planting_date": today - timedelta(days=55),
        "expected_harvest_date": today + timedelta(days=55),
        "status": "at_risk",
        "current_stage": "growing",
    },
    {
        "name": "Beans HT-W 2023C",
        "field_index": 5,
        "crop_type_index": 5,  # Beans
        "planting_date": today - timedelta(days=170),
        "expected_harvest_date": today - timedelta(days=95),
        "actual_harvest_date": today - timedelta(days=94),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Maize HT-W 2023A",
        "field_index": 5,
        "crop_type_index": 0,  # Maize
        "planting_date": today - timedelta(days=320),
        "expected_harvest_date": today - timedelta(days=200),
        "actual_harvest_date": today - timedelta(days=198),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 7: Riverbank Plot (4 seasons, 1 active)
    {
        "name": "Rice RBP 2024A",
        "field_index": 6,
        "crop_type_index": 2,  # Rice
        "planting_date": today - timedelta(days=70),
        "expected_harvest_date": today + timedelta(days=80),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Maize RBP 2023B",
        "field_index": 6,
        "crop_type_index": 0,  # Maize
        "planting_date": today - timedelta(days=230),
        "expected_harvest_date": today - timedelta(days=110),
        "actual_harvest_date": today - timedelta(days=107),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Potato RBP 2023A",
        "field_index": 6,
        "crop_type_index": 3,  # Potato
        "planting_date": today - timedelta(days=350),
        "expected_harvest_date": today - timedelta(days=260),
        "actual_harvest_date": today - timedelta(days=258),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Tomato RBP 2022C",
        "field_index": 6,
        "crop_type_index": 4,  # Tomato
        "planting_date": today - timedelta(days=480),
        "expected_harvest_date": today - timedelta(days=400),
        "actual_harvest_date": today - timedelta(days=398),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 8: Forest Edge (2 seasons, 1 active)
    {
        "name": "Beans FE 2024A",
        "field_index": 7,
        "crop_type_index": 5,  # Beans
        "planting_date": today - timedelta(days=25),
        "expected_harvest_date": today + timedelta(days=50),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Rice FE 2023B",
        "field_index": 7,
        "crop_type_index": 2,  # Rice
        "planting_date": today - timedelta(days=220),
        "expected_harvest_date": today - timedelta(days=70),
        "actual_harvest_date": today - timedelta(days=68),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 9: Central Block C (3 seasons, 1 active)
    {
        "name": "Maize CBC 2024A",
        "field_index": 8,
        "crop_type_index": 0,  # Maize
        "planting_date": today - timedelta(days=50),
        "expected_harvest_date": today + timedelta(days=70),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Potato CBC 2023C",
        "field_index": 8,
        "crop_type_index": 3,  # Potato
        "planting_date": today - timedelta(days=160),
        "expected_harvest_date": today - timedelta(days=70),
        "actual_harvest_date": today - timedelta(days=69),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    {
        "name": "Wheat CBC 2023A",
        "field_index": 8,
        "crop_type_index": 1,  # Wheat
        "planting_date": today - timedelta(days=310),
        "expected_harvest_date": today - timedelta(days=200),
        "actual_harvest_date": today - timedelta(days=198),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
    # Field 10: South Pasture (2 seasons, 1 active)
    {
        "name": "Tomato SP 2024A",
        "field_index": 9,
        "crop_type_index": 4,  # Tomato
        "planting_date": today - timedelta(days=40),
        "expected_harvest_date": today + timedelta(days=40),
        "status": "active",
        "current_stage": "growing",
    },
    {
        "name": "Beans SP 2023B",
        "field_index": 9,
        "crop_type_index": 5,  # Beans
        "planting_date": today - timedelta(days=150),
        "expected_harvest_date": today - timedelta(days=75),
        "actual_harvest_date": today - timedelta(days=74),
        "status": "completed",
        "current_stage": "harvested",
        "active": False,
    },
]

# ============================================
# FIELD ASSIGNMENTS (agents assigned to fields)
# ============================================
# Agent indices: 4=alice, 5=bob, 6=carol, 7=dan, 8=eve, 9=frank
# Admin indices: 0=jane, 1=mike
FIELD_ASSIGNMENTS = [
    # Alice (agent 4) -> North Ridge A, Valley Bottom 1, Hill Terrace East
    {"field_index": 0, "agent_index": 4, "assigned_by_index": 0},
    {"field_index": 2, "agent_index": 4, "assigned_by_index": 0},
    {"field_index": 4, "agent_index": 4, "assigned_by_index": 0},
    # Bob (agent 5) -> North Ridge B, Riverbank Plot
    {"field_index": 1, "agent_index": 5, "assigned_by_index": 1},
    {"field_index": 6, "agent_index": 5, "assigned_by_index": 1},
    # Carol (agent 6) -> Valley Bottom 2, Forest Edge
    {"field_index": 3, "agent_index": 6, "assigned_by_index": 0},
    {"field_index": 7, "agent_index": 6, "assigned_by_index": 0},
    # Dan (agent 7) -> Hill Terrace West, Central Block C
    {"field_index": 5, "agent_index": 7, "assigned_by_index": 1},
    {"field_index": 8, "agent_index": 7, "assigned_by_index": 1},
    # Eve (agent 8) -> South Pasture
    {"field_index": 9, "agent_index": 8, "assigned_by_index": 0},
    # Frank (agent 9, inactive) -> no assignments
]

# ============================================
# FIELD UPDATES (season progress updates)
# ============================================
# For each ACTIVE season, provide staged updates
FIELD_UPDATES = [
    # Maize NR-A 2024A (season 0) - Alice logged
    {
        "crop_season_index": 0,
        "agent_index": 4,
        "stage": "planted",
        "notes": "Planted hybrid maize seeds, 5 acres. Soil moisture good. Applied DAP fertilizer at planting.",
        "days_ago": 40,
    },
    {
        "crop_season_index": 0,
        "agent_index": 4,
        "stage": "growing",
        "notes": "Germination rate ~95%. Plants at 4-leaf stage. No pest issues observed. Light weeding done.",
        "days_ago": 20,
    },
    # Beans NR-B 2024A (season 3) - Bob logged
    {
        "crop_season_index": 3,
        "agent_index": 5,
        "stage": "planted",
        "notes": "Planted bush beans variety. Row spacing 45cm. Inoculated seeds before planting.",
        "days_ago": 18,
    },
    {
        "crop_season_index": 3,
        "agent_index": 5,
        "stage": "growing",
        "notes": "Seedlings emerged uniformly. First trifoliate leaves visible. Minor aphid infestation on edges - treated with neem oil.",
        "days_ago": 8,
    },
    # Rice VB-1 2024A (season 5) - Alice logged
    {
        "crop_season_index": 5,
        "agent_index": 4,
        "stage": "planted",
        "notes": "Transplanted rice seedlings from nursery. Water level maintained at 5cm. Applied basal fertilizer.",
        "days_ago": 55,
    },
    {
        "crop_season_index": 5,
        "agent_index": 4,
        "stage": "growing",
        "notes": "Tillering stage progressing well. 15-20 tillers per hill. Water level increased to 10cm. Top dressing applied.",
        "days_ago": 30,
    },
    # Tomato VB-2 2024A (season 9) - Carol logged
    {
        "crop_season_index": 9,
        "agent_index": 6,
        "stage": "planted",
        "notes": "Transplanted tomato seedlings. Installed drip irrigation. Mulching applied. Staking done.",
        "days_ago": 28,
    },
    {
        "crop_season_index": 9,
        "agent_index": 6,
        "stage": "growing",
        "notes": "Plants 45cm tall. First flower clusters visible. Weekly fertigation schedule maintained. Pruned lower suckers.",
        "days_ago": 12,
    },
    # Potato HT-E 2024A (season 11) - Alice logged
    {
        "crop_season_index": 11,
        "agent_index": 4,
        "stage": "planted",
        "notes": "Planted certified seed potatoes. Ridges prepared. Well-rotted manure incorporated.",
        "days_ago": 32,
    },
    {
        "crop_season_index": 11,
        "agent_index": 4,
        "stage": "growing",
        "notes": "Full canopy achieved. Tubers initiating. Earth-up done. Late blight preventive spray applied.",
        "days_ago": 15,
    },
    # Wheat HT-W 2024A (season 12, at_risk) - Dan logged
    {
        "crop_season_index": 12,
        "agent_index": 7,
        "stage": "planted",
        "notes": "Drilled wheat seeds. Pre-emergence herbicide applied. Soil moisture adequate.",
        "days_ago": 50,
    },
    {
        "crop_season_index": 12,
        "agent_index": 7,
        "stage": "growing",
        "notes": "Stem elongation stage. Yellow rust spotted on lower leaves - fungicide applied. Monitoring closely.",
        "days_ago": 25,
    },
    # Rice RBP 2024A (season 14) - Bob logged
    {
        "crop_season_index": 14,
        "agent_index": 5,
        "stage": "planted",
        "notes": "Direct-seeded rice. Pre-germinated seeds used. Field leveled properly.",
        "days_ago": 65,
    },
    {
        "crop_season_index": 14,
        "agent_index": 5,
        "stage": "growing",
        "notes": "Panicle initiation stage. Water management critical now. Applied potash fertilizer. Stem borer traps installed.",
        "days_ago": 35,
    },
    # Beans FE 2024A (season 18) - Carol logged
    {
        "crop_season_index": 18,
        "agent_index": 6,
        "stage": "planted",
        "notes": "Planted beans in forest edge field. Partial shade management. Organic compost applied.",
        "days_ago": 22,
    },
    {
        "crop_season_index": 18,
        "agent_index": 6,
        "stage": "growing",
        "notes": "Vegetative growth stage. Leaf miners observed - threshold not reached. Beneficial insects present.",
        "days_ago": 10,
    },
    # Maize CBC 2024A (season 19) - Dan logged
    {
        "crop_season_index": 19,
        "agent_index": 7,
        "stage": "planted",
        "notes": "Planted maize in central block. Precision planting at 75cm x 25cm. NPK fertilizer applied.",
        "days_ago": 45,
    },
    {
        "crop_season_index": 19,
        "agent_index": 7,
        "stage": "growing",
        "notes": "Knee-high stage. Top dressing with CAN fertilizer done. Fall armyworm scouting - negative.",
        "days_ago": 22,
    },
    # Tomato SP 2024A (season 21) - Eve logged
    {
        "crop_season_index": 21,
        "agent_index": 8,
        "stage": "planted",
        "notes": "Planted determinate tomato variety in south pasture. Drip lines installed. Plastic mulch laid.",
        "days_ago": 35,
    },
    {
        "crop_season_index": 21,
        "agent_index": 8,
        "stage": "growing",
        "notes": "Fruit setting stage. Whitefly population increasing - yellow sticky traps deployed. Calcium nitrate applied for blossom end rot prevention.",
        "days_ago": 14,
    },
]

# ============================================
# HELPER: Resolve indexes to actual references after creation
# ============================================
def resolve_seed_data(created_users, created_crop_types, created_fields, created_seasons):
    """Return resolved assignments and updates with actual object references.

    Use this after creating all objects to map indexes to real instances.
    """
    resolved_assignments = []
    for assignment in FIELD_ASSIGNMENTS:
        resolved_assignments.append({
            "field": created_fields[assignment["field_index"]],
            "agent": created_users[assignment["agent_index"]],
            "assigned_by": created_users[assignment["assigned_by_index"]],
        })

    resolved_updates = []
    for update in FIELD_UPDATES:
        resolved_updates.append({
            "crop_season": created_seasons[update["crop_season_index"]],
            "agent": created_users[update["agent_index"]],
            "stage": update["stage"],
            "notes": update["notes"],
            "created_at_override": today - timedelta(days=update["days_ago"]),
        })

    return resolved_assignments, resolved_updates
