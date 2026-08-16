PRAGMA foreign_keys = ON;

CREATE INDEX idx_orders_status_date ON orders(status, placed_at);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_returns_order_status ON returns(order_id, status);
CREATE INDEX idx_return_items_item ON return_items(order_item_id);

