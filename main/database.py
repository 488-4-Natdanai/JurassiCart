"""
database.py  –  CSV-based persistence layer for JurassiCart
Tables (CSV files):
    users.csv       – user accounts
    stores.csv      – one store per user
    dinosaurs.csv   – dinosaur listings per store
    orders.csv      – customer orders
    order_items.csv – line items per order
"""

import csv, os, hashlib, uuid
from datetime import datetime

_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(_DB_DIR, exist_ok=True)

# ── file paths ───────────────────────────────────────────────────────────────
USERS_CSV       = os.path.join(_DB_DIR, "users.csv")
STORES_CSV      = os.path.join(_DB_DIR, "stores.csv")
DINOSAURS_CSV   = os.path.join(_DB_DIR, "dinosaurs.csv")
ORDERS_CSV      = os.path.join(_DB_DIR, "orders.csv")
ORDER_ITEMS_CSV = os.path.join(_DB_DIR, "order_items.csv")
CART_CSV        = os.path.join(_DB_DIR, "cart.csv")

# ── schema definitions ───────────────────────────────────────────────────────
_SCHEMAS = {
    USERS_CSV:       ["user_id", "username", "password_hash", "email", "phone",
                      "name", "gender", "dob", "wallet", "avatar", "created_at"],
    STORES_CSV:      ["store_id", "user_id", "store_name", "description", "created_at"],
    DINOSAURS_CSV:   ["dino_id", "store_id", "name", "gene", "gender", "age",
                      "color", "price", "stock", "image", "description", "created_at"],
    ORDERS_CSV:      ["order_id", "user_id", "status", "total", "shipping_name",
                      "shipping_address", "email", "phone", "created_at", "delivery_days"],
    ORDER_ITEMS_CSV: ["item_id", "order_id", "dino_id", "dino_name", "qty", "unit_price"],
    CART_CSV:        ["cart_id", "user_id", "dino_id", "dino_name", "gene",
                      "color", "price", "qty"],
}

# ── internal helpers ─────────────────────────────────────────────────────────
def _ensure(path: str):
    """Create CSV with header row if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(_SCHEMAS[path])

def _read(path: str) -> list[dict]:
    _ensure(path)
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _write(path: str, rows: list[dict]):
    _ensure(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_SCHEMAS[path])
        w.writeheader()
        w.writerows(rows)

def _append(path: str, row: dict):
    _ensure(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_SCHEMAS[path])
        w.writerow(row)

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _uid() -> str:
    return str(uuid.uuid4())[:8]

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ════════════════════════════════════════════════════════════════════════════
#  USER
# ════════════════════════════════════════════════════════════════════════════

def register_user(username: str, password: str, email: str = "", phone: str = "") -> dict | None:
    """
    Create a new user. Returns the new user dict, or None if username taken.
    """
    users = _read(USERS_CSV)
    if any(u["username"].lower() == username.lower() for u in users):
        return None  # duplicate

    user = {
        "user_id":       _uid(),
        "username":      username,
        "password_hash": _hash(password),
        "email":         email,
        "phone":         phone,
        "name":          "",
        "gender":        "",
        "dob":           "",
        "wallet":        "0",
        "avatar":        "",
        "created_at":    _now(),
    }
    _append(USERS_CSV, user)
    return user


def login_user(username: str, password: str) -> dict | None:
    """Return user dict if credentials match, else None."""
    for u in _read(USERS_CSV):
        if u["username"].lower() == username.lower() and u["password_hash"] == _hash(password):
            return u
    return None


def get_user(user_id: str) -> dict | None:
    """Return user dict by user_id, or None if not found."""
    for u in _read(USERS_CSV):
        if u["user_id"] == user_id:
            return u
    return None


def update_user(user_id: str, **fields) -> bool:
    """Update arbitrary fields for a user. Returns True on success."""
    rows = _read(USERS_CSV)
    updated = False
    for row in rows:
        if row["user_id"] == user_id:
            for k, v in fields.items():
                if k in row:
                    row[k] = v
            updated = True
            break
    if updated:
        _write(USERS_CSV, rows)
    return updated


def add_wallet(user_id: str, amount: int) -> int:
    """Add amount to wallet. Returns new balance."""
    rows = _read(USERS_CSV)
    new_balance = 0
    for row in rows:
        if row["user_id"] == user_id:
            new_balance = int(row["wallet"]) + amount
            row["wallet"] = str(new_balance)
            break
    _write(USERS_CSV, rows)
    return new_balance


def get_wallet(user_id: str) -> int:
    """Return the current wallet balance for a user."""
    u = get_user(user_id)
    return int(u["wallet"]) if u else 0

# ════════════════════════════════════════════════════════════════════════════
#  STORE
# ════════════════════════════════════════════════════════════════════════════

def create_store(user_id: str, store_name: str, description: str = "") -> dict | None:
    """One store per user. Returns None if user already has a store."""
    stores = _read(STORES_CSV)
    if any(s["user_id"] == user_id for s in stores):
        return None
    store = {
        "store_id":    _uid(),
        "user_id":     user_id,
        "store_name":  store_name,
        "description": description,
        "created_at":  _now(),
    }
    _append(STORES_CSV, store)
    return store


def get_store_by_user(user_id: str) -> dict | None:
    """Return the store owned by the given user, or None."""
    for s in _read(STORES_CSV):
        if s["user_id"] == user_id:
            return s
    return None


def get_all_stores() -> list[dict]:
    """Return all stores."""
    return _read(STORES_CSV)

# ════════════════════════════════════════════════════════════════════════════
#  DINOSAUR
# ════════════════════════════════════════════════════════════════════════════

def add_dinosaur(store_id: str, name: str, gene: str, gender: str,
                 age: int, color: str, price: int, stock: int,
                 image: str = "", description: str = "") -> dict:
    """Add a new dinosaur listing to a store and return the created dict."""
    dino = {
        "dino_id":     _uid(),
        "store_id":    store_id,
        "name":        name,
        "gene":        gene,        # Carnivore / Herbivore / Omnivore
        "gender":      gender,      # Male / Female
        "age":         str(age),
        "color":       color,
        "price":       str(price),
        "stock":       str(stock),
        "image":       image,
        "description": description,
        "created_at":  _now(),
    }
    _append(DINOSAURS_CSV, dino)
    return dino


def get_all_dinosaurs() -> list[dict]:
    """Return all dinos with store_name injected."""
    stores = {s["store_id"]: s["store_name"] for s in _read(STORES_CSV)}
    dinos = _read(DINOSAURS_CSV)
    for d in dinos:
        d["store_name"] = stores.get(d["store_id"], "Unknown Store")
    return dinos


def get_dinosaurs_by_store(store_id: str) -> list[dict]:
    """Return all dinosaurs belonging to a specific store."""
    return [d for d in _read(DINOSAURS_CSV) if d["store_id"] == store_id]


def get_dinosaur(dino_id: str) -> dict | None:
    """Return a single dinosaur by ID, or None if not found."""
    for d in _read(DINOSAURS_CSV):
        if d["dino_id"] == dino_id:
            return d
    return None


def update_dinosaur(dino_id: str, **fields) -> bool:
    """Update arbitrary fields on a dinosaur record. Returns True on success."""
    rows = _read(DINOSAURS_CSV)
    updated = False
    for row in rows:
        if row["dino_id"] == dino_id:
            for k, v in fields.items():
                if k in row:
                    row[k] = str(v)
            updated = True
            break
    if updated:
        _write(DINOSAURS_CSV, rows)
    return updated


def delete_dinosaur(dino_id: str) -> bool:
    """Delete a dinosaur by ID. Returns True if a record was removed."""
    rows = _read(DINOSAURS_CSV)
    new_rows = [r for r in rows if r["dino_id"] != dino_id]
    if len(new_rows) < len(rows):
        _write(DINOSAURS_CSV, new_rows)
        return True
    return False


def reduce_stock(dino_id: str, qty: int) -> bool:
    """Reduce stock by qty. Returns False if insufficient stock."""
    rows = _read(DINOSAURS_CSV)
    for row in rows:
        if row["dino_id"] == dino_id:
            current = int(row["stock"])
            if current < qty:
                return False
            row["stock"] = str(current - qty)
            _write(DINOSAURS_CSV, rows)
            return True
    return False


def seed_dinosaurs():
    """Insert 8 sample dinosaurs if DB is empty, spread across 3 fictional stores."""
    _ensure(DINOSAURS_CSV)
    if _read(DINOSAURS_CSV):
        return  # already seeded

    _ensure(STORES_CSV)
    _ensure(USERS_CSV)

    # helper: get-or-create seed user + store
    def _get_or_create_store(username, store_name):
        users = _read(USERS_CSV)
        user_id = None
        for u in users:
            if u["username"] == username:
                user_id = u["user_id"]
                break
        if not user_id:
            u = {"user_id": _uid(), "username": username,
                 "password_hash": _hash("seed1234"), "email": "",
                 "phone": "", "name": "", "gender": "", "dob": "",
                 "wallet": "0", "avatar": "", "created_at": _now()}
            _append(USERS_CSV, u)
            user_id = u["user_id"]
        stores = _read(STORES_CSV)
        for s in stores:
            if s["store_name"] == store_name:
                return s["store_id"]
        s = {"store_id": _uid(), "user_id": user_id,
             "store_name": store_name, "description": "", "created_at": _now()}
        _append(STORES_CSV, s)
        return s["store_id"]

    sid1 = _get_or_create_store("rex_dealer",    "Rex's Predator Shop")
    sid2 = _get_or_create_store("gentle_giants", "Gentle Giants Ranch")
    sid3 = _get_or_create_store("dino_world",    "DinoWorld Emporium")

    samples = [
        (sid1, "Tyrannosaurus Rex",  "Carnivore", "Male",   8,  "#2d7a2d", 25_000_000, 5,
         "The apex predator. Massive jaws, tiny arms, maximum attitude."),
        (sid2, "Triceratops",        "Herbivore", "Female", 12, "#8b6914", 18_000_000, 8,
         "Three-horned gentle giant. Great for garden patrol."),
        (sid1, "Velociraptor",       "Carnivore", "Male",   3,  "#c8a000", 12_000_000, 12,
         "Highly intelligent pack hunter. Requires experienced owner."),
        (sid2, "Brachiosaurus",      "Herbivore", "Female", 20, "#4a7c59", 40_000_000, 3,
         "Tallest dino available. Eats treetops, very calm temperament."),
        (sid3, "Phuwiangosaurus",    "Herbivore", "Male",   15, "#e8e800", 50_000_000, 2,
         "Rare Thai sauropod. Long neck, peaceful, eats 200 kg/day."),
        (sid2, "Ankylosaurus",       "Herbivore", "Female", 10, "#6b8e23", 22_000_000, 6,
         "Living tank with club tail. Nearly indestructible armor."),
        (sid3, "Pteranodon",         "Carnivore", "Male",   5,  "#708090", 15_000_000, 9,
         "Winged reptile. Not technically a dinosaur but we sell it anyway."),
        (sid3, "Spinosaurus",        "Omnivore",  "Female", 11, "#1e6b8a", 35_000_000, 4,
         "Larger than T-Rex, loves water. Semi-aquatic lifestyle."),
    ]

    for sid, name, gene, gender, age, color, price, stock, desc in samples:
        add_dinosaur(store_id=sid, name=name, gene=gene, gender=gender,
                     age=age, color=color, price=price, stock=stock,
                     image="", description=desc)

# ════════════════════════════════════════════════════════════════════════════
#  ORDER
# ════════════════════════════════════════════════════════════════════════════

import random

def create_order(user_id: str, items: list[dict], shipping: dict, deduct_wallet: bool = True) -> dict | None:
    """
    items: [{"dino_id": ..., "dino_name": ..., "qty": ..., "unit_price": ...}, ...]
    shipping: {"name", "address", "email", "phone"}
    Returns order dict or None if wallet insufficient.
    """
    total = sum(int(i.get("unit_price", i.get("price", 0))) * int(i["qty"]) for i in items)

    if deduct_wallet:
        wallet = get_wallet(user_id)
        if wallet < total:
            return None
        add_wallet(user_id, -total)

    delivery_days = random.randint(5, 10)
    order = {
        "order_id":        _uid(),
        "user_id":         user_id,
        "status":          "Processing",
        "total":           str(total),
        "shipping_name":   shipping.get("name", ""),
        "shipping_address":shipping.get("address", ""),
        "email":           shipping.get("email", ""),
        "phone":           shipping.get("phone", ""),
        "created_at":      _now(),
        "delivery_days":   str(delivery_days),
    }
    _append(ORDERS_CSV, order)

    for item in items:
        _append(ORDER_ITEMS_CSV, {
            "item_id":    _uid(),
            "order_id":   order["order_id"],
            "dino_id":    item.get("dino_id", ""),
            "dino_name":  item.get("dino_name", item.get("name", "")),
            "qty":        str(item["qty"]),
            "unit_price": str(item.get("unit_price", item.get("price", 0))),
        })

    # reduce stock
    for item in items:
        reduce_stock(item["dino_id"], int(item["qty"]))

    return order


def get_orders_by_user(user_id: str) -> list[dict]:
    """Return all orders placed by a user."""
    return [o for o in _read(ORDERS_CSV) if o["user_id"] == user_id]


def get_order_items(order_id: str) -> list[dict]:
    """Return all line items for a given order."""
    return [i for i in _read(ORDER_ITEMS_CSV) if i["order_id"] == order_id]


def update_order_status(order_id: str, status: str) -> bool:
    """Update the status field of an order. Returns True on success."""
    rows = _read(ORDERS_CSV)
    for row in rows:
        if row["order_id"] == order_id:
            row["status"] = status
            _write(ORDERS_CSV, rows)
            return True
    return False

# ════════════════════════════════════════════════════════════════════════════
#  CART
# ════════════════════════════════════════════════════════════════════════════

def get_cart(user_id: str) -> list[dict]:
    """Return all cart rows for a user."""
    return [r for r in _read(CART_CSV) if r["user_id"] == user_id]


def add_to_cart(user_id: str, dino: dict) -> dict:
    """
    Add dino to cart or increment qty if already present.
    dino must have: dino_id, name, gene, color, price
    Returns the cart row.
    """
    rows = _read(CART_CSV)
    for row in rows:
        if row["user_id"] == user_id and row["dino_id"] == dino["dino_id"]:
            row["qty"] = str(int(row["qty"]) + 1)
            _write(CART_CSV, rows)
            return row

    new_row = {
        "cart_id":   _uid(),
        "user_id":   user_id,
        "dino_id":   dino["dino_id"],
        "dino_name": dino["name"],
        "gene":      dino.get("gene", ""),
        "color":     dino.get("color", "#888888"),
        "price":     str(dino["price"]),
        "qty":       "1",
    }
    _append(CART_CSV, new_row)
    return new_row


def update_cart_qty(cart_id: str, qty: int) -> bool:
    """Set the quantity of a cart item; removes it if qty <= 0. Returns True on success."""
    rows = _read(CART_CSV)
    for row in rows:
        if row["cart_id"] == cart_id:
            if qty <= 0:
                rows.remove(row)
            else:
                row["qty"] = str(qty)
            _write(CART_CSV, rows)
            return True
    return False


def remove_from_cart(cart_id: str) -> bool:
    """Remove a single item from the cart by cart_id. Returns True if removed."""
    rows = _read(CART_CSV)
    new_rows = [r for r in rows if r["cart_id"] != cart_id]
    if len(new_rows) < len(rows):
        _write(CART_CSV, new_rows)
        return True
    return False


def clear_cart(user_id: str):
    """Remove all cart items for a user (called after order placed)."""
    rows = [r for r in _read(CART_CSV) if r["user_id"] != user_id]
    _write(CART_CSV, rows)
